# api_client.py - التعامل مع OpenWeatherMap API
import requests
import logging
from config import API_KEY, BASE_URL, UNITS

logger = logging.getLogger(__name__)


def fetch_weather(city):
    """جيب بيانات الطقس لمدينة معينة"""
    params = {
        'q': city,
        'appid': API_KEY,
        'units': UNITS
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        raw = response.json()
        return parse_weather(raw)

    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            logger.error(f"❌ API Key غلط أو مش متفعّل بعد")
        elif response.status_code == 404:
            logger.error(f"❌ المدينة '{city}' مش موجودة")
        else:
            logger.error(f"❌ HTTP Error لـ {city}: {e}")
        return None

    except requests.exceptions.ConnectionError:
        logger.error(f"❌ مفيش إنترنت")
        return None

    except requests.exceptions.Timeout:
        logger.error(f"❌ الـ API بطيء، حاول تاني")
        return None

    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع لـ {city}: {e}")
        return None


def parse_weather(raw):
    """تحويل الـ JSON لـ dictionary مرتب"""
    try:
        return {
            'city':        raw['name'],
            'country':     raw['sys']['country'],
            'latitude':    raw['coord']['lat'],
            'longitude':   raw['coord']['lon'],
            'temperature': raw['main']['temp'],
            'feels_like':  raw['main']['feels_like'],
            'humidity':    raw['main']['humidity'],
            'pressure':    raw['main']['pressure'],
            'wind_speed':  raw['wind']['speed'],
            'wind_direction': raw['wind'].get('deg', 0),
            'condition':   raw['weather'][0]['main'],
            'description': raw['weather'][0]['description'],
            'visibility':  raw.get('visibility', 0),
            'cloudiness':  raw['clouds']['all'],
        }
    except KeyError as e:
        logger.error(f"❌ خطأ في تحليل البيانات: {e}")
        return None


def fetch_all_cities(cities):
    """جيب بيانات كل المدن"""
    results = []
    errors = []

    for city in cities:
        logger.info(f"⏳ جاري جلب بيانات {city}...")
        data = fetch_weather(city)
        if data:
            results.append(data)
            logger.info(f"✅ {city}: {data['temperature']}°C, {data['description']}")
        else:
            errors.append(city)

    logger.info(f"\n📊 النتيجة: {len(results)} نجحت، {len(errors)} فشلت")
    if errors:
        logger.warning(f"⚠️ المدن اللي فشلت: {', '.join(errors)}")

    return results, errors
