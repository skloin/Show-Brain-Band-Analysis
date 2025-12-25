import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page setup
st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost Analysis")

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Fetching the data from your specific sheet tabs
    artists_df = conn.read(worksheet="Sheet 2", ttl="0")
    assumptions_df = conn.read(worksheet="Assumptions", ttl="0")
    return artists_df, assumptions_df

try:
    artists_df, assumptions_df = load_data()
    # [span_2](start_span)Create budget lookup (e.g., Headliner: 600)[span_2](end_span)
    budgets = dict(zip(assumptions_df['Bill Placement'], assumptions_df['Budget']))
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# Sidebar Navigation
page = st.sidebar.radio("Go to", ["Artist Search", "New Projection", "Edit Assumptions"])

if page == "Artist Search":
    st.header("Search Existing Artist Data")
    artist = st.selectbox("Select Artist", artists_df['Band Name'].unique())
    
    if artist:
        res = artists_df[artists_df['Band Name'] == artist].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Average Cost", res['Average Cost'])
        [span_3](start_span)c2.metric("Total IG Followers", res['Total IG Followers']) #[span_3](end_span)
        [span_4](start_span)c3.metric("Spotify Listeners", res['Spotify Listeners']) #[span_4](end_span)
        
        st.write("---")
        st.subheader("Placement Details")
        [span_5](start_span)st.write(f"**Bill Potential:** {res['Bill Potential']}") #[span_5](end_span)
        [span_6](start_span)st.write(f"**Affordability:** {res['Affordability']}") #[span_6](end_span)

elif page == "New Projection":
    st.header("Predictive Calculator")
    with st.form("calc"):
        name = st.text_input("Band Name")
        cost = st.number_input("Average Cost ($)", min_value=0.0)
        ig_own = st.number_input("IG Followers", min_value=0)
        ig_assoc = st.number_input("Associated IG Followers", min_value=0)
        
        if st.form_submit_button("Calculate"):
            total_ig = ig_own + ig_assoc
            # [span_7](start_span)Match affordability against Headliner budget (600)[span_7](end_span)
            status = "Yes" if cost <= budgets.get("Headliner", 600) else "No"
            
            st.info(f"Analysis for {name}")
            st.metric("Projected Total IG", f"{total_ig:,}")
            st.metric("Affordable (Headliner Tier)?", status)

elif page == "Edit Assumptions":
    st.header("Update Tier Budgets")
    # [span_8](start_span)Displays: Headliner, Direct Support, Indirect Support, Opener[span_8](end_span)
    updated_assumptions = st.data_editor(assumptions_df)
    
    if st.button("Sync to Google Sheets"):
        conn.update(worksheet="Assumptions", data=updated_assumptions)
        st.success("Google Sheet Updated!")
