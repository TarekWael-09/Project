# scheduler.py - الجدولة التلقائية
import schedule
import time
import logging
from datetime import datetime
from etl_pipeline import run_pipeline
from reporter import generate_full_report
from monitor import print_health_report
from config import COLLECTION_INTERVAL_MINUTES

logger = logging.getLogger(__name__)


def job_collect_data():
    """مهمة جمع البيانات"""
    logger.info(f"\n⏰ تشغيل مجدول - {datetime.now().strftime('%H:%M:%S')}")
    run_pipeline()


def job_generate_report():
    """مهمة توليد التقارير"""
    logger.info(f"\n📄 توليد تقرير تلقائي - {datetime.now().strftime('%H:%M:%S')}")
    report, filepath = generate_full_report()
    logger.info(f"✅ التقرير محفوظ: {filepath}")


def job_health_check():
    """مهمة فحص صحة النظام"""
    print_health_report()


def start_scheduler():
    """ابدأ الـ Scheduler"""
    logger.info("⏰ بدء الجدولة التلقائية...")
    logger.info(f"   - جمع البيانات كل {COLLECTION_INTERVAL_MINUTES} دقيقة")
    logger.info(f"   - تقرير يومي الساعة 8 صباحاً")
    logger.info(f"   - فحص صحة النظام كل ساعة")

    # جمع البيانات كل X دقيقة
    schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(job_collect_data)

    # تقرير يومي الساعة 8 صباحاً
    schedule.every().day.at("08:00").do(job_generate_report)

    # فحص صحة النظام كل ساعة
    schedule.every().hour.do(job_health_check)

    # شغّل أول مرة فوراً
    logger.info("🚀 تشغيل أول مرة الآن...")
    job_collect_data()

    # حلقة التشغيل
    logger.info("\n✅ الـ Scheduler شغّال - اضغط Ctrl+C للإيقاف\n")
    while True:
        schedule.run_pending()
        time.sleep(60)  # فحص كل دقيقة


def run_once():
    """تشغيل مرة واحدة بدون جدولة"""
    logger.info("▶️ تشغيل مرة واحدة...")
    return run_pipeline()
