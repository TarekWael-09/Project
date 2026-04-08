# main.py - نقطة الدخول الرئيسية
import sys
import os
import logging

# إضافة المجلد الحالي للـ path
sys.path.insert(0, os.path.dirname(__file__))

from database import setup_database
from etl_pipeline import run_pipeline
from reporter import get_current_weather_report, get_stats_report, get_alerts_report, generate_full_report
from monitor import print_health_report
from scheduler import start_scheduler
from config import LOG_DIR, LOG_FILE


def setup_logging():
    """إعداد نظام الـ Logging"""
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_menu():
    """اطبع القائمة الرئيسية"""
    print("\n" + "=" * 50)
    print("🌤️  Weather Data Pipeline System")
    print("=" * 50)
    print("1. تشغيل Pipeline مرة واحدة")
    print("2. عرض الطقس الحالي لكل المدن")
    print("3. عرض الإحصائيات (7 أيام)")
    print("4. عرض التنبيهات")
    print("5. توليد تقرير شامل")
    print("6. فحص صحة النظام")
    print("7. بدء الجدولة التلقائية (كل 30 دقيقة)")
    print("0. خروج")
    print("=" * 50)


def main():
    """الدالة الرئيسية"""
    setup_logging()
    logger = logging.getLogger(__name__)

    # إعداد قاعدة البيانات
    logger.info("🔧 إعداد قاعدة البيانات...")
    setup_database()

    # تشغيل مباشر من command line
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "run":
            run_pipeline()
        elif command == "report":
            report, filepath = generate_full_report()
            print(report)
        elif command == "monitor":
            print_health_report()
        elif command == "schedule":
            start_scheduler()
        else:
            print(f"❌ أمر غير معروف: {command}")
            print("الأوامر المتاحة: run, report, monitor, schedule")
        return

    # القائمة التفاعلية
    while True:
        print_menu()
        choice = input("\nاختر رقم: ").strip()

        if choice == "1":
            run_pipeline()

        elif choice == "2":
            print(get_current_weather_report())

        elif choice == "3":
            print(get_stats_report(days=7))

        elif choice == "4":
            print(get_alerts_report())

        elif choice == "5":
            print("⏳ جاري توليد التقرير...")
            report, filepath = generate_full_report()
            print(report)
            print(f"\n✅ تم الحفظ في: {filepath}")

        elif choice == "6":
            print_health_report()

        elif choice == "7":
            print("⚠️ هيشتغل في الخلفية - اضغط Ctrl+C للإيقاف")
            start_scheduler()

        elif choice == "0":
            print("\n👋 مع السلامة!")
            break

        else:
            print("❌ اختيار غير صحيح، حاول تاني")

        input("\n[اضغط Enter للمتابعة...]")


if __name__ == "__main__":
    main()
