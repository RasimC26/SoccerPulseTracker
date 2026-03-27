import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import streamlit.components.v1 as components

# -------------------------------
# Function to read the latest data from CSV
# -------------------------------
def get_real_data():
    try:
        df = pd.read_csv('pulse_data.csv')
        df.columns = ['Minute', 'Buzz', 'Trending', 'Timestamp', 'Status'] 
        df['Minute'] = df['Minute'].astype(str)
        return df
    except Exception as e:
        # Returns an empty dataframe if the file isn't ready yet
        return pd.DataFrame(columns=['Minute', 'Buzz', 'Trending', 'Timestamp', 'Status'])

# Load the latest data
df = get_real_data()


# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Soccer Pulse Tracker", layout="wide")
st.title("Live Match Pulse Tracker")

# -------------------------------
# Countdown Timer (JS), ONLY if data exists
# -------------------------------
if not df.empty and len(df) > 0:
    last_update_time = float(df['Timestamp'].iloc[-1])
    components.html(f"""
<div id="countdown" style="font-family: 'Source Sans Pro', sans-serif; font-size:25px; font-weight:700; color:white;">
Refreshing in ...
</div>

<script>
const lastUpdate = {last_update_time};
let isReloading = false;

function updateTimer() {{
    if (isReloading) return;

    const now = Date.now() / 1000;
    const elapsed = now - lastUpdate;
    const remaining = Math.max(0, 60 - Math.floor(elapsed));

    document.getElementById("countdown").innerHTML =
        "Next Refresh in <b>" + remaining + "s</b>";

    if (remaining <= 0 && !isReloading) {{
        isReloading = true;
        document.getElementById("countdown").innerHTML = "<b>Syncing Data...</b>";
        setTimeout(() => {{
            window.parent.location.reload();
        }}, 2000); // small delay to show "Syncing Data..."
    }}
}}

setInterval(updateTimer, 1000);
updateTimer();
</script>
""", height=40)

# -------------------------------
# Placeholders for dynamic content
# -------------------------------
metric_placeholder = st.empty() # Metrics like Match Minute and Buzz
chart_placeholder = st.empty() # Area chart for Buzz over time
keyword_placeholder = st.sidebar.empty() # Trending words in sidebar

# -------------------------------
# Only update if data exists
# -------------------------------
if not df.empty and len(df) > 0:

    # Get latest values
    current_minute = df['Minute'].iloc[-1]
    current_buzz = df['Buzz'].iloc[-1]

    # Process Trending Words
    raw_trending = df['Trending'].iloc[-1]
    if pd.isna(raw_trending) or raw_trending == "":
        trending_list = ["Waiting..."]
    else:
        trending_list = str(raw_trending).split(",")

    # -------------------------------
    # Metrics Section
    # -------------------------------
    with metric_placeholder.container():
        m_col1, m_col2 = st.columns(2)
        delta_val = int(current_buzz - df['Buzz'].iloc[-2]) if len(df) > 1 else 0
        m_col1.metric("Match Minute", f"{current_minute}'")
        m_col2.metric("Latest Buzz Score", current_buzz, delta=delta_val)

    # -------------------------------
    # Chart Section
    # -------------------------------
    with chart_placeholder.container():
        fig = px.area(df, x='Minute', y='Buzz', title="Match Momentum Pulse",
              color_discrete_sequence=['#ff4b4b'],
              category_orders={"Minute": df['Minute'].tolist()})
              

        fig.update_layout(
            xaxis_title="Match Minute",
            yaxis_title="Social Volume",
            xaxis=dict(type='category', nticks=20, tickangle=0, tickfont=dict(size=10), fixedrange=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Sidebar - Trending Words
    # -------------------------------
    with keyword_placeholder.container():
        st.write("# Top 5 Trending Terms:")
        
        # Define the ranking styles/sizes
        rank_prefixes = ["# 1. ", "### 2. ", "#### 3. ", "##### 4. ", "###### 5. "]
        
        if trending_list != "Waiting...":
            for i in range(len(trending_list)):

                word = trending_list[i].upper()
                
                prefix = rank_prefixes[i]
                
                if i == 0: # The #1 Spot
                    st.markdown(f"{prefix} :green[{word}]")
                else:
                    st.markdown(f"{prefix}{word}")
        else:
            st.info("Waiting for chat data...")
            
# -------------------------------
# Fallback for when CSV has no data yet
# -------------------------------
else:
    # What to show while waiting for the first minute of data
    with metric_placeholder.container():
        st.warning("Waiting for kickoff... The first data point will appear in 60 seconds.")
    with chart_placeholder.container():
        st.info("Check your terminal to ensure collector.py is running and you have pressed ENTER.")