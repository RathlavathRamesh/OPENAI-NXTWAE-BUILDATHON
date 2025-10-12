import psycopg2
import json 
from typing import Dict, Any
from .environment import Config


def insert_incident(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Function to insert a new incident into the INCIDENTS table
    """
    try:
        #Get the Database connection parameters from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        #Create the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to insert a new incident
        insert_query = f"""
            INSERT INTO {DB_SCHEMA}.INCIDENTS (INCIDENT_TYPE, INCIDENT_DESCRIPTION, INCIDENT_STATUS, CREATED_AT, UPDATED_AT)
            VALUES (%s, %s, %s, NOW(), NOW())
            RETURNING INCIDENT_ID;
        """
        cursor.execute(insert_query, (
            incident_data.get("incident_type"),
            incident_data.get("incident_description"),
            incident_data.get("incident_status", "Open")
        ))
        incident_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "execution_status": "Success",
            "status_code": 201,
            "message": f"Incident created successfully with incident_id: {incident_id}",
            "incident_id": incident_id
        }
    except Exception as e:
        return {
            "execution_status": "Failed",
            "status_code": 500,
            "message": f"Error creating incident. Error: {str(e)}"
        }

def processed_input_summary_json(incident_id : int, processed_input_json : json) -> Dict[str, Any]:
    """
    Function to update the processed_input_json based on incident_id
    """
    try:
        #Get the Database connection parameters from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        #Create the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to update the processed_input_json
        update_query = f"""
            UPDATE {DB_SCHEMA}.INCIDENTS
            SET PROCESSED_INPUT_JSON = %s
            WHERE INCIDENT_ID = %s;
        """
        cursor.execute(update_query, (json.dumps(processed_input_json), incident_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "execution_status": "Success",
            "status_code": 200,
            "message": f"Processed input JSON updated successfully for incident_id: {incident_id}"
        }
    except Exception as e:
        return {
            "execution_status": "Failed",
            "status_code": 500,
            "message": f"Error updating processed input JSON for incident_id: {incident_id}. Error: {str(e)}"
        }
        
def analyze_summarize_json(incident_id : int, analyze_summarize_json : json) -> Dict[str, Any]:
    """
    Function to update the analyze_summarize_json based on incident_id
    """
    try:
        #Get the Database connection parameters from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        #Create the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to update the analyze_summarize_json
        update_query = f"""
            UPDATE {DB_SCHEMA}.INCIDENTS
            SET ANALYZE_SUMMARY_JSON = %s
            WHERE INCIDENT_ID = %s;
        """
        cursor.execute(update_query, (json.dumps(analyze_summarize_json), incident_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "execution_status": "Success",
            "status_code": 200,
            "message": f"Analyze and Summarize JSON updated successfully for incident_id: {incident_id}"
        }
    except Exception as e:
        return {
            "execution_status": "Failed",
            "status_code": 500,
            "message": f"Error updating Analyze and Summarize JSON for incident_id: {incident_id}. Error: {str(e)}"
        }
def judgement_summary_json(incident_id : int, judgement_summary_json : json) -> Dict[str, Any]:
    """
    Function to update the judgement_summary_json based on incident_id
    """
    try:
        #Get the Database connection parameters from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        #Create the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to update the judgement_summary_json
        update_query = f"""
            UPDATE {DB_SCHEMA}.INCIDENTS
            SET JUDGEMENT_SUMMARY_JSON = %s
            WHERE INCIDENT_ID = %s;
        """
        cursor.execute(update_query, (json.dumps(judgement_summary_json), incident_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "execution_status": "Success",
            "status_code": 200,
            "message": f"Judgement Summary JSON updated successfully for incident_id: {incident_id}"
        }
    except Exception as e:
        return {
            "execution_status": "Failed",
            "status_code": 500,
            "message": f"Error updating Judgement Summary JSON for incident_id: {incident_id}. Error: {str(e)}"
        }

def final_summary_json(incident_id : int, final_summary_json : json) -> Dict[str, Any]:
    """
    Function to update the final_summary_json based on incident_id
    """
    try:
        #Get the Database connection parameters from config
        DB_CONNECTION_STRING = Config.DB_CONNECTION_STRING
        DB_SCHEMA = Config.DB_SCHEMA
        #Create the connection
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        #Query to update the final_summary_json
        update_query = f"""
                            UPDATE {DB_SCHEMA}.INCIDENTS i
                            SET
                                FINAL_SUMMARY_JSON = %s,
                                PRIORITY_SCORE = (to_jsonb(%s) ->> 'priority_score')::INT,
                                RISK_FACTORS = (to_jsonb(%s) ->> 'recommendations')::JSONB,
                                SEVERITY_LEVEL_ID = (
                                    SELECT s.severity_level_id
                                    FROM {DB_SCHEMA}.severity_levels s
                                    WHERE s.severity_level_name = (to_jsonb(%s) ->> 'severity')
                                    LIMIT 1
                                )
                            WHERE i.INCIDENT_ID = %s;
                        """
        # Convert the input JSON to a Python dictionary if it's a string
        data = final_summary_json
        cursor.execute(
                        update_query,
                        (
                            json.dumps(data),  # 1 → FINAL_SUMMARY_JSON
                            json.dumps(data),  # 2 → Extract priority_score
                            json.dumps(data),  # 3 → Extract recommendations
                            json.dumps(data),  # 4 → Extract severity for lookup
                            incident_id        # 5 → Target record
                        )
                    )
        cursor.execute(update_query, (json.dumps(final_summary_json), incident_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "execution_status": "Success",
            "status_code": 200,
            "message": f"Final Summary JSON updated successfully for incident_id: {incident_id}"
        }
    except Exception as e:
        return {
            "execution_status": "Failed",
            "status_code": 500,
            "message": f"Error updating Final Summary JSON for incident_id: {incident_id}. Error: {str(e)}"
        }
       
 
 