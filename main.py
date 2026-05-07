import os
import json
import random
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = "6f269bfdaed8be832a84c4f8916d6184"  # Your OpenWeatherMap API key

CROP_DATA = []

def load_crop_data():
    global CROP_DATA
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "crop_suitability.json")
        with open(json_path, "r") as f:
            CROP_DATA = json.load(f)
        print("Crop suitability data loaded successfully.")
    except FileNotFoundError:
        print("Error: 'crop_suitability.json' file not found.")
        CROP_DATA = []
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}")
        CROP_DATA = []

def geocode_city(location):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if data:
        return data[0]['lat'], data[0]['lon']
    else:
        raise ValueError(f"Could not geocode location: {location}")

def get_weather_by_coords(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    resp = requests.get(url)
    data = resp.json()
    if "main" not in data:
        raise ValueError(f"Weather API error: {data.get('message', 'Unknown error')}")
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    soil_moisture = random.uniform(25, 70)
    return temp, humidity, soil_moisture

def get_ndvi(temp, humidity):
    base = 0.3 + (humidity / 200) - (abs(temp - 30) / 100)
    return round(max(0, min(base, 0.9)), 2)

def find_suitable_crops(location, soil):
    matched_crops = []
    location_lower = location.lower()
    for entry in CROP_DATA:
        if entry["city"].lower() == location_lower and soil in entry["soil"]:
            matched_crops.extend(entry["crops"])
    return matched_crops

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        location = data.get("location")
        soil = data.get("soil")

        if not location or not soil:
            return jsonify({"error": "location and soil are required"}), 400

        lat, lon = geocode_city(location)
        temp, humidity, soil_moisture = get_weather_by_coords(lat, lon)
        ndvi = get_ndvi(temp, humidity)

        if humidity > 75 and temp > 30:
            pest_risk = "⚠️ High – humid and warm conditions favor pest growth"
        elif humidity > 60:
            pest_risk = "🟡 Moderate – possible pest signs"
        else:
            pest_risk = "🟢 Low – stable conditions"

        if soil_moisture < 30:
            mineral_status = "❌ Low – soil may need nutrient enrichment"
        elif soil_moisture < 50:
            mineral_status = "⚠️ Medium – maintain soil fertility"
        else:
            mineral_status = "✅ Good – healthy nutrient balance"

        if ndvi < 0.3:
            crop_condition = "❌ Poor vegetation – crops are stressed"
        elif ndvi < 0.6:
            crop_condition = "⚠️ Average – some areas under stress"
        else:
            crop_condition = "✅ Healthy – good crop vigor"

        suggested_crops = find_suitable_crops(location, soil)

        return jsonify({
            "location": location.title(),
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "soil_moisture": round(soil_moisture, 2),
            "ndvi": ndvi,
            "soil_type": soil,
            "pest_outbreak": pest_risk,
            "mineral_deficiency": mineral_status,
            "crop_condition": crop_condition,
            "suggested_crops": ", ".join(suggested_crops) if suggested_crops else "No suitable crops found"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    load_crop_data()
    app.run(debug=True)

if __name__ == "__main__":
    main()
