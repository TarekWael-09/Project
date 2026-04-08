# validator.py - التحقق من جودة البيانات
import logging

logger = logging.getLogger(__name__)

# حدود منطقية للبيانات
VALID_RANGES = {
    'temperature': (-80, 60),
    'humidity':    (0, 100),
    'pressure':    (870, 1085),
    'wind_speed':  (0, 113),
    'cloudiness':  (0, 100),
}


def validate_weather_data(data):
    """تحقق من صحة بيانات الطقس - يرجع (is_valid, errors)"""
    errors = []

    if not data:
        return False, ["البيانات فاضية"]

    # تحقق من الحقول المطلوبة
    required_fields = ['city', 'country', 'temperature', 'humidity', 'pressure']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"الحقل '{field}' ناقص")

    if errors:
        return False, errors

    # تحقق من النطاقات المنطقية
    checks = {
        'temperature': data.get('temperature'),
        'humidity':    data.get('humidity'),
        'pressure':    data.get('pressure'),
        'wind_speed':  data.get('wind_speed'),
        'cloudiness':  data.get('cloudiness'),
    }

    for field, value in checks.items():
        if value is not None and field in VALID_RANGES:
            min_val, max_val = VALID_RANGES[field]
            if not (min_val <= value <= max_val):
                errors.append(f"قيمة '{field}' = {value} خارج النطاق المنطقي ({min_val} → {max_val})")

    # تحقق من اسم المدينة
    if data.get('city') and len(data['city']) < 2:
        errors.append("اسم المدينة قصير جداً")

    is_valid = len(errors) == 0

    if not is_valid:
        logger.warning(f"⚠️ بيانات {data.get('city', 'Unknown')} فيها مشاكل: {errors}")
    
    return is_valid, errors


def validate_batch(weather_list):
    """تحقق من دفعة بيانات كاملة"""
    valid = []
    invalid = []

    for data in weather_list:
        is_valid, errors = validate_weather_data(data)
        if is_valid:
            valid.append(data)
        else:
            invalid.append({'data': data, 'errors': errors})

    total = len(weather_list)
    logger.info(f"📋 نتيجة التحقق: {len(valid)}/{total} صحيحة")
    
    return valid, invalid


def check_data_quality(weather_list):
    """تقرير جودة البيانات"""
    if not weather_list:
        return {}

    total = len(weather_list)
    
    report = {
        'total_records': total,
        'complete_records': 0,
        'missing_fields': {},
        'out_of_range': {},
        'quality_score': 0
    }

    for data in weather_list:
        # عد الحقول الناقصة
        for field in ['temperature', 'humidity', 'pressure', 'wind_speed', 'visibility']:
            if data.get(field) is None:
                report['missing_fields'][field] = report['missing_fields'].get(field, 0) + 1

        # عد القيم خارج النطاق
        for field, (min_v, max_v) in VALID_RANGES.items():
            val = data.get(field)
            if val is not None and not (min_v <= val <= max_v):
                report['out_of_range'][field] = report['out_of_range'].get(field, 0) + 1

        # عد السجلات الكاملة
        if not any(data.get(f) is None for f in ['temperature', 'humidity', 'pressure']):
            report['complete_records'] += 1

    # احسب نقطة الجودة
    report['quality_score'] = round((report['complete_records'] / total) * 100, 1)
    
    return report
