import streamlit as st
import requests
import pandas as pd
import altair as alt

# StarTree Cloud Broker URL and Basic Auth Token
PINOT_BROKER_URL = 'https://<your-broker-url>'  # Replace with your actual broker URL
BASIC_AUTH_TOKEN = 'Basic <your-basic-auth-token>'  # Replace with your actual Basic Auth token

# Function to query StarTree Cloud Pinot
def query_pinot(query):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': BASIC_AUTH_TOKEN
    }
    response = requests.post(
        f'{PINOT_BROKER_URL}/query/sql',
        json={'sql': query},
        headers=headers
    )
    
    if response.status_code != 200:
        st.error(f"Error querying Pinot: {response.status_code} {response.reason}")
        return []

    try:
        result = response.json()
        if 'resultTable' not in result or 'rows' not in result['resultTable']:
            st.error("Unexpected response format")
            st.json(result)  # Display the unexpected JSON for debugging
            return []
        return result['resultTable']['rows']
    except ValueError:
        st.error("Failed to parse response as JSON")
        st.text(response.text)  # Display the raw response text for debugging
        return []

# Streamlit app
st.title('Clickstream Metrics Dashboard')

# Query event counts by type
event_counts_query = """
    SELECT event_type, COUNT(*) as event_count 
    FROM clickstream 
    GROUP BY event_type
"""
event_counts_data = query_pinot(event_counts_query)
if event_counts_data:
    event_counts_df = pd.DataFrame(event_counts_data, columns=['event_type', 'event_count'])

    # Display event counts
    st.write("## Event Counts by Type")
    st.write(event_counts_df)

    # Bar chart of event counts
    bar_chart = alt.Chart(event_counts_df).mark_bar().encode(
        x='event_type',
        y='event_count'
    )
    st.altair_chart(bar_chart, use_container_width=True)

# Query average duration by event type
avg_duration_query = """
    SELECT event_type, AVG(duration) as avg_duration 
    FROM clickstream 
    GROUP BY event_type
"""
avg_duration_data = query_pinot(avg_duration_query)
if avg_duration_data:
    avg_duration_df = pd.DataFrame(avg_duration_data, columns=['event_type', 'avg_duration'])

    # Display average duration
    st.write("## Average Duration by Event Type")
    st.write(avg_duration_df)

    # Line chart of average duration
    line_chart = alt.Chart(avg_duration_df).mark_line().encode(
        x='event_type',
        y='avg_duration'
    )
    st.altair_chart(line_chart, use_container_width=True)
