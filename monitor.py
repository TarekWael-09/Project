# monitor.py - مراقبة صحة النظام
import os
import logging
from datetime import datetime, timedelta
from database import get_connection
from config import DB_PATH, LOG_FILE

logger = logging.getLogger(__name__)


def check_database_health():
    """تحقق من صحة قاعدة البيانات"""
    status = {"status": "OK", "issues": []}

    try:
        # تحقق من وجود الملف
        if not os.path.exists(DB_PATH):
            status["status"] = "WARNING"
            status["issues"].append("قاعدة البيانات مش موجودة بعد")
            return status

        # حجم الملف
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        status["db_size_mb"] = round(size_mb, 2)

        conn = get_connection()
        cursor = conn.cursor()

        # عدد السجلات
        cursor.execute("SELECT COUNT(*) as cnt FROM weather_data")
        status["total_records"] = cursor.fetchone()['cnt']

        # عدد المدن
        cursor.execute("SELECT COUNT(*) as cnt FROM cities")
        status["total_cities"] = cursor.fetchone()['cnt']

        # آخر تحديث
        cursor.execute("SELECT MAX(timestamp) as last FROM weather_data")
        row = cursor.fetchone()
        last_update = row['last'] if row else None
        status["last_update"] = last_update

        # تحقق لو البيانات قديمة (أكتر من ساعتين)
        if last_update:
            last_dt = datetime.fromisoformat(last_update)
            age_hours = (datetime.now() - last_dt).total_seconds() / 3600
            status["data_age_hours"] = round(age_hours, 1)

            if age_hours > 2:
                status["status"] = "WARNING"
                status["issues"].append(f"البيانات قديمة ({age_hours:.1f} ساعة)")
        else:
            status["status"] = "WARNING"
            status["issues"].append("مفيش بيانات في قاعدة البيانات")

        conn.close()

    except Exception as e:
        status["status"] = "ERROR"
        status["issues"].append(f"خطأ: {e}")

    return status


def check_pipeline_health():
    """تحقق من صحة الـ Pipeline"""
    status = {"status": "OK", "issues": []}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # آخر 10 تشغيلات
        cursor.execute('''
            SELECT status, run_time, cities_count, records_saved, errors_count, duration_sec
            FROM pipeline_runs
            ORDER BY run_time DESC
            LIMIT 10
        ''')
        runs = cursor.fetchall()
        conn.close()

        if not runs:
            status["status"] = "WARNING"
            status["issues"].append("مفيش تاريخ تشغيل")
            return status

        status["total_runs"] = len(runs)
        status["last_run"] = runs[0]['run_time']
        status["last_status"] = runs[0]['status']

        # احسب نسبة النجاح
        success_count = sum(1 for r in runs if r['status'] == 'SUCCESS')
        status["success_rate"] = round((success_count / len(runs)) * 100, 1)

        if status["success_rate"] < 70:
            status["status"] = "WARNING"
            status["issues"].append(f"نسبة النجاح منخفضة: {status['success_rate']}%")

        if runs[0]['status'] != 'SUCCESS':
            status["status"] = "WARNING"
            status["issues"].append(f"آخر تشغيل فشل: {runs[0]['status']}")

    except Exception as e:
        status["status"] = "ERROR"
        status["issues"].append(f"خطأ: {e}")

    return status


def get_system_health():
    """تقرير شامل لصحة النظام"""
    db_health = check_database_health()
    pipeline_health = check_pipeline_health()

    # تحديد الحالة الإجمالية
    overall = "OK"
    if db_health["status"] == "ERROR" or pipeline_health["status"] == "ERROR":
        overall = "ERROR"
    elif db_health["status"] == "WARNING" or pipeline_health["status"] == "WARNING":
        overall = "WARNING"

    return {
        "overall_status": overall,
        "timestamp": datetime.now().isoformat(),
        "database": db_health,
        "pipeline": pipeline_health,
    }


def print_health_report():
    """اطبع تقرير صحة النظام"""
    health = get_system_health()

    icons = {"OK": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(health["overall_status"], "❓")

    print("\n" + "=" * 50)
    print(f"🏥 تقرير صحة النظام - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    print(f"{icon} الحالة الإجمالية: {health['overall_status']}")

    print(f"\n📦 قاعدة البيانات:")
    db = health['database']
    print(f"   الحالة   : {icons.get(db['status'], '?')} {db['status']}")
    print(f"   السجلات  : {db.get('total_records', 'N/A')}")
    print(f"   المدن    : {db.get('total_cities', 'N/A')}")
    print(f"   الحجم    : {db.get('db_size_mb', 'N/A')} MB")
    print(f"   آخر بيانات: {db.get('data_age_hours', 'N/A')} ساعة")

    print(f"\n⚙️  الـ Pipeline:")
    pipe = health['pipeline']
    print(f"   الحالة       : {icons.get(pipe['status'], '?')} {pipe['status']}")
    print(f"   نسبة النجاح  : {pipe.get('success_rate', 'N/A')}%")
    print(f"   آخر تشغيل   : {pipe.get('last_run', 'N/A')}")

    # اطبع المشاكل لو فيه
    all_issues = db.get('issues', []) + pipe.get('issues', [])
    if all_issues:
        print(f"\n⚠️  المشاكل:")
        for issue in all_issues:
            print(f"   - {issue}")

    print("=" * 50)
    return health
