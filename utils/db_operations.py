# top of the same FastAPI file
import json, uuid, datetime as dt
from utils.db_connect import connect_to_postgres  # your helper that returns a psycopg2 connection


def create_incident_and_get_id(username, lat, lon):
    victim_name = (username or "").strip() or "Anonymous Reporter"
    loc = json.dumps({"lat": lat, "lon": lon})

    conn = connect_to_postgres()
    try:
        with conn.cursor() as cur:
            # Prevent two writers from choosing the same id
            cur.execute("LOCK TABLE incident IN SHARE ROW EXCLUSIVE MODE")

            # Start from max(id)+1
            cur.execute("SELECT COALESCE(MAX(incident_id), 0) + 1 FROM incident")
            next_id = cur.fetchone()[0]

            # Probe upward until a free id is inserted successfully
            while True:
                cur.execute("""
                    INSERT INTO incident (
                        incident_id, victim_user_name, location, created_by, created_date, active_flag
                    ) VALUES (
                        %s, %s, %s::jsonb, %s, NOW(), 'Y'
                    )
                    ON CONFLICT (incident_id) DO NOTHING
                    RETURNING incident_id
                """, (next_id, victim_name, loc, None))
                row = cur.fetchone()
                if row:
                    conn.commit()
                    return row[0]
                next_id += 1  # try next free id
    finally:
        conn.close()

def update_incident_summary(incident_id: int, summary_dict: dict) -> None:
    conn = connect_to_postgres()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE incident
                SET incident_summary = %s::jsonb,
                    updated_date     = NOW()
                WHERE incident_id   = %s
            """, (
                json.dumps(summary_dict),
                incident_id
            ))
            conn.commit()
    finally:
        conn.close()
        
        
        



