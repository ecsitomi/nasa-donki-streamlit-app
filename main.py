import streamlit as st
from nasa_api import get_date_range, fetch_cme_events, fetch_flr_events, fetch_gst_events
import pandas as pd
import altair as alt
from collections import Counter
from datetime import datetime, timedelta

# Események formázása
def render_item(key, value, level=0):
    indent = " " * level  # unicode spacing
    if isinstance(value, dict):
        for subkey, subval in value.items():
            render_item(subkey, subval, level+1)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            if isinstance(item, dict):
                st.write(f"{indent}🔹 {key} [{i+1}]")
                for subkey, subval in item.items():
                    render_item(subkey, subval, level+1)
            else:
                st.write(f"{indent}• {key}: {item}")
    else:
        if "link" in key.lower() and isinstance(value, str):
            st.markdown(f"{indent}**{key}:** [🔗 Link]({value})")
        else:
            st.write(f"{indent}**{key}:** {value}")


def get_event_time(event):
    return event.get("startTime") or event.get("peakTime") or ""

st.set_page_config(page_title="NASA Space Weather Dashboard", layout="wide")
st.title("☀️ NASA Space Weather Dashboard")

st.sidebar.header("Filters")

# Nap választó (időtáv)
days = st.sidebar.slider("Show events from the past ... days", min_value=1, max_value=365, value=30)
start_date, end_date = get_date_range(days)

# Eseménytípus-választó
event_type = st.sidebar.selectbox("Select Event Type", ["CME", "FLR", "GST"])

st.caption(f"Showing **{event_type}** events from **{start_date}** to **{end_date}**")

# Események lekérése
with st.spinner(f"Fetching {event_type} events..."):
    if event_type == "CME":
        events = fetch_cme_events(start_date, end_date)
    elif event_type == "FLR":
        events = fetch_flr_events(start_date, end_date)
    elif event_type == "GST":
        events = fetch_gst_events(start_date, end_date)
    else:
        events = []

# 🌍 Predicted Impacts in Sidebar
impacts_summary = []

for event in events:
    analyses = event.get("cmeAnalyses", [])
    for analysis in analyses:
        enlil_list = analysis.get("enlilList", [])
        for sim in enlil_list:
            if isinstance(sim, dict):
                impact_list = sim.get("impactList")
                if isinstance(impact_list, list):
                    for impact in impact_list:
                        location = impact.get("location")
                        arrival = impact.get("arrivalTime", "N/A")
                        if location:
                            impacts_summary.append({
                                "location": location,
                                "arrival": arrival,
                                "eventID": event.get("activityID", "N/A")
                            })

if impacts_summary:
    with st.sidebar.expander("🪐 Predicted Impacts"):
        for impact in impacts_summary:
            if impact["location"] == "Earth":
                st.error(f"🌍 Earth: {impact['arrival']}")
            else:
                st.warning(f"🪐 {impact['location']}: {impact['arrival']}")
else:
    with st.sidebar.expander("🪐 Predicted Impacts"):
        st.info("No predicted planetary impacts found.")

# Megjelenítés
if not events:
    st.warning(f"No {event_type} events found.")
else:
    # 📊 Grafikon: teljes naplista, még ha 0 esemény is van
    date_range = pd.date_range(start=start_date, end=end_date)

    event_dates = []
    for e in events:
        date_str = e.get("startTime") or e.get("peakTime") or ""
        if date_str:
            event_dates.append(date_str[:10])

    event_counts = Counter(event_dates)

    data = {
        "Date": [d.strftime("%Y-%m-%d") for d in date_range],
        "Count": [event_counts.get(d.strftime("%Y-%m-%d"), 0) for d in date_range]
    }

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])  # dátum formázás
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")  # string formátum (év-hónap-nap)

    st.subheader("📊 Event Distribution Over Time")
    chart = alt.Chart(df).mark_bar(size=20).encode(
        x=alt.X("Date:N",  # N = nominal, azaz minden nap külön kategória
                title="Date",
                sort=None,
                axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Count:Q", title=f"{event_type} Events"),
        tooltip=["Date", "Count"]
    ).properties(width=days * 20, height=300)

    st.altair_chart(chart, use_container_width=True)

    # 📡 Események részletes listája
    sorted_events = sorted(events, key=get_event_time, reverse=True)
    for idx, event in enumerate(sorted_events):
        activity_id = event.get("activityID", "N/A")
        short_id = activity_id.split("-CME-001")[0] if isinstance(activity_id, str) else "N/A"
        with st.expander(f"📡 {event_type} #{idx+1} – {short_id}"):
            for key, value in event.items():
                render_item(key, value)
