from flask import Flask, request, Response
import time 
import json 
import psycopg2
from environment import Config
from google import genai
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

#Route to provide the response for a given prompt using OpenAI GPT-5 (For now we are using Gemini)
@app.route('/api/generate-response', methods=['POST'])
def generate_response():
    #Fetch the input payload from the request
    input_data = request.get_json()
    if input_data is None or 'prompt' not in input_data:
        response = {
            "execution_status": "Failed",
            "status_code": 400,
            "message": "Invalid input: 'prompt' key is missing",
            "error_code": "INVALID_INPUT",
            "error_message": "'prompt' key is required in the request body",
            "output_kpis": {
                "execution_time": 0
            }
        }
        return Response(json.dumps(response), status=400, mimetype='application/json')
    #Record the start time for execution time calculation
    start_time = time.time()
    try:
        #Get the prompt and other details from the input data
        prompt = input_data['prompt']
        section_id = int(input_data.get('section_id'))
        section_name = input_data.get('section_name')
        user_id = int(input_data.get('user_id'))
        #Access the DB connection string and schema from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        #Create the connection to the database
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Prepare a query to insert the prompt details into the database
        insert_query = f"""
                            INSERT INTO {DB_SCHEMA}.PROMPT_RESPONSES
                            (PROMPT, SECTION_ID, SECTION_NAME, PROMPT_GIVEN_AT, USER_ID, CREATED_BY)
                            VALUES (%s, %s, %s, NOW(), %s, %s)
                            RETURNING PROMPT_RESPONSE_ID;
                        """
        cursor.execute(insert_query, (prompt, section_id, section_name, user_id, user_id))
        prompt_response_id = cursor.fetchone()[0]
        conn.commit()
        #Get the Gemini API key from config
        GOOGLE_API_KEY = Config.GOOGLE_API_KEY
        #Create the genai client
        client = genai.Client(api_key=GOOGLE_API_KEY)
        #Generate the response using Gemini API 
        model_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        response_text = model_response.text
        #Update the record with response and response time 
        update_query = f"""
                            UPDATE {DB_SCHEMA}.PROMPT_RESPONSES
                            SET 
                                RESPONSE = %s, 
                                RESPONSE_PROVIDED_AT = NOW(),
                                UPDATED_BY = %s,
                                UPDATED_DATE = NOW()
                            WHERE PROMPT_RESPONSE_ID = %s;
                        """
        cursor.execute(update_query, (json.dumps({"response": response_text}), user_id, prompt_response_id))
        conn.commit()
        #Close the cursor and connection
        cursor.close()
        conn.close()
        response = {
            "execution_status": "Success",  
            "status_code": 200,
            "message": "Response generated successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            },
            "body": {
                "response": response_text
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')        
    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error generating response",
            "error_code": "GENAI_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')
        
        
#Route to fetch all incidents
@app.route('/api/allincidents',methods=['GET'])
def fetch_all_incidents():
    start_time = time.time()
    try:
        #Get the connection_string and schema from config 
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING  
        DB_SCHEMA = Config.DB_SCHEMA
        #Establishing the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to fetch All Incidents
        query = f"""
                    SELECT 
                        INCIDENT_ID, 
                        INCIDENT_NAME, 
                        LOCATION ->> 'place', 
                        SEVERITY_LEVEL,
                        CAST(ROUND(EXTRACT(EPOCH FROM (NOW() - A.CREATED_DATE)) / 60,2) AS FLOAT) AS ELAPSED_TIME_MINS,
                        A.INCIDENT_STATUS AS STATUS,
                        A.EMERGENCY_SCORE AS AI_SCORE,
                        A.PERSONNEL AS PERSONNEL,
                        A.DESCRIPTION AS INCIDENT_DESCRIPTION,
                        A.PRIORITY AS INCIDENT_PRIORITY,
                        A.RISK_FACTORS AS RISK_FACTORS,
                        D.USER_NAME AS REPORTED_BY
                    FROM 
                        {DB_SCHEMA}.INCIDENTS A
                        JOIN 
                        {DB_SCHEMA}.SEVERITY_LEVELS B 
                        ON A.SEVERITY_LEVEL_ID = B.SEVERITY_LEVEL_ID
                        AND 
                        A.ACTIVE_FLAG = 'Y'
                        AND
                        B.ACTIVE_FLAG = 'Y'
                        JOIN 
                        {DB_SCHEMA}.INCIDENT_TYPES C
                        ON A.INCIDENT_TYPE_ID = C.INCIDENT_TYPE_ID
                        AND
                        C.ACTIVE_FLAG = 'Y'
                        JOIN 
                        USERS_INFORMATION D
                        ON A.USER_ID = D.USER_ID
                        AND 
                        D.ACTIVE_FLAG = 'Y'
                    ORDER BY 
                        A.CREATED_DATE DESC;
                """
        cursor.execute(query)
        #Fetch all recent incidents
        incidents = cursor.fetchall()  
        #If no recent incidents found, return appropriate response
        if not incidents:
            response = {
                "execution_status": "Failed",
                "status_code": 404,
                "message": "No Recent Incidents found",
                "error_code": "NO_DATA",
                "error_message": "The INCIDENTS table is empty or no active incidents found",
                "output_kpis": {
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')
        #Prepare the incidents list
        incidents_list = []
        for row in incidents:
            incident = {
                "incident_id": row[0],
                "incident_name": row[1],
                "location": row[2],
                "severity_level": row[3],
                "time": row[4],
                "status": row[5],
                "ai_score": row[6], 
                "personnel": row[7],
                "description": row[8],
                "priority": row[9],
                "risk_factors": row[10],
                "reported_by": row[11]
            }
            incidents_list.append(incident)
        #Close the cursor and connection
        cursor.close()  
        conn.close()
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Incidents fetched successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            },
            "body": {
                "incidents": incidents_list
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')
    except Exception as e:  
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error fetching Recent Incidents",
            "error_code": "CONFIG_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')


# Route to fetch recent incidents in Dashboards page
@app.route('/api/recentincidents',methods=['GET'])
def fetch_recent_incidents():
    start_time = time.time()
    try:
        #Get the connection_string and schema from config 
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING  
        DB_SCHEMA = Config.DB_SCHEMA
        #Establishing the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to fetch recent incidents
        query = f"""
                    SELECT 
                        INCIDENT_ID, 
                        INCIDENT_NAME, 
                        LOCATION ->> 'place', 
                        SEVERITY_LEVEL,
                        CAST(ROUND(EXTRACT(EPOCH FROM (NOW() - A.CREATED_DATE)) / 60,2) AS FLOAT) AS ELAPSED_TIME_MINS
                    FROM 
                        {DB_SCHEMA}.INCIDENTS A
                        JOIN 
                        {DB_SCHEMA}.SEVERITY_LEVELS B 
                        ON A.SEVERITY_LEVEL_ID = B.SEVERITY_LEVEL_ID
                        AND 
                        A.ACTIVE_FLAG = 'Y'
                        AND
                        B.ACTIVE_FLAG = 'Y'
                        JOIN 
                        {DB_SCHEMA}.INCIDENT_TYPES C
                        ON A.INCIDENT_TYPE_ID = C.INCIDENT_TYPE_ID
                        AND
                        C.ACTIVE_FLAG = 'Y'
                    ORDER BY 
                        A.CREATED_DATE DESC 
                    LIMIT 5;
                """
        cursor.execute(query)
        #Fetch all recent incidents
        recent_incidents = cursor.fetchall()  
        #If no recent incidents found, return appropriate response
        if not recent_incidents:
            response = {
                "execution_status": "Failed",
                "status_code": 404,
                "message": "No Recent Incidents found",
                "error_code": "NO_DATA",
                "error_message": "The INCIDENTS table is empty or no active incidents found",
                "output_kpis": {
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')
        #Prepare the recent incidents list
        recent_incidents_list = []
        for row in recent_incidents:
            incident = {
                "incident_id": row[0],
                "incident_name": row[1],
                "location": row[2],
                "severity_level": row[3],
                "elapsed_time": row[4]
            }
            recent_incidents_list.append(incident)
        #Close the cursor and connection
        cursor.close()  
        conn.close()
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Recent Incidents fetched successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            },
            "body": {
                "recent_incidents": recent_incidents_list
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')
    except Exception as e:  
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error fetching Recent Incidents",
            "error_code": "CONFIG_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')

# Route to fetch dashboard report
@app.route('/api/dashboardreport', methods=['GET'])
def fetch_dashboard_report():
    start_time = time.time()
    try:
        #Get the connection_string and schema from config 
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING  
        DB_SCHEMA = Config.DB_SCHEMA
        #Establishing the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to fetch dashboard report
        query_for_incidents = f"""
                    SELECT 
                        COUNT(*) AS ACTIVE_INCIDENTS ,
                        CAST(AVG(EXTRACT(EPOCH FROM (UPDATED_DATE - CREATED_DATE)) / 60) AS FLOAT) AS AVG_RESPONSE_TIME_MINS,
                        SUM(PERSONNEL) AS TOTAL_PEOPLE_ASSISTED 
                    FROM {DB_SCHEMA}.INCIDENTS 
                    WHERE 
                        LOWER(INCIDENT_STATUS) IN ('active','sumitted','responding')
                        AND 
                        ACTIVE_FLAG = 'Y';
                """
        cursor.execute(query_for_incidents)
        #Fetch incident related reports
        active_incidents = cursor.fetchone()
        #If no active incidents found, return appropriate response
        if not active_incidents:
            response = {
                "execution_status": "Failed",       
                "status_code": 404,
                "message": "No Active Incidents found",
                "error_code": "NO_DATA",
                "error_message": "No active incidents found in the INCIDENTS table",
                "output_kpis": {
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')
        #Query to fetch Active Response Teams 
        query_for_response_teams = """
                                    SELECT
                                        COUNT(*) AS ACTIVE_RESPONSE_TEAMS
                                    FROM 
                                        RESCUE_TEAMS_INFO 
                                    WHERE 
                                        ACTIVE_FLAG = 'Y';"""
        cursor.execute(query_for_response_teams)
        #Get the count of active response teams
        active_response_teams = cursor.fetchone()
        #Close the cursor and connection
        cursor.close()  
        conn.close()
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Dashboard Report fetched successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }, 
            "body": {
                "active_incidents": active_incidents[0],
                "response_teams": active_response_teams[0],
                "people_assisted": active_incidents[2],
                "avg_response": round(active_incidents[1],2)
            }   
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')
    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error fetching Dashboard Reports",
            "error_code": "CONFIG_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')

#Route to fetch severity levels
@app.route('/api/severitylevels', methods=['GET'])
def fetch_severity_levels():
    start_time = time.time()
    try:
        #Get the connection_string and schema from config 
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING  
        DB_SCHEMA = Config.DB_SCHEMA
        #Establishing the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to fetch severity levels
        query = f"SELECT SEVERITY_LEVEL_ID,SEVERITY_LEVEL  FROM {DB_SCHEMA}.SEVERITY_LEVELS WHERE ACTIVE_FLAG = 'Y';"
        cursor.execute(query)
        #Fetch all severity levels
        severity_levels = cursor.fetchall()  
        #If no severity levels found, return appropriate response
        if not severity_levels:
            response = {
                "execution_status": "Failed",
                "status_code": 404,
                "message": "No Severity Levels found",
                "error_code": "NO_DATA",
                "error_message": "The SEVERITY_LEVELS table is empty or no active severity levels found",
                "output_kpis": {
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')
        #Prepare the severity levels list
        severity_levels_list = [{"id": row[0], "value": row[1]} for row in severity_levels]
        #Close the cursor and connection
        cursor.close()  
        conn.close()
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Severity Levels fetched successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            },
            "body": {
                "severity_levels": severity_levels_list
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')
    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error fetching Severity Levels",
            "error_code": "CONFIG_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')
        
#Route to fetch incident types
@app.route('/api/incidenttypes', methods=['GET'])
def fetch_incident_types():
    start_time = time.time()
    try:
        #Get the connection_string and schema from config 
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA 
        #Establishing the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to fetch incident types
        query = f"SELECT INCIDENT_TYPE_ID,INCIDENT_NAME  FROM {DB_SCHEMA}.INCIDENT_TYPES WHERE ACTIVE_FLAG = 'Y';"
        cursor.execute(query)
        #Fetch all incident types
        incident_types = cursor.fetchall()
        #If no incident types found, return appropriate response
        if not incident_types:
            response = {
                "execution_status": "Failed",
                "status_code": 404,
                "message": "No Incident Types found",
                "error_code": "NO_DATA",
                "error_message": "The INCIDENT_TYPES table is empty or no active incident types found",
                "output_kpis": {
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')
        #Prepare the incident types list
        incident_types_list = [{"id": row[0], "value": row[1]} for row in incident_types]
        #Close the cursor and connection
        cursor.close()
        conn.close()
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Incident Types fetched successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            },
            "body": {
                "emergency_types": incident_types_list
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')
    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error fetching Incident Types",
            "error_code": "CONFIG_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')
        
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8002, debug = True)