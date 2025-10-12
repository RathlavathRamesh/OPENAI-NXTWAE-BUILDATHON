from flask import Flask, request, Response, jsonify
import time 
import json 
import psycopg2
from environment import Config
from google import genai
from flask_cors import CORS
import requests
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import base64

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

#Route to fetch all sections
@app.route('/api/getsections', methods=['POST'])
def get_sections():
    #Fetch the input payload from the request
    input_data = request.get_json()
    if input_data is None or "user_id" not in input_data:
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
    start_time = time.time()
    try:
        #Fetch the DB connection string and schema from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        user_id = int(input_data.get("user_id"))
        #Create the connection to the database
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Prepare a query to fetch all sections
        query = f"SELECT SECTION_ID, SECTION_NAME,PROMPT,PROMPT_GIVEN_AT,RESPONSE,RESPONSE_PROVIDED_AT FROM {DB_SCHEMA}.PROMPT_RESPONSES WHERE ACTIVE_FLAG = 'Y' AND USER_ID = %s;"
        cursor.execute(query, (user_id,))
        sections = cursor.fetchall()
        #If no sections found, return appropriate response
        if not sections:
            response = {
                "execution_status": "Failed",
                "status_code": 404,
                "message": "No Sections found",
                "error_code": "NO_DATA",
                "error_message": "The PROMPT_RESPONSES table is empty or no active sections found",
                "output_kpis": {
                    "execution_time": round(time.time() - start_time, 2)
                }
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')
        #Prepare the sections list
        sections_list = []
        for row in sections:
            section = {
                "section_id": row[0],
                "section_name": row[1],
                "prompt": row[2],
                "prompt_given_at": str(row[3]),
                "response": row[4]["response"],
                "response_provided_at": str(row[5])
            }
            sections_list.append(section)
        #Close the cursor and connection
        cursor.close()
        conn.close()
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Sections fetched successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            },
            "body": {
                "sections": sections_list
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')
    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error fetching Sections",
            "error_code": "CONFIG_ERROR",
            "error_message": str(e),
            "output_kpis": {
                "execution_time": round(time.time() - start_time, 2)
            }
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')

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
        
@app.route('/api/register', methods=['POST'])
def register_user():
    start_time = time.time()
    try:
        input_data = request.get_json()
        required_fields = ['user_name', 'email', 'password']

        # Validate input
        if not input_data or not all(field in input_data for field in required_fields):
            response = {
                "execution_status": "Failed",
                "status_code": 400,
                "message": "Invalid input: Missing required fields",
                "error_code": "INVALID_INPUT",
                "error_message": "Fields 'user_name', 'email', and 'password' are required",
                "output_kpis": {"execution_time": 0}
            }
            return Response(json.dumps(response), status=400, mimetype='application/json')

        user_name = input_data['user_name']
        email = input_data['email']
        password = input_data['password']
        hashed_password = password

        # Connect to DB
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute(f"SELECT USER_ID FROM {DB_SCHEMA}.USERS_INFORMATION WHERE EMAIL = %s;", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            response = {
                "execution_status": "Failed",
                "status_code": 409,
                "message": "User already exists",
                "error_code": "USER_EXISTS",
                "error_message": "Email is already registered",
                "output_kpis": {"execution_time": round(time.time() - start_time, 2)}
            }
            return Response(json.dumps(response), status=409, mimetype='application/json')

        # Insert new user
        insert_query = f"""
            INSERT INTO {DB_SCHEMA}.USERS_INFORMATION
            (USER_NAME, EMAIL, PASSWORD, CREATED_BY, CREATED_DATE, ACTIVE_FLAG)
            VALUES (%s, %s, %s, %s, NOW(), 'Y')
            RETURNING USER_ID;
        """
        cursor.execute(insert_query, (user_name, email, hashed_password, 1))
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        response = {
            "execution_status": "Success",
            "status_code": 201,
            "message": "User registered successfully",
            "error_code": None,
            "error_message": None,
            "output_kpis": {"execution_time": round(time.time() - start_time, 2)},
            "body": {"user_id": user_id, "email": email}
        }
        return Response(json.dumps(response), status=201, mimetype='application/json')

    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error registering user",
            "error_code": "DB_ERROR",
            "error_message": str(e),
            "output_kpis": {"execution_time": round(time.time() - start_time, 2)}
        }
        return Response(json.dumps(response), status=500, mimetype='application/json')

@app.route('/api/login', methods=['POST'])
def login_user():
    start_time = time.time()
    try:
        input_data = request.get_json()
        if not input_data or 'email' not in input_data or 'password' not in input_data:
            response = {
                "execution_status": "Failed",
                "status_code": 400,
                "message": "Invalid input: Missing email or password",
                "error_code": "INVALID_INPUT",
                "error_message": "'email' and 'password' are required",
                "output_kpis": {"execution_time": 0}
            }
            return Response(json.dumps(response), status=400, mimetype='application/json')

        email = input_data['email']
        password = input_data['password']

        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Fetch user details
        cursor.execute(
            f"SELECT USER_ID, USER_NAME, PASSWORD, ACTIVE_FLAG FROM {DB_SCHEMA}.USERS_INFORMATION WHERE EMAIL = %s;",
            (email,))
        user = cursor.fetchone()

        if not user:
            response = {
                "execution_status": "Failed",
                "status_code": 404,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND",
                "error_message": "Invalid email or password",
                "output_kpis": {"execution_time": round(time.time() - start_time, 2)}
            }
            return Response(json.dumps(response), status=404, mimetype='application/json')

        user_id, user_name, stored_password, active_flag = user

        # Check if active
        if active_flag != 'Y':
            response = {
                "execution_status": "Failed",
                "status_code": 403,
                "message": "Account inactive",
                "error_code": "ACCOUNT_INACTIVE",
                "error_message": "User account is deactivated",
                "output_kpis": {"execution_time": round(time.time() - start_time, 2)}
            }
            return Response(json.dumps(response), status=403, mimetype='application/json')

        # Verify password
        if not password == stored_password:
            response = {
                "execution_status": "Failed",
                "status_code": 401,
                "message": "Invalid credentials",
                "error_code": "INVALID_CREDENTIALS",
                "error_message": "Incorrect password",
                "output_kpis": {"execution_time": round(time.time() - start_time, 2)}
            }
            return Response(json.dumps(response), status=401, mimetype='application/json')

        cursor.close()
        conn.close()

        # Successful login
        response = {
            "execution_status": "Success",
            "status_code": 200,
            "message": "Login successful",
            "error_code": None,
            "error_message": None,
            "output_kpis": {"execution_time": round(time.time() - start_time, 2)},
            "body": {
                "user_id": user_id,
                "user_name": user_name,
                "email": email
            }
        }
        return Response(json.dumps(response), status=200, mimetype='application/json')

    except Exception as e:
        response = {
            "execution_status": "Failed",
            "status_code": 500,
            "message": "Error during login",
            "error_code": "DB_ERROR",
            "error_message": str(e),
            "output_kpis": {"execution_time": round(time.time() - start_time, 2)}
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
                        A.RISK_FACTORS AS RISK_FACTORS
                    FROM 
                        {DB_SCHEMA}.INCIDENTS A
                        LEFT JOIN 
                        {DB_SCHEMA}.SEVERITY_LEVELS B 
                        ON A.SEVERITY_LEVEL_ID = B.SEVERITY_LEVEL_ID
                        JOIN 
                        {DB_SCHEMA}.INCIDENT_TYPES C
                        ON A.INCIDENT_TYPE_ID = C.INCIDENT_TYPE_ID
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
                "risk_factors": row[10]
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
                        LEFT JOIN 
                        {DB_SCHEMA}.SEVERITY_LEVELS B 
                        ON A.SEVERITY_LEVEL_ID = B.SEVERITY_LEVEL_ID
                        AND 
                        A.ACTIVE_FLAG = 'Y'
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

UPLOAD_FOLDER = "uploads"
CORE_API_URL = "http://localhost:8000/upload_request"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_base64_file(base64_string, filename):
    """Save a base64-encoded file to disk and return the path."""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_string))
    return file_path


