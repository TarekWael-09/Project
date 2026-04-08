# etl_pipeline.py - الـ ETL Pipeline الرئيسي
import logging
import time
from datetime import datetime

from api_client import fetch_all_cities
from database import insert_city, insert_weather, insert_alert, log_pipeline_run
from validator import validate_batch, check_data_quality
from config import CITIES, ALERTS

logger = logging.getLogger(__name__)


# ===== EXTRACT =====
def extract(cities=None):
    """استخراج البيانات من API"""
    logger.info("=" * 50)
    logger.info("🔄 مرحلة EXTRACT - جلب البيانات من API")
    logger.info("=" * 50)

    target_cities = cities or CITIES
    raw_data, errors = fetch_all_cities(target_cities)
    
    logger.info(f"✅ تم جلب {len(raw_data)} مدينة بنجاح")
    return raw_data, errors


# ===== TRANSFORM =====
def transform(raw_data):
    """تنظيف وتحويل البيانات"""
    logger.info("\n" + "=" * 50)
    logger.info("🔄 مرحلة TRANSFORM - تنظيف البيانات")
    logger.info("=" * 50)

    # تحقق من صحة البيانات
    valid_data, invalid_data = validate_batch(raw_data)

    if invalid_data:
        logger.warning(f"⚠️ {len(invalid_data)} سجل فيها مشاكل:")
        for item in invalid_data:
            city = item['data'].get('city', 'Unknown')
            logger.warning(f"   - {city}: {item['errors']}")

    # تقرير الجودة
    quality = check_data_quality(valid_data)
    logger.info(f"📊 نقطة الجودة: {quality.get('quality_score', 0)}%")

    # تحويل وتنظيف البيانات
    transformed = []
    for data in valid_data:
        cleaned = {
            'city':        data['city'].strip(),
            'country':     data.get('country', 'Unknown'),
            'latitude':    round(data.get('latitude', 0), 4),
            'longitude':   round(data.get('longitude', 0), 4),
            'temperature': round(data['temperature'], 1),
            'feels_like':  round(data.get('feels_like', data['temperature']), 1),
            'humidity':    int(data['humidity']),
            'pressure':    round(data.get('pressure', 1013), 1),
            'wind_speed':  round(data.get('wind_speed', 0), 1),
            'wind_direction': int(data.get('wind_direction', 0)),
            'condition':   data.get('condition', 'Unknown'),
            'description': data.get('description', '').capitalize(),
            'visibility':  int(data.get('visibility', 0)),
            'cloudiness':  int(data.get('cloudiness', 0)),
        }
        transformed.append(cleaned)

    logger.info(f"✅ تم تحويل {len(transformed)} سجل")
    return transformed


# ===== LOAD =====
def load(transformed_data):
    """تحميل البيانات لقاعدة البيانات"""
    logger.info("\n" + "=" * 50)
    logger.info("🔄 مرحلة LOAD - حفظ في قاعدة البيانات")
    logger.info("=" * 50)

    saved = 0
    alerts_triggered = 0

    for data in transformed_data:
        # إضافة/جلب المدينة
        city_id = insert_city(
            data['city'],
            data['country'],
            data['latitude'],
            data['longitude']
        )

        if city_id is None:
            logger.error(f"❌ فشل في حفظ مدينة: {data['city']}")
            continue

        # حفظ بيانات الطقس
        record_id = insert_weather(city_id, data)
        if record_id:
            saved += 1
            logger.info(f"💾 حُفظ: {data['city']} → {data['temperature']}°C, {data['description']}")

        # فحص التنبيهات
        alerts = check_alerts(city_id, data)
        alerts_triggered += len(alerts)

    logger.info(f"\n✅ تم حفظ {saved} سجل")
    if alerts_triggered:
        logger.warning(f"🚨 {alerts_triggered} تنبيه تم إطلاقه")

    return saved


def check_alerts(city_id, data):
    """فحص وحفظ التنبيهات"""
    alerts = []
    city = data['city']
    temp = data['temperature']
    humidity = data['humidity']
    wind = data['wind_speed']

    # تنبيه حرارة مرتفعة
    if temp > ALERTS['high_temp']:
        msg = f"🌡️ حرارة مرتفعة في {city}: {temp}°C (الحد: {ALERTS['high_temp']}°C)"
        logger.warning(msg)
        insert_alert(city_id, "HIGH_TEMP", msg, temp, ALERTS['high_temp'])
        alerts.append(msg)

    # تنبيه حرارة منخفضة
    if temp < ALERTS['low_temp']:
        msg = f"🥶 حرارة منخفضة جداً في {city}: {temp}°C (الحد: {ALERTS['low_temp']}°C)"
        logger.warning(msg)
        insert_alert(city_id, "LOW_TEMP", msg, temp, ALERTS['low_temp'])
        alerts.append(msg)

    # تنبيه رطوبة مرتفعة
    if humidity > ALERTS['high_humidity']:
        msg = f"💧 رطوبة مرتفعة جداً في {city}: {humidity}% (الحد: {ALERTS['high_humidity']}%)"
        logger.warning(msg)
        insert_alert(city_id, "HIGH_HUMIDITY", msg, humidity, ALERTS['high_humidity'])
        alerts.append(msg)

    # تنبيه رياح قوية
    if wind > ALERTS['high_wind']:
        msg = f"💨 رياح قوية في {city}: {wind} م/ث (الحد: {ALERTS['high_wind']} م/ث)"
        logger.warning(msg)
        insert_alert(city_id, "HIGH_WIND", msg, wind, ALERTS['high_wind'])
        alerts.append(msg)

    return alerts


# ===== RUN FULL PIPELINE =====
def run_pipeline(cities=None):
    """تشغيل الـ Pipeline كامل"""
    start_time = time.time()
    logger.info(f"\n🚀 بدء تشغيل Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Extract
        raw_data, errors = extract(cities)

        if not raw_data:
            logger.error("❌ مفيش بيانات اتجلبت، تأكد من الـ API Key")
            log_pipeline_run("FAILED", 0, 0, len(errors), time.time() - start_time)
            return False

        # Transform
        transformed = transform(raw_data)

        if not transformed:
            logger.error("❌ مفيش بيانات صالحة بعد التحقق")
            log_pipeline_run("FAILED", len(raw_data), 0, len(errors), time.time() - start_time)
            return False

        # Load
        saved = load(transformed)

        # سجّل نتيجة التشغيل
        duration = round(time.time() - start_time, 2)
        log_pipeline_run("SUCCESS", len(raw_data), saved, len(errors), duration)

        logger.info(f"\n🎉 Pipeline انتهى بنجاح في {duration} ثانية")
        logger.info(f"📊 ملخص: {len(raw_data)} مدينة → {saved} سجل محفوظ")
        return True

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        logger.error(f"💥 خطأ في الـ Pipeline: {e}", exc_info=True)
        log_pipeline_run("ERROR", 0, 0, 1, duration)
        return False
