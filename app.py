from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import pytz

app = Flask(__name__)
CORS(app)  # 🚀 allow all origins by default
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Timezone Converter API",
        "usage": "POST /convert with {from_timezone, time}"
    })

@app.route('/timezones')
def get_timezones():
    # Send all available pytz timezones
    return jsonify({"timezones": pytz.all_timezones})

@app.route('/convert', methods=['POST'])
def convert_time():
    data = request.json
    
    from_tz_key = data.get("from_timezone")
    time_str = data.get("time")  # Expected format: "HH:MM"
    
    if from_tz_key not in pytz.all_timezones:
        return jsonify({"error": "Invalid timezone. Use one from /timezones"}), 400
    
    tz_from = pytz.timezone(from_tz_key)
    
    try:
        # Parse input time
        time_obj = datetime.strptime(time_str, "%H:%M")
        now_date = datetime.now().date()
        source_datetime = datetime.combine(now_date, time_obj.time())
        source_datetime = tz_from.localize(source_datetime)

        results = {}
        for tz_key in pytz.all_timezones:
            tz = pytz.timezone(tz_key)
            converted = source_datetime.astimezone(tz)
            results[tz_key] = converted.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            "from_timezone": from_tz_key,
            "input_time": time_str,
            "converted_times": results
        })
    
    except ValueError:
        return jsonify({"error": "Invalid time format. Use HH:MM (24-hour clock)."}), 400


if __name__ == "__main__":
    app.run(debug=True)
