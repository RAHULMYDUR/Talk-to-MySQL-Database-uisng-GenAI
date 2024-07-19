import requests
import streamlit as st
import json
import mysql.connector

API_KEY = "AIzaSyCzdCOyd-7os-SRgbEolxtwEEgYYkjKpsM"

def get_query_from_gemini(user_question, schema):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    prompt = f'''
    You are a language model that converts natural language questions into SQL queries.
    Here is the schema of the "{schema}" database:
    
    {schema}
    
    User Question: "{user_question}"
    
    Convert the above question into a valid SQL query.
    '''
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data), verify=False)
        response.raise_for_status()
        generated_content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        if generated_content.startswith("```sql"):
            generated_content = generated_content.replace("```sql", "").strip()
        if generated_content.endswith("```"):
            generated_content = generated_content.replace("```", "").strip()
        return generated_content
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        return None
    except KeyError:
        st.error(f"Unexpected response format: {response.json()}")
        return None
    except Exception as err:
        st.error(f"Exception occurred during request: {err}")
        return None

def execute_sql_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        return column_names, result
    except mysql.connector.Error as e:
        st.error(f"MySQL Error: {e}")
        return None, None
