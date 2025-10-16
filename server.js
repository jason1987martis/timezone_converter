import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import moment from "moment-timezone";

const app = express();
const PORT = process.env.PORT || 10000;

app.use(cors());
app.use(bodyParser.json());

// Welcome endpoint
app.get("/", (req, res) => {
  res.json({
    message: "Welcome to the Timezone Converter API",
    usage: "POST /convert with {from_timezone, time}"
  });
});

// Replace this with environment variable in production
const PING_KEY = "123";

// Pinger endpoint (keep-alive)
app.get("/pinger", (req, res) => {
  const key = req.query.key || "Guest";
  if (key !== PING_KEY) {
    return res.status(403).json({ error: "Invalid key" });
  }
  res.json({ status: "alive", message: "Pinger acknowledged successfully." });
});

// Get all timezones
app.get("/timezones", (req, res) => {
  res.json({ timezones: moment.tz.names() });
});

// Time conversion endpoint
app.post("/convert", (req, res) => {
  const { from_timezone, to_timezone, time } = req.body;

  // Validate timezone
  if (!moment.tz.zone(from_timezone)) {
    return res.status(400).json({
      error: "Invalid timezone. Use one from /timezones"
    });
  }

  let inputMoment;
  try {
    // Try parsing with date, fallback to HH:mm only
    inputMoment = moment.tz(time, "YYYY-MM-DD HH:mm", from_timezone);
    if (!inputMoment.isValid()) {
      const today = moment().format("YYYY-MM-DD");
      inputMoment = moment.tz(`${today} ${time}`, "YYYY-MM-DD HH:mm", from_timezone);
    }
  } catch {
    return res.status(400).json({
      error: "Invalid time format. Use 'HH:MM' or 'YYYY-MM-DD HH:MM'"
    });
  }

  const results = {};

  if (to_timezone) {
    // Convert to specific timezone
    if (!moment.tz.zone(to_timezone)) {
      return res.status(400).json({
        error: "Invalid target timezone. Use one from /timezones"
      });
    }
    const converted = inputMoment.clone().tz(to_timezone);
    results[to_timezone] = converted.format("YYYY-MM-DD HH:mm:ss");
  } else {
    // Convert to all timezones
    moment.tz.names().forEach((tz) => {
      const converted = inputMoment.clone().tz(tz);
      results[tz] = converted.format("YYYY-MM-DD HH:mm:ss");
    });
  }

  res.json({
    from_timezone,
    input_time: time,
    converted_times: results
  });
});

// Start server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 Timezone Converter API running on port ${PORT}`);
});
