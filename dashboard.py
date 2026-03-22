import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

# Sets up the browser tab and layout
st.set_page_config(page_title="Soccer Pulse Tracker", layout="wide")

st.title("Live Match Pulse Tracker")

# Auto refresh every 10 seconds, need to replace in future due to frustrating position reset
st_autorefresh(interval=10000, key="refresh")

# These are empty slots on the website we will fill with data
metric_placeholder = st.empty()
chart_placeholder = st.empty()
keyword_placeholder = st.sidebar.empty()


def get_real_data():
    try:
        df = pd.read_csv('pulse_data.csv')
        df.columns = ['Minute', 'Buzz'] 
        return df
    except Exception as e:
        # Returns an empty dataframe if the file isn't ready yet
        return pd.DataFrame(columns=['Minute', 'Buzz'])


df = get_real_data()

if not df.empty and len(df) > 0:

    current_minute = df['Minute'].iloc[-1]
    current_buzz = df['Buzz'].iloc[-1]

    # Update Metrics in their own locked container
    with metric_placeholder.container():
        m_col1, m_col2 = st.columns(2)
        delta_val = int(current_buzz - df['Buzz'].iloc[-2]) if len(df) > 1 else 0
        m_col1.metric("Match Minute", f"{current_minute}'")
        m_col2.metric("Latest Buzz Score", current_buzz, delta=delta_val)

    # Update Chart in its placeholder
    with chart_placeholder.container():
        fig = px.area(df, x='Minute', y='Buzz', title="Match Momentum Pulse", color_discrete_sequence=['#ff4b4b']) 
        fig.update_layout(xaxis_title="Match Minute", yaxis_title="Social Volume", xaxis=dict(range=[0, 95]))
        st.plotly_chart(fig, use_container_width=True)

    # Update Sidebar in its placeholder
    with keyword_placeholder.container():
        st.write("### Trending Terms")
        trending = ["Haaland", "VAR", "Offside", "Ref", "Bangers Only"]
        st.pills("", trending, selection_mode="multi", disabled=True)
    
else:
    # What to show while waiting for the first minute of data
    with metric_placeholder.container():
        st.warning("Waiting for kickoff... The first data point will appear in 60 seconds.")
    with chart_placeholder.container():
        st.info("Check your terminal to ensure collector.py is running and you have pressed ENTER.")