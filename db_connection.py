import mysql.connector
import streamlit as st

def connect_to_mysql(host, port, username, password):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"MySQL connection error: {e}")
        return None
