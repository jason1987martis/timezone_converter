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

# Replace this with a secure environment variable in production
PING_KEY = "123"

@app.get("/pinger")
def pinger(key: str = Query(..., description="Authentication key for cron job")):
    """
    Simple keep-alive endpoint that returns a 200 response
    if the provided key matches the configured secret.
    """
    if key != PING_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    return {"status": "alive", "message": "Pinger acknowledged successfully."}


@app.route('/timezones')
def get_timezones():
    # Send all available pytz timezones
    return jsonify({"timezones": pytz.all_timezones})

@app.route('/convert', methods=['POST'])
def convert_time():
    data = request.json
    from_tz_key = data.get("from_timezone")
    to_tz_key = data.get("to_timezone")  # optional
    time_str = data.get("time")  # Can be "HH:MM" or "YYYY-MM-DD HH:MM" format
    
    if from_tz_key not in pytz.all_timezones:
        return jsonify({"error": "Invalid timezone. Use one from /timezones"}), 400
    
    tz_from = pytz.timezone(from_tz_key)

    try:
        # Try parsing with full datetime first, fallback to HH:MM only
        try:
            time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            time_obj = datetime.strptime(time_str, "%H:%M")
            now_date = datetime.now().date()
            time_obj = datetime.combine(now_date, time_obj.time())

        # Localize to source timezone
        source_datetime = tz_from.localize(time_obj)

        results = {}
        if to_tz_key:  # only convert to one
            tz = pytz.timezone(to_tz_key)
            converted = source_datetime.astimezone(tz)
            results[to_tz_key] = converted.strftime('%Y-%m-%d %H:%M:%S')
        else:  # convert to all
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
        return jsonify({"error": "Invalid time format. Use 'HH:MM' or 'YYYY-MM-DD HH:MM'"}), 400

if __name__ == "__main__":
    app.run(debug=True)

