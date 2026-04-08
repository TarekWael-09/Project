# database.py - قاعدة البيانات
import sqlite3
import os
import logging
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection():
    """الاتصال بقاعدة البيانات"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # نرجع النتائج كـ dictionary
    return conn


def setup_database():
    """إنشاء الجداول لو مش موجودة"""
    conn = get_connection()
    cursor = conn.cursor()

    # جدول المدن
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            city_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL UNIQUE,
            country   TEXT,
            latitude  REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # جدول بيانات الطقس
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            record_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id           INTEGER NOT NULL,
            timestamp         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            temperature_c     REAL,
            feels_like_c      REAL,
            humidity          INTEGER,
            pressure_hpa      REAL,
            wind_speed_mps    REAL,
            wind_direction    INTEGER,
            weather_condition TEXT,
            weather_desc      TEXT,
            visibility_m      INTEGER,
            cloudiness        INTEGER,
            FOREIGN KEY (city_id) REFERENCES cities(city_id)
        )
    ''')

    # جدول التنبيهات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id     INTEGER NOT NULL,
            alert_type  TEXT NOT NULL,
            alert_msg   TEXT NOT NULL,
            value       REAL,
            threshold   REAL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (city_id) REFERENCES cities(city_id)
        )
    ''')

    # جدول سجل التشغيل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            run_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status       TEXT NOT NULL,
            cities_count INTEGER DEFAULT 0,
            records_saved INTEGER DEFAULT 0,
            errors_count  INTEGER DEFAULT 0,
            duration_sec  REAL DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("✅ قاعدة البيانات جاهزة")


def insert_city(city_name, country=None, lat=None, lon=None):
    """إضافة مدينة جديدة"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO cities (city_name, country, latitude, longitude)
            VALUES (?, ?, ?, ?)
        ''', (city_name, country, lat, lon))
        conn.commit()

        cursor.execute('SELECT city_id FROM cities WHERE city_name = ?', (city_name,))
        row = cursor.fetchone()
        return row['city_id'] if row else None
    finally:
        conn.close()


def insert_weather(city_id, data):
    """حفظ بيانات الطقس"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO weather_data (
                city_id, temperature_c, feels_like_c, humidity,
                pressure_hpa, wind_speed_mps, wind_direction,
                weather_condition, weather_desc, visibility_m, cloudiness
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            city_id,
            data.get('temperature'),
            data.get('feels_like'),
            data.get('humidity'),
            data.get('pressure'),
            data.get('wind_speed'),
            data.get('wind_direction'),
            data.get('condition'),
            data.get('description'),
            data.get('visibility'),
            data.get('cloudiness')
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_alert(city_id, alert_type, message, value, threshold):
    """حفظ تنبيه"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO alerts (city_id, alert_type, alert_msg, value, threshold)
            VALUES (?, ?, ?, ?, ?)
        ''', (city_id, alert_type, message, value, threshold))
        conn.commit()
    finally:
        conn.close()


def log_pipeline_run(status, cities_count=0, records_saved=0, errors_count=0, duration=0):
    """تسجيل نتيجة تشغيل الـ pipeline"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO pipeline_runs (status, cities_count, records_saved, errors_count, duration_sec)
            VALUES (?, ?, ?, ?, ?)
        ''', (status, cities_count, records_saved, errors_count, duration))
        conn.commit()
    finally:
        conn.close()


def get_latest_weather(city_name=None):
    """جيب أحدث بيانات الطقس"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if city_name:
            cursor.execute('''
                SELECT c.city_name, c.country, w.*
                FROM weather_data w
                JOIN cities c ON w.city_id = c.city_id
                WHERE c.city_name = ?
                ORDER BY w.timestamp DESC LIMIT 1
            ''', (city_name,))
            return cursor.fetchone()
        else:
            cursor.execute('''
                SELECT c.city_name, c.country, w.*
                FROM weather_data w
                JOIN cities c ON w.city_id = c.city_id
                WHERE w.timestamp = (
                    SELECT MAX(timestamp) FROM weather_data w2
                    WHERE w2.city_id = w.city_id
                )
                ORDER BY c.city_name
            ''')
            return cursor.fetchall()
    finally:
        conn.close()


def get_weather_history(city_name, days=7):
    """جيب تاريخ الطقس لمدينة"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT c.city_name, w.*
            FROM weather_data w
            JOIN cities c ON w.city_id = c.city_id
            WHERE c.city_name = ?
            AND w.timestamp >= datetime('now', ? || ' days')
            ORDER BY w.timestamp DESC
        ''', (city_name, f'-{days}'))
        return cursor.fetchall()
    finally:
        conn.close()


def get_stats(city_name, days=30):
    """إحصائيات الطقس لمدينة"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT
                c.city_name,
                COUNT(*) as total_records,
                ROUND(AVG(w.temperature_c), 1) as avg_temp,
                ROUND(MAX(w.temperature_c), 1) as max_temp,
                ROUND(MIN(w.temperature_c), 1) as min_temp,
                ROUND(AVG(w.humidity), 1) as avg_humidity,
                ROUND(AVG(w.wind_speed_mps), 1) as avg_wind
            FROM weather_data w
            JOIN cities c ON w.city_id = c.city_id
            WHERE c.city_name = ?
            AND w.timestamp >= datetime('now', ? || ' days')
        ''', (city_name, f'-{days}'))
        return cursor.fetchone()
    finally:
        conn.close()
