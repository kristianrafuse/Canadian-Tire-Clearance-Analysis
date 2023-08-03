from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

app = Flask(__name__)

# Connection details
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOST')
database = os.environ.get('DB_NAME')

# Create the database URL
url = f'postgresql://{username}:{password}@{host}/{database}'

# Create the engine
engine = create_engine(url)

# Create a scoped session to interact with the database and automatically close after the request has been processed.
session = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def welcome():
    return render_template("index.html")

# Route for api/data access
@app.route("/api")
def api():
    data = {}

    # Loop through the table names
    table_names = ["clearance", "sales"]
    for table_name in table_names:
        try:
            # Execute a select query on each table
            query = f"SELECT * FROM {table_name}"
            result = engine.execute(query)
            # Fetch all rows and columns
            rows = result.fetchall()
            columns = result.keys()
            # use zip function to take columns and rows and pair their elements together
            # then create a dictonary 
            table_data = [dict(zip(columns, row)) for row in rows]
            data[table_name] = {"csv_data": table_data}
            # error handling -- this saved me when I decided it would be a good idea to upgrade
            # SQLalchemy...
        except Exception as e:
            print(e)
            return jsonify({"error": f"An error occurred while fetching data from the table {table_name}: {str(e)}"})

    return jsonify(data)

# Remove the session after each request
# I read that By using a scoped session and the teardown_appcontext, you ensure that sessions are properly 
# created and cleaned up for each request, preventing any potential resource leaks and ensuring 
# efficient use of database connections.

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

if __name__ == "__main__":
    app.run()