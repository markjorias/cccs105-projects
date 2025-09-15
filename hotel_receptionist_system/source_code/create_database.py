import mysql.connector
from mysql.connector import Error
import os

def read_sql_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def execute_sql_script(cursor, sql_script):
    # Split the script into individual statements
    statements = sql_script.split(';')
    
    for statement in statements:
        # Skip empty statements
        if statement.strip():
            try:
                cursor.execute(statement)
            except Error as e:
                print(f"Error executing statement: {e}")
                print(f"Statement: {statement}")

def create_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password=""   # Replace with your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Connected to MySQL server")

            # Read and execute schema.sql
            print("Creating database and tables...")
            schema_sql = read_sql_file('database\schema.sql')
            execute_sql_script(cursor, schema_sql)
            
            # Read and execute initial_data.sql
            print("Inserting initial data...")
            initial_data_sql = read_sql_file('database\initial_data.sql')
            execute_sql_script(cursor, initial_data_sql)

            # Commit the changes
            connection.commit()
            print("Database creation and initialization completed successfully!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_database() 