import streamlit as st
import pandas as pd
from db_connection import connect_to_mysql
from query_execution import get_query_from_gemini, execute_sql_query

def main():
    st.title("Talk to MySQL Database")

    # # Sidebar for MySQL Database Connection
    # st.sidebar.subheader("MySQL Database Connection")
    # username = st.sidebar.text_input("Username")
    # password = st.sidebar.text_input("Password", type="password")
    # host = st.sidebar.text_input("Host", value="localhost")
    # port = st.sidebar.text_input("Port", value="3306")

    # Sidebar for MySQL Database Connection
    st.sidebar.subheader("MySQL Database Connection")
    username = st.secrets["mysql"]["username"]
    password = st.secrets["mysql"]["password"]
    host = st.secrets["mysql"]["host"]
    port = st.secrets["mysql"]["port"]

    if 'conn' not in st.session_state:
        st.session_state.conn = None
        st.session_state.databases = []
        st.session_state.schema = ""
        st.session_state.selected_database = None
        st.session_state.generated_query = ""
        st.session_state.result = None
        st.session_state.column_names = []

    # Connect to MySQL
    if st.sidebar.button("Connect"):
        if username and password and host and port:
            st.session_state.conn = connect_to_mysql(host, port, username, password)
            if st.session_state.conn:
                st.success("Connected to MySQL database successfully.")
                cursor = st.session_state.conn.cursor()
                cursor.execute("SHOW DATABASES")
                st.session_state.databases = [db[0] for db in cursor.fetchall()]
            else:
                st.error("Failed to connect to MySQL database. Check your credentials and try again.")

    # Database Selection and Schema Display
    if st.session_state.conn:
        st.sidebar.subheader("Available Databases")
        selected_database = st.sidebar.selectbox("Select a database", st.session_state.databases, key="database_selectbox")

        if selected_database:
            if selected_database != st.session_state.selected_database:
                st.session_state.selected_database = selected_database
                st.session_state.schema = ""

                try:
                    cursor = st.session_state.conn.cursor()
                    cursor.execute(f"USE {selected_database}")
                    cursor.execute("SHOW TABLES")
                    tables = [table[0] for table in cursor.fetchall()]
                    st.session_state.schema = f"{selected_database} Tables: {', '.join(tables)}"
                except Exception as e:
                    st.error(f"Error fetching database schema: {e}")

    # Display schema if a database is selected
    if st.session_state.selected_database:
        st.sidebar.write(f"Selected Database: {st.session_state.selected_database}")
        st.sidebar.write(f"Database Schema: {st.session_state.schema}")

    # User Input for Query Generation
    user_question = st.text_area("Ask a question about the MySQL database tables:")

    if st.button("Generate SQL Query"):
        if user_question:
            st.write(f"**User Question:** {user_question}")
            st.write(f"**Sending to Gemini API with Schema:** {st.session_state.schema}")
            st.session_state.generated_query = get_query_from_gemini(user_question, st.session_state.schema)
            if st.session_state.generated_query:
                st.write(f"**Generated SQL Query:**")
                st.code(st.session_state.generated_query)

                if st.session_state.generated_query:
                    try:
                        st.write("Executing SQL query...")
                        column_names, st.session_state.result = execute_sql_query(st.session_state.conn, st.session_state.generated_query)
                        if st.session_state.result:
                            st.write(f"**Query Result:**")
                            df = pd.DataFrame(st.session_state.result, columns=column_names)
                            st.dataframe(df)
                        else:
                            st.warning("No results returned from the query.")
                    except Exception as e:
                        st.error(f"Error executing SQL query: {e}")
            else:
                st.warning("The question did not relate to the schema or table information. Please provide a relevant question.")
        else:
            st.warning("Please enter a question before generating a SQL query.")

if __name__ == "__main__":
    main()
