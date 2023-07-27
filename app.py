from flask import Flask, jsonify, render_template, request
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Connection details
username = 'irgmjyyk'
password = '7xvPybDcdNCzDCgnW1XmTNIvwSKp9GfO'
host = 'rajje.db.elephantsql.com'
database = 'irgmjyyk'

# Create the database URL
url = f'postgresql://{username}:{password}@{host}/{database}'

# Create the engine
engine = create_engine(url)

# Create a base class for declarative models
Base = declarative_base()

# Define the UserPreferences model
class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)

# Create the table in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

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


@app.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        email = request.form.get("email")
        threshold = int(request.form.get("threshold"))

        # Insert the email and threshold into the database
        user_preferences = UserPreferences(email=email, threshold=threshold)
        session.add(user_preferences)
        session.commit()

        return jsonify({"message": "Subscription successful!"})
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the subscription: {str(e)}"})

if __name__ == "__main__":
    app.run()