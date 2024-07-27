import json
from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
from datetime import datetime  # Import datetime module

app = Flask(__name__)

# Initialize MongoDB client and specify the database and collection
client = MongoClient("mongodb+srv://aylascawol:<password>@ayla-sic5-scawol.grwwhow.mongodb.net/?retryWrites=true&w=majority&appName=ayla-sic5-scawol")
db = client["scawol-database"]
jarak_collection = db["sensor-colection3"]

@app.route("/")
def root_route():
    return "Hello world!"

@app.route("/jarak")
def get_jarak():
    # Retrieve all documents from the collection and convert them to a list of floats
    jarak_list = list(jarak_collection.find({}, {"_id": 0, "jarak": 1, "timestamp": 1}))
    
    # Extract jarak values and timestamps into separate lists
    jarak_data = [item["jarak"] for item in jarak_list]
    timestamps = [item["timestamp"] for item in jarak_list]
    
    # Create a DataFrame using Pandas
    df = pd.DataFrame({"jarak": jarak_data, "timestamp": timestamps})
    
    # Perform some analysis or manipulations with Pandas (example: calculating mean)
    jarak_mean = df['jarak'].mean()
    
    # Prepare response JSON
    response = {
        "mean_jarak": jarak_mean,
        "jarak_data": jarak_data,
        "timestamps": timestamps
    }
    
    return jsonify(response)

def insert_jarak_to_db(jarak_value):
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Insert data into MongoDB with timestamp
    jarak_collection.insert_one({"jarak": jarak_value, "timestamp": timestamp})
    print(f"Received jarak {jarak_value} at {timestamp}")

@app.route("/submit-jarak", methods=["POST"])
def post_jarak():
    pesan = request.data.decode("utf8")
    jarak_value = float(pesan)
    insert_jarak_to_db(jarak_value)
    return f"Received jarak {pesan}"

@app.route("/submit", methods=["POST"])
def post_data():
    pesan = request.data.decode("utf8")
    pesan = json.loads(pesan)
    jarak_value = float(pesan["jarak"])
    insert_jarak_to_db(jarak_value)
    return f"Received data {pesan}"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')