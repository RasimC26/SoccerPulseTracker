import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.express as px

# Sets up the browser tab and layout
st.set_page_config(page_title="Soccer Pulse Tracker", layout="wide")

st.title("Live Match Pulse Tracker")

# These are empty slots on the website we will fill with data
metric_placeholder = st.empty()
chart_placeholder = st.empty()
keyword_placeholder = st.sidebar.empty()

# MOCK DATA INITIALIZATION
# We start with an empty DataFrame to hold our "Pulse" scores
if 'buzz_data' not in st.session_state:
    st.session_state.buzz_data = pd.DataFrame(columns=['Minute', 'Buzz'])


# The live loop: This simulates a real-time data stream
for minute in range(1, 91):
    new_buzz = np.random.randint(10, 50) 

    # Append new data to our state
    new_row = pd.DataFrame({'Minute': [minute], 'Buzz': [new_buzz]})
    st.session_state.buzz_data = pd.concat([st.session_state.buzz_data, new_row], ignore_index=True)

   # Update Metrics in their own locked container
    with metric_placeholder.container():
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("Current Match Minute", f"{minute}'")

        if len(st.session_state.buzz_data) > 1:
            previous_buzz = st.session_state.buzz_data['Buzz'].iloc[-2]
            delta_value = new_buzz - previous_buzz
        else:
            delta_value = 0
        m_col2.metric("Latest Buzz Score", new_buzz, delta=delta_value)

    # Update Chart in its placeholder
    with chart_placeholder:
        fig = px.area(st.session_state.buzz_data, x='Minute', y='Buzz', 
             title="Match Momentum Pulse",
             color_discrete_sequence=['#ff4b4b']) 
        fig.update_layout(xaxis_title="Match Minute", yaxis_title="Social Volume")
        chart_placeholder.plotly_chart(fig, use_container_width=True)

    # Update Sidebar in its placeholder
    with keyword_placeholder.container():

        st.write("### Trending Terms")
        trending = ["Haaland", "VAR", "Offside", "Ref", "Bangers Only"]
        st.pills("", trending, selection_mode="multi", disabled=True, key=f"pills_{minute}")

    time.sleep(1)