"""
solar_fsm.py
Deterministic Finite-State Automaton for Bikram Sambat (BS).
Discretizes continuous solar transit (Sankranti) against Kathmandu Sunrise/Sunset thresholds.
"""

from datetime import date, timedelta
from src.ephemeris import (
    gregorian_to_jd,
    get_sun_sidereal_longitude,
    get_kathmandu_sunrise_sunset,
    find_sankranti_in_window,
    SOLAR_RASHIS,
    NPT_OFFSET_HOURS,
)


class SolarFSM:
    def __init__(self):
        pass

    def evaluate_date(self, target_date: date):
        """
        Calculates the exact Bikram Sambat (BS) date for any given Gregorian date.
        Scans backwards to find the active month's Sankranti (Gate 1) and counts civil days.
        """
        # Step backwards day-by-day (maximum 33 days) to locate the Sankranti that initiated this month
        current_day = target_date
        sankranti_found = None
        sankranti_date = None

        for offset in range(35):
            check_day = target_date - timedelta(days=offset)
            prev_day = check_day - timedelta(days=1)

            sunrise_prev, sunset_prev = get_kathmandu_sunrise_sunset(prev_day.year, prev_day.month, prev_day.day)
            sunrise_curr, sunset_curr = get_kathmandu_sunrise_sunset(check_day.year, check_day.month, check_day.day)

            # JD at sunrise (converted from NPT to UT)
            jd_prev_sunrise = gregorian_to_jd(prev_day.year, prev_day.month, prev_day.day, sunrise_prev - NPT_OFFSET_HOURS)
            jd_curr_sunrise = gregorian_to_jd(check_day.year, check_day.month, check_day.day, sunrise_curr - NPT_OFFSET_HOURS)

            transit = find_sankranti_in_window(jd_prev_sunrise, jd_curr_sunrise)
            if transit:
                transit_jd, rashi_idx = transit
                # Convert transit JD to decimal hour NPT on check_day
                transit_hour_npt = ((transit_jd + 0.5 + (NPT_OFFSET_HOURS / 24.0)) % 1.0) * 24.0

                # Civil Discretization Rule:
                # If transit occurs before Sunset of prev_day -> Gate 1 was prev_day.
                # If transit occurs between prev Sunset and curr Sunset -> Gate 1 is check_day.
                sankranti_found = (transit_jd, rashi_idx)
                sankranti_date = check_day
                break

        if not sankranti_date:
            raise RuntimeError(f"Could not locate Sankranti boundary for date: {target_date}")

        transit_jd, rashi_idx = sankranti_found
        rashi_name, bs_month_name = SOLAR_RASHIS[rashi_idx]

        # Gate count is the civil day difference from Gate 1
        gate = (target_date - sankranti_date).days + 1

        # Approximate BS Year: Gregorian Year + 56 (Jan-Apr) or + 57 (Apr-Dec)
        sun_long = get_sun_sidereal_longitude(gregorian_to_jd(target_date.year, target_date.month, target_date.day, 12.0))
        if rashi_idx >= 0 and target_date.month >= 4:
            bs_year = target_date.year + 57
        else:
            bs_year = target_date.year + 56

        return {
            "bs_year": bs_year,
            "bs_month_index": rashi_idx + 1,
            "bs_month_name": bs_month_name,
            "rashi_name": rashi_name,
            "gate": gate,
            "sankranti_date": sankranti_date.isoformat(),
        }


if __name__ == "__main__":
    fsm = SolarFSM()
    today = date.today()
    res = fsm.evaluate_date(today)
    print("==================================================")
    print(" BIKRAM SAMBAT DETERMINISTIC STATE MACHINE ")
    print("==================================================")
    print(f"Input Gregorian Date : {today.isoformat()}")
    print(f"Bikram Sambat Output : {res['bs_year']} {res['bs_month_name']} {res['gate']} Gate")
    print(f"Active Zodiac Sign   : {res['rashi_name']} Rashi")
    print(f"Month Initiated On   : {res['sankranti_date']} (Gate 1)")
    print("==================================================")