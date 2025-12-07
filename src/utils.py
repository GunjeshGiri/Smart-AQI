# src/utils.py
import pandas as pd

def compute_aqi_from_pm25(pm25_value):
    # Placeholder: use CPCB / WHO breakpoints in production
    if pm25_value <= 30:
        return 0, 'Good'
    elif pm25_value <= 60:
        return 1, 'Satisfactory'
    elif pm25_value <= 90:
        return 2, 'Moderate'
    elif pm25_value <= 120:
        return 3, 'Poor'
    else:
        return 4, 'Very Poor'
