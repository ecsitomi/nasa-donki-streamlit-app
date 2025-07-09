import requests
from datetime import datetime, timedelta
import streamlit as st

API_KEY = st.secrets["NASA_API_KEY"]
BASE_URL = "https://api.nasa.gov/DONKI"

def get_date_range(days=7):
    end = datetime.utcnow().date()
    start = end - timedelta(days=days - 1)
    return start, end  # visszatér datetime.date objektumokkal

def fetch_cme_events(start_date, end_date):
    return _fetch_events("CME", start_date, end_date)

def fetch_flr_events(start_date, end_date):
    return _fetch_events("FLR", start_date, end_date)

def fetch_gst_events(start_date, end_date):
    return _fetch_events("GST", start_date, end_date)

def _fetch_events(event_type, start_date, end_date):
    url = f"{BASE_URL}/{event_type}"
    params = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "api_key": API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print(f"Error fetching {event_type} events:", e)
        return []

