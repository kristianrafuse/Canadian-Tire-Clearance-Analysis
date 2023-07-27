from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine

app = Flask(__name__)

# Connection details
username = 'irgmjyyk'
password = ''
host = 'rajje.db.elephantsql.com'
database = 'irgmjyyk'

# Create the database URL
url = f'postgresql://{username}:{password}@{host}/{database}'

# Create the engine
engine = create_engine(url)

@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/api")
def api():
    data = {}

    # Loop through the table names
    table_names = ["clearance", "hot_sale", "red_alert_deals", "sales"]
    for table_name in table_names:
        try:
            # Execute a select query on each table
            query = f"SELECT * FROM {table_name}"
            result = engine.execute(query)
            # Fetch all rows and convert to a list of dictionaries
            rows = result.fetchall()
            columns = result.keys()
            table_data = [dict(zip(columns, row)) for row in rows]
            data[table_name] = {"csv_data": table_data}
        except Exception as e:
            return jsonify({"error": f"An error occurred while fetching data from the table {table_name}: {str(e)}"})

    return jsonify(data)

if __name__ == "__main__":
    app.run()