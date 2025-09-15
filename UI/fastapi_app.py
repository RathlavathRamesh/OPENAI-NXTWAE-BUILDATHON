import os
from typing import List, Optional, Tuple
import psycopg2, json, uuid
PG_DSN = os.getenv("PG_DSN")  # e.g., postgres://user:pass@host:5432/db

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from utils.db_connect import connect_to_postgres
# Import your existing modules (absolute package imports)
from input_preprocessing.router import preprocess_request
from ai_core.multimodel_inference_gateway import multimodal_infer_gemini
from ai_core.weather_reports import get_weather_by_coords
from ai_core.incident_judge import judge_incident_with_gemini
from utils.db_operations import update_incident_summary , create_incident_and_get_id

from utils.send_email import send_email_notification
app = FastAPI(title="Disaster Smart API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models (Pydantic)
class AnalyzeResponse(BaseModel):
    incident_id: str
    incident_request: dict
    realworld_context: dict
    priority_score_0_10: int
    real_incident: bool

# Helpers
def _to_uploads(files: List[UploadFile]) -> List[Tuple[str, bytes, str]]:
    uploads = []
    for f in files or []:
        try:
            content = f.file.read()
        finally:
            f.file.close()
        uploads.append((f.filename or "upload.bin", content, f.content_type or ""))
    return uploads


def _compute_priority(severity: str, verdict: int) -> int:
    s = (severity or "").lower()
    base = 10 if s == "critical" else 8 if s == "high" else 5 if s in ("moderate","medium") else 3 if s == "low" else 4
    bonus = 2 if verdict >= 8 else 1 if verdict >= 5 else 0
    return min(10, base + bonus)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    channel: str = Form("app"),
    username: str = Form(None),                # NEW: may be None -> fallback name used in helper
    text: str = Form(""),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    files: List[UploadFile] = File(default=[]),
):
    try:
        # A) Create minimal incident row upfront and get its ID
        incident_id = create_incident_and_get_id(username, lat, lon)
        # 1) Preprocess into incident (unchanged)
        uploads = _to_uploads(files)
        latlon_str = f"{lat},{lon}" if lat is not None and lon is not None else ""
        incident = preprocess_request(channel, text, latlon_str, uploads)

        # 2) Multimodal inference (Gemini) -> situation JSON (unchanged name kept as 'incident_request' per your code)
        incident_request = multimodal_infer_gemini(incident)

        # 3) Real-world context (unchanged)
        realworld_context = get_weather_by_coords(lat, lon)

        # 5) LLM-as-a-Judge gating (unchanged)
        judge = judge_incident_with_gemini(incident_request, realworld_context)

        # 6) Priority after gating (unchanged)
        if not judge.get("real_incident", False):
            priority = 0
        else:
            sev = (judge.get("final_severity"))
            priority = _compute_priority(sev, int(judge.get("verdict_score_0_10", 0)))

        # B) Update only incident_summary at the end
        summary = {
            "incident_request": incident_request,
            "realworld_context": realworld_context,
            "judge": judge,
            "priority_score_0_10": priority
        }
        update_incident_summary(incident_id, summary)

        # C) Return including the incident_id for later dispatch
        return AnalyzeResponse(
            incident_id=str(incident_id),
            incident_request=incident_request,
            realworld_context=realworld_context,
            priority_score_0_10=priority,
            real_incident=bool(True),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DispatchIn(BaseModel):
    incident_id: str

def _haversine_km(a_lat, a_lon, b_lat, b_lon):
    import math
    R=6371.0
    dlat=math.radians(b_lat-a_lat); dlon=math.radians(b_lon-a_lon)
    la1=math.radians(a_lat); la2=math.radians(b_lat)
    h=math.sin(dlat/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(h))

@app.post("/dispatch")
async def dispatch_api(body: DispatchIn):
    conn=connect_to_postgres()
    try:
        with conn.cursor() as cur:
            # Fetch incident
            cur.execute("""SELECT id, lat, lon, status FROM incidents WHERE id=%s""", (body.incident_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "incident not found")
            inc = {"id": row, "lat": float(row[2]), "lon": float(row[1]), "status": row[3]}
            if inc["status"] != "verified":
                raise HTTPException(409, "incident not verified")

            # Prevent duplicates within 10 minutes
            cur.execute("""
                SELECT id, state FROM dispatch_jobs
                WHERE incident_id=%s AND enqueued_at > NOW() - INTERVAL '10 minutes'
                ORDER BY enqueued_at DESC LIMIT 1
            """, (inc["id"],))
            existing = cur.fetchone()
            if existing and existing[2] in ("queued","allocating","assigned"):
                return {"job_id": str(existing), "state": existing[2], "message": "dispatch already requested recently"}

            # Create job
            job_id = uuid.uuid4()
            cur.execute("""INSERT INTO dispatch_jobs (id, incident_id, state, priority, enqueued_at)
                           VALUES (%s,%s,'queued',50,NOW())""", (job_id, inc["id"]))
            conn.commit()

            # Allocating
            cur.execute("""UPDATE dispatch_jobs SET state='allocating', started_at=NOW() WHERE id=%s""", (job_id,))
            conn.commit()

            # Fetch teams
            cur.execute("""
                SELECT id, name, lat, lon, contact_email, contact_phone, capacity, load, available
                FROM teams
                WHERE available = TRUE AND (load < capacity)
            """)
            teams = cur.fetchall()
            if not teams:
                cur.execute("""UPDATE dispatch_jobs SET state='failed', finished_at=NOW(), last_error='no team available' WHERE id=%s""", (job_id,))
                conn.commit()
                return {"job_id": str(job_id), "state": "failed", "message": "No team available now."}

            # Choose nearest
            best = None
            for t in teams:
                tinfo = {"id": t, "name": t[2], "lat": float(t[1]), "lon": float(t[3]),
                         "email": t[4], "phone": t[5], "capacity": int(t[6]), "load": int(t[7])}
                dist = _haversine_km(inc["lat"], inc["lon"], tinfo["lat"], tinfo["lon"])
                eta = max(5, int(dist/0.6))
                if (best is None) or (eta < best["eta"]):
                    best = {"team": tinfo, "eta": eta, "dist": dist}

            # Notify (MVP: print)
            print(f"[NOTIFY] Team {best['team']['name']} -> Incident {inc['id']} ({inc['lat']},{inc['lon']}) ETA~{best['eta']}m")

            # Optional: bump load by 1 for demo realism
            cur.execute("""UPDATE teams SET load = LEAST(capacity, load+1) WHERE id=%s""", (best["team"]["id"],))

            # Mark assigned and reflect incident state
            cur.execute("""UPDATE dispatch_jobs SET state='assigned', finished_at=NOW() WHERE id=%s""", (job_id,))
            cur.execute("""UPDATE incidents SET allocation_status='assigned' WHERE id=%s""", (inc["id"],))
            conn.commit()

            return {
                "job_id": str(job_id),
                "state": "assigned",
                "assigned_to": {
                    "team_id": str(best["team"]["id"]),
                    "team_name": best["team"]["name"],
                    "contact_phone": best["team"]["phone"],
                    "contact_email": best["team"]["email"]
                },
                "eta_min": best["eta"],
                "message": f"{best['team']['name']} is on the way. Please follow safety guidance until they arrive."
            }
    finally:
        conn.close()



from pydantic import BaseModel
import uuid, json, os, smtplib
from email.mime.text import MIMEText

class RequestResourceIn(BaseModel):
    incident_id: int

def _build_email_body(incident_id:int, summary:dict, team_name:str) -> str:
    ir = summary.get("incident_request", {})
    ctx = summary.get("realworld_context", {})
    judge = summary.get("judge", {})
    priority = summary.get("priority_score_0_10")

    lines = []
    lines.append(f"Assignment: Incident #{incident_id} → {team_name}")
    lines.append("")
    lines.append("Situation Summary:")
    lines.append(ir.get("situation_summary", "N/A"))
    lines.append("")
    hz = ir.get("hazards") or []
    if hz:
        lines.append("Hazards:")
        for h in hz:
            lines.append(f"- {h.get('type','?')} | severity={h.get('severity','?')} | {h.get('details','')}")
        lines.append("")
    pa = ir.get("people_affected") or {}
    lines.append(f"People affected: est={pa.get('visible_count_estimate','?')} injuries_visible={pa.get('injuries_visible','?')}")
    infra = ir.get("infrastructure") or {}
    if infra.get("blocked_roads"):
        lines.append(f"Blocked roads: {', '.join(infra['blocked_roads'])}")
    lines.append("")
    if ctx:
        lines.append("Real-world context:")
        lines.append(f"- location: {ctx.get('location')}")
        lines.append(f"- weather: {ctx.get('description')} | temp_C: {ctx.get('temperature_C')} | humidity%: {ctx.get('humidity_percent')}")
        lines.append("")
    lines.append(f"Verdict: real_incident={judge.get('real_incident')} score(0-10)={judge.get('verdict_score_0_10')} final_severity={judge.get('final_severity')}")
    lines.append(f"Priority (0-10): {priority}")
    lines.append("")
    latlon = ir.get("location_hint") or f"{ir.get('lat')},{ir.get('lon')}"
    lines.append(f"Navigate to: {latlon}")
    lines.append("")
    lines.append("Please acknowledge and proceed ASAP.")
    return "\n".join(lines)

def _send_email_smtp(to_email:str, subject:str, body:str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL", smtp_user or "noreply@example.org")

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        if smtp_user and smtp_pass:
            s.login(smtp_user, smtp_pass)
        s.sendmail(from_email, [to_email], msg.as_string())

@app.post("/request_resource")
async def request_resource(body: RequestResourceIn):
    conn = connect_to_postgres()
    try:
        with conn.cursor() as cur:
            # 1) Load incident summary
            cur.execute("""
                SELECT incident_id, incident_summary
                FROM incident
                WHERE incident_id=%s
            """, (body.incident_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "incident not found")
            incident_id = int(row[0])
            summary = row[1]
            if isinstance(summary, str):
                summary = json.loads(summary or "{}")

            # 2) Fetch fixed rescue_team user_id=6
            cur.execute("""
                SELECT rescue_team_id, rescue_team_user_name, email_id, phone, location
                FROM rescue_team
                WHERE rescue_team_id=%s AND active_flag='Y'
            """, (6,))
            t = cur.fetchone()
            if not t:
                raise HTTPException(404, "rescue team (id=6) not found or inactive")
            team = {
                "id": t[0],
                "name": t[1],
                "email": t[2],
                "phone": t[3],
                "location": t[4],
            }
            if not team["email"]:
                raise HTTPException(409, "rescue team email_id missing; cannot send email")

            # 3) Write dispatch job (audit) and mark team allocated
            job_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO dispatch_jobs (id, incident_id, state, priority, enqueued_at, started_at, finished_at)
                VALUES (%s, %s, 'assigned', 50, NOW(), NOW(), NOW())
            """, (job_id, str(incident_id)))
            cur.execute("""
                UPDATE rescue_team
                SET is_allocated='Y', updated_date=NOW()
                WHERE rescue_team_id=%s
            """, (team["id"],))
            conn.commit()

        # 4) Email the details
        subject = f"[Rescue Dispatch] Incident #{incident_id} assigned to {team['name']}"
        body_txt = _build_email_body(incident_id, summary, team["name"])
        send_email_notification(subject=subject,body=body_txt,to_mail=team["email"])
        

        # 5) Respond to UI
        return {
            "job_id": job_id,
            "status": "assigned",
            "assigned_to": {
                "team_id": str(team["id"]),
                "team_name": team["name"],
                "contact_phone": team["phone"],
                "contact_email": team["email"]
            },
            "message": "Rescue team member will reach out ASAP."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        conn.close()
