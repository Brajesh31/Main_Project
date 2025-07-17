from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import requests
import pickle
import pandas as pd
import numpy as np
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)



# Load the pre-trained model and scaler
model = pickle.load(open('best_rf_model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))

# OpenWeather API key (replace with your own)
API_KEY = "157f8f284185045c40c97e137d3f20d6"

# Function to fetch weather data from OpenWeather API
def get_weather_data(latitude, longitude):
    try:
        # Build the API request URL
        api_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={API_KEY}"
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for failed requests
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Function to preprocess weather data for the model
def preprocess_weather_data(weather_json):
    wind_speeds = []
    temperatures = []
    humidities = []
    pressures = []
    timestamps = []

    # Extract relevant weather data from the API response
    for entry in weather_json['list']:
        wind_speeds.append(entry['wind']['speed'])  # Wind speed in m/s
        temperatures.append(entry['main']['temp'])  # Temperature in °C
        humidities.append(entry['main']['humidity'])  # Humidity in %
        pressures.append(entry['main']['pressure'])  # Pressure in hPa
        timestamps.append(entry['dt_txt'])  # Timestamp

    # Create a DataFrame for the features
    data = pd.DataFrame({
        'Wind Speed (m/s)': wind_speeds,
        'Temperature': temperatures,
        'Humidity': humidities,
        'Pressure': pressures
    })

    # Scale the data using the pre-fitted scaler
    scaled_data = scaler.transform(data)

    return scaled_data, timestamps

# Function to format the output
def format_output(predictions, timestamps, weather_json):
    output = []
    for i, prediction in enumerate(predictions):
        output.append({
            "timestamp": timestamps[i],
            "predicted_power": round(prediction, 2),  # Predicted power in kW
            "wind_speed": weather_json['list'][i]['wind']['speed'],  # Wind speed in m/s
            "temperature": weather_json['list'][i]['main']['temp'],  # Temperature in °C
            "humidity": weather_json['list'][i]['main']['humidity'],  # Humidity in %
            "pressure": weather_json['list'][i]['main']['pressure']  # Pressure in hPa
        })
    return output

# Define the prediction endpoint
@app.route('/predict', methods=['GET'])
def predict():
    try:
        # Get latitude and longitude from the request
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        if not latitude or not longitude:
            return jsonify({"error": "Latitude and Longitude are required!"}), 400

        # Fetch weather data
        weather_json = get_weather_data(latitude, longitude)
        if "error" in weather_json:
            return jsonify({"error": weather_json["error"]}), 500

        # Preprocess the weather data
        scaled_data, timestamps = preprocess_weather_data(weather_json)

        # Predict power generation
        predictions = model.predict(scaled_data)

        # Format the output
        output = format_output(predictions, timestamps, weather_json)

        return jsonify({"data": output}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # This allows external devices to access the server