@app.route("/api/submitrequest", methods=["POST"])
def submit_request():
    try:
        # 🔹 Extract form fields
        description = request.form.get("description")
        location = request.form.get("location")
        reporter_id = int(request.form.get("reporterId"))
        reporter_contact = request.form.get("reporterContactNumber")
        incident_type = request.form.get("emergencyType")
        incident_type_id = request.form.get("emergencyTypeId")
        severity = request.form.get("estimatedSeverity")

        # 🔹 Extract uploaded files
        images = request.files.getlist("images")
        videos = request.files.getlist("videos")
        audios = request.files.getlist("audio")

        # Split lat, lon
        lat, lon = location.split(",") if location else (None, None)
        uploaded_files = images + videos + audios

      # Convert to proper form-data tuples
        files = []
        for f in uploaded_files:
            if f and f.filename:
                files.append(
                    ("files", (f.filename, f.stream, f.mimetype or "application/octet-stream"))
                )

        # 🔹 Database connection
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        # Format location as JSON
        location_json = {
            "place": "NIAT Hyderabad",
            "latitude": lat.strip() if lat else "",
            "longitude": lon.strip() if lon else ""
        }

        # 🔹 Insert into INCIDENTS table
        insert_query = f"""
            INSERT INTO {DB_SCHEMA}.INCIDENTS
            (INCIDENT_TYPE_ID, USER_ID, LOCATION, DESCRIPTION, INCIDENT_STATUS, CREATED_BY)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING INCIDENT_ID;
        """
        cursor.execute(insert_query, (
            incident_type_id,
            reporter_id,
            json.dumps(location_json),
            description,
            'Submitted',
            reporter_id
        ))
        print("Inserted incident record.")

        incident_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        # 🔹 Prepare payload for Core API
        payload = {
            "channel": "app",
            "text": description,
            "lat": lat.strip() if lat else "",
            "lon": lon.strip() if lon else "",
            "incident_id": incident_id
        }

        # 🔹 Send to Core API
        response = requests.post(
            CORE_API_URL,
            data=payload,
            files=files,
            headers={"Accept": "application/json"}
        )
        return jsonify({
            "status": "success",
            "incident_id": incident_id,
            "core_api_response": response.json()
        }), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

       
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8002, debug = True)