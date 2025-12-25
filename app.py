import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost & ROI Analysis")

# Define the connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # We use 'Sheet 2' and 'Assumptions' exactly as they appear in your files
        # ttl=0 ensures the app pulls fresh data on every manual refresh
        artists_df = conn.read(worksheet="Sheet 2", ttl="0")
        assumptions_df = conn.read(worksheet="Assumptions", ttl="0")
        return artists_df, assumptions_df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None:
    # Sidebar Navigation
    page = st.sidebar.radio("Navigation", ["Artist Dashboard", "New Projection", "Edit Assumptions"])

    if page == "Artist Dashboard":
        st.header("Search Existing Artist Data")
        artist = st.selectbox("Select Band", artists_df['Band Name'].unique())
        
        if artist:
            res = artists_df[artists_df['Band Name'] == artist].iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Cost", f"{res['Average Cost']}")
            col2.metric("Total IG Followers", f"{res['Total IG Followers']}")
            col3.metric("Spotify Listeners", f"{res['Spotify Listeners']}")
            
            st.divider()
            st.subheader("Placement & ROI")
            m1, m2, m3 = st.columns(3)
            m1.write(f"**Bill Potential:** {res['Bill Potential']}")
            m2.write(f"**Marketing Strength:** {res['Marketing Strength']}")
            m3.write(f"**Affordability:** {res['Affordability']}")

    elif page == "New Projection":
        st.header("New Artist Projection")
        with st.form("calc"):
            name = st.text_input("Band Name")
            cost = st.number_input("Average Cost ($)", min_value=0)
            ig = st.number_input("IG Followers", min_value=0)
            assoc_ig = st.number_input("Associated IG Followers", min_value=0)
            spotify = st.number_input("Spotify Followers", min_value=0)
            
            if st.form_submit_button("Run Analysis"):
                total_ig = ig + assoc_ig
                # Logic: Compare against Headliner budget ($600) from your Assumptions file
                h_budget = int(assumptions_df.loc[assumptions_df['Bill Placement'] == 'Headliner', 'Budget'].values[0])
                affordable = "Yes" if cost <= h_budget else "No"
                
                st.success(f"Projections for {name}")
                res1, res2 = st.columns(2)
                res1.metric("Projected Total IG", f"{total_ig:,}")
                res2.metric("Affordable (Headliner Tier)?", affordable)

    elif page == "Edit Assumptions":
        st.header("Manage Placement Budgets")
        # Edit the table containing Headliner ($600), Direct Support ($200), etc.
        edited_df = st.data_editor(assumptions_df)
        
        if st.button("Save to Google Sheets"):
            conn.update(worksheet="Assumptions", data=edited_df)
            st.success("Google Sheet Updated!")
