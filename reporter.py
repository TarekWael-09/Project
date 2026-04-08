# reporter.py - التقارير والتحليلات
import os
import logging
from datetime import datetime
from database import get_latest_weather, get_stats, get_connection
from config import REPORTS_DIR

logger = logging.getLogger(__name__)


def get_current_weather_report():
    """تقرير الطقس الحالي لكل المدن"""
    rows = get_latest_weather()
    if not rows:
        return "❌ مفيش بيانات في قاعدة البيانات"

    lines = []
    lines.append("=" * 60)
    lines.append(f"🌍 تقرير الطقس الحالي - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)

    for row in rows:
        lines.append(f"\n🏙️  {row['city_name']}, {row['country']}")
        lines.append(f"   🌡️  درجة الحرارة : {row['temperature_c']}°C (الإحساس: {row['feels_like_c']}°C)")
        lines.append(f"   💧 الرطوبة      : {row['humidity']}%")
        lines.append(f"   🌬️  الرياح       : {row['wind_speed_mps']} م/ث")
        lines.append(f"   ☁️  الحالة       : {row['weather_desc']}")
        lines.append(f"   📅 آخر تحديث   : {row['timestamp']}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def get_stats_report(days=7):
    """تقرير إحصائيات لكل المدن"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT city_name FROM cities ORDER BY city_name")
    cities = [row['city_name'] for row in cursor.fetchall()]
    conn.close()

    if not cities:
        return "❌ مفيش مدن في قاعدة البيانات"

    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 إحصائيات {days} أيام الأخيرة - {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("=" * 60)
    lines.append(f"{'المدينة':<15} {'متوسط':<8} {'أعلى':<8} {'أدنى':<8} {'رطوبة':<8} {'سجلات'}")
    lines.append("-" * 60)

    for city in cities:
        stats = get_stats(city, days)
        if stats and stats['total_records'] > 0:
            lines.append(
                f"{city:<15} {stats['avg_temp']:<8} {stats['max_temp']:<8} "
                f"{stats['min_temp']:<8} {stats['avg_humidity']:<8} {stats['total_records']}"
            )

    lines.append("=" * 60)
    return "\n".join(lines)


def get_alerts_report():
    """تقرير التنبيهات الأخيرة"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.alert_type, a.alert_msg, a.value, a.threshold, a.created_at, c.city_name
        FROM alerts a
        JOIN cities c ON a.city_id = c.city_id
        ORDER BY a.created_at DESC
        LIMIT 20
    ''')
    alerts = cursor.fetchall()
    conn.close()

    if not alerts:
        return "✅ مفيش تنبيهات حالياً"

    lines = []
    lines.append("=" * 60)
    lines.append(f"🚨 التنبيهات الأخيرة")
    lines.append("=" * 60)

    for alert in alerts:
        lines.append(f"\n⚠️  {alert['alert_msg']}")
        lines.append(f"   📅 {alert['created_at']}")

    lines.append("=" * 60)
    return "\n".join(lines)


def get_hottest_cities():
    """أعلى المدن حرارة"""
    rows = get_latest_weather()
    if not rows:
        return []

    sorted_cities = sorted(rows, key=lambda x: x['temperature_c'] or -999, reverse=True)
    return sorted_cities


def save_report_to_file(content, filename=None):
    """حفظ التقرير في ملف"""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not filename:
        filename = f"weather_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"📄 تم حفظ التقرير: {filepath}")
    return filepath


def generate_full_report():
    """تقرير شامل كامل"""
    report_parts = []
    report_parts.append(get_current_weather_report())
    report_parts.append("\n\n")
    report_parts.append(get_stats_report(days=7))
    report_parts.append("\n\n")
    report_parts.append(get_alerts_report())

    full_report = "\n".join(report_parts)

    # حفظ في ملف
    filepath = save_report_to_file(full_report)

    return full_report, filepath
