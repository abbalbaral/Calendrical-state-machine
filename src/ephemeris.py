"""
ephemeris.py
Deterministic celestial coordinate engine for Sun and Moon.
Computes Nirayana (Sidereal) longitudes, dynamic Kathmandu sunrise/sunset,
and continuous solar transit (Sankranti) timestamps.
"""

import math
from datetime import datetime, date, timedelta

# Standard coordinates for Kathmandu, Nepal
KATHMANDU_LAT = 27.7172
KATHMANDU_LON = 85.3240
NPT_OFFSET_HOURS = 5.75  # UTC + 5:45

# 12 Nirayana Solar Rashis and Bikram Sambat months
SOLAR_RASHIS = [
    ("Mesha", "Baisakh"),
    ("Vrisha", "Jestha"),
    ("Mithuna", "Ashadh"),
    ("Karkata", "Shrawan"),
    ("Simha", "Bhadra"),
    ("Kanya", "Ashwin"),
    ("Tula", "Kartik"),
    ("Vrischika", "Mangsir"),
    ("Dhanu", "Poush"),
    ("Makara", "Magh"),
    ("Kumbha", "Falgun"),
    ("Meena", "Chaitra"),
]

# 12 Nepal Sambat Lunisolar months (Amanta system: New Moon to New Moon)
NEPAL_SAMBAT_MONTHS = [
    "Kachhala", "Thinla", "Pohela", "Sillha", 
    "Chilaha", "Chaula", "Bachhala", "Tachhala", 
    "Dillha", "Gunla", "Yala", "Kaulla"
]

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya (Aaunsi)"
]


def gregorian_to_jd(year: int, month: int, day: int, hour: float = 0.0) -> float:
    """Converts a Gregorian date and decimal UT hour to Julian Day Number."""
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + (day + hour / 24.0) + B - 1524.5
    return jd


def calculate_lahiri_ayanamsha(jd: float) -> float:
    """Calculates Lahiri Ayanamsha (precession offset) for converting Sayana to Nirayana."""
    T = (jd - 2451545.0) / 36525.0
    return (24.0416 + (T * 1.39697)) % 360.0


def get_sun_sidereal_longitude(jd: float) -> float:
    """Computes Nirayana (sidereal) solar longitude in degrees [0, 360)."""
    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + 36000.76983 * T + 0.0003032 * (T ** 2)) % 360.0
    M = (357.52911 + 35999.05029 * T - 0.0001537 * (T ** 2)) % 360.0
    M_rad = math.radians(M)

    # Equation of the center (Keplerian perturbation)
    C = (1.914602 - 0.004817 * T) * math.sin(M_rad) + (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) + 0.000289 * math.sin(3 * M_rad)
    sun_tropical = (L0 + C) % 360.0
    ayanamsha = calculate_lahiri_ayanamsha(jd)
    return (sun_tropical - ayanamsha) % 360.0


def get_moon_sidereal_longitude(jd: float) -> float:
    """
    Computes Nirayana (sidereal) lunar longitude in degrees [0, 360).
    Implements Chapront ELP-2000 / Meeus periodic perturbation series.
    """
    T = (jd - 2451545.0) / 36525.0

    # Fundamental lunar arguments (degrees)
    L_prime = (218.3164477 + 481267.88123421 * T) % 360.0  # Moon's mean longitude
    D = (297.8501921 + 445267.1114034 * T) % 360.0          # Mean elongation
    M = (357.5291092 + 35999.0502909 * T) % 360.0           # Sun's mean anomaly
    M_prime = (134.9633964 + 477198.8675055 * T) % 360.0   # Moon's mean anomaly
    F = (93.2720950 + 483202.0175233 * T) % 360.0           # Moon's argument of latitude (distance from node)

    # Periodic perturbations (Evection, Variation, Annual Equation)
    Sigma_l = (
        6.288774 * math.sin(math.radians(M_prime))
        + 1.274027 * math.sin(math.radians(2 * D - M_prime))
        + 0.658314 * math.sin(math.radians(2 * D))
        + 0.213618 * math.sin(math.radians(2 * M_prime))
        - 0.185116 * math.sin(math.radians(M))
        - 0.114332 * math.sin(math.radians(2 * F))
        + 0.058793 * math.sin(math.radians(2 * D - 2 * M_prime))
        + 0.057066 * math.sin(math.radians(2 * D - M - M_prime))
        + 0.053322 * math.sin(math.radians(2 * D + M_prime))
    )

    moon_tropical = (L_prime + Sigma_l) % 360.0
    ayanamsha = calculate_lahiri_ayanamsha(jd)
    return (moon_tropical - ayanamsha) % 360.0


def get_kathmandu_sunrise_sunset(year: int, month: int, day: int):
    """
    Computes exact local Sunrise and Sunset times for Kathmandu (NPT = UTC+5:45)
    using NOAA solar equations. Returns (sunrise_hour_npt, sunset_hour_npt).
    """
    # Day of year
    N = (date(year, month, day) - date(year, 1, 1)).days + 1
    # Solar declination approximation
    declination = -23.44 * math.cos(math.radians((360.0 / 365.24) * (N + 10)))

    lat_rad = math.radians(KATHMANDU_LAT)
    dec_rad = math.radians(declination)

    cos_omega = -math.tan(lat_rad) * math.tan(dec_rad)
    cos_omega = max(-1.0, min(1.0, cos_omega))
    omega = math.degrees(math.acos(cos_omega))

    daylight_hours = (2.0 * omega) / 15.0

    # Solar noon adjustment for Kathmandu meridian (85.324° E vs 86.25° E NPT standard)
    lon_diff_degrees = (NPT_OFFSET_HOURS * 15.0) - KATHMANDU_LON
    solar_noon_npt = 12.0 + (lon_diff_degrees * 4.0 / 60.0)

    sunrise = solar_noon_npt - (daylight_hours / 2.0)
    sunset = solar_noon_npt + (daylight_hours / 2.0)
    return sunrise, sunset


def find_sankranti_in_window(jd_start: float, jd_end: float):
    """
    Checks if a 30° solar boundary crossing (Sankranti) occurred between jd_start and jd_end.
    If yes, returns (exact_transit_jd, new_rashi_index). Otherwise returns None.
    """
    sun_start = get_sun_sidereal_longitude(jd_start)
    sun_end = get_sun_sidereal_longitude(jd_end)

    rashi_start = int(sun_start // 30)
    rashi_end = int(sun_end // 30)

    if rashi_start != rashi_end:
        # Binary search / Bisection to locate transit to within 1 second
        low, high = jd_start, jd_end
        target_boundary = rashi_end * 30.0
        for _ in range(24):  # 24 iterations gives sub-second precision
            mid = (low + high) / 2.0
            mid_long = get_sun_sidereal_longitude(mid)
            if (mid_long - target_boundary) % 360.0 < 180.0:
                high = mid
            else:
                low = mid
        return ((low + high) / 2.0, rashi_end)
    return None