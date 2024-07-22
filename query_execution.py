import requests
import json
import mysql.connector


def get_query_from_gemini(user_question, schema):
    API_KEY = st.secrets["gemini_api_key"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

    prompt = f'''
    You are a language model that converts natural language questions into SQL queries.
    Here is the schema of the "{schema}" database:
    
    {schema}
    
    User Question: "{user_question}"
    
    If the question does not relate to the schema or table information, please respond with: "Please provide a question related to the schema or table information."

    Whenever the question is related to one specific database, check all schema of that database (tables, columns, and data types). the ask questions involving more than two tables, and it needs to handle those properly and create a query properly.
    
    Consider whichever column datatype is "enum", so take care of that.

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
        return None
    except KeyError:
        return None
    except Exception as err:
        return None

def execute_sql_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        result = cursor.fetchall()
        return column_names, result
    except mysql.connector.Error as e:
        return None, None
