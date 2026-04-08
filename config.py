# config.py - إعدادات المشروع
import os

# ===== API Settings =====
API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
UNITS = "metric"  # celsius

# ===== Cities to Track =====
CITIES = [
    "Cairo",
    "Alexandria",
    "Dubai",
    "Riyadh",
    "London",
    "New York",
    "Tokyo",
    "Paris",
    "Berlin",
    "Istanbul"
]

# ===== Database Settings =====
DB_NAME = "weather_data.db"
DB_PATH = os.path.join(os.path.dirname(__file__), "database", DB_NAME)

# ===== Scheduler Settings =====
COLLECTION_INTERVAL_MINUTES = 30  # جمع البيانات كل 30 دقيقة

# ===== Alert Thresholds =====
ALERTS = {
    "high_temp": 35,      # تنبيه لو الحرارة فوق 35
    "low_temp": 0,        # تنبيه لو الحرارة تحت 0
    "high_humidity": 90,  # تنبيه لو الرطوبة فوق 90%
    "high_wind": 50,      # تنبيه لو الرياح فوق 50 كم/ساعة
}

# ===== Logging Settings =====
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

# ===== Reports Settings =====
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
