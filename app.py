import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page setup
st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost & ROI Analysis")

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # NOTE: Rename your tab in Google Sheets to "Sheet2" (no space)
        artists = conn.read(worksheet="Log", ttl="0")
        assumptions = conn.read(worksheet="Assumptions", ttl="0")
        return artists, assumptions
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None:
    menu = ["Dashboard", "New Projection", "Settings"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Dashboard":
        st.header("Artist Search")
        band = st.selectbox("Select Band", artists_df['Band Name'].unique())
        
        if band:
            data = artists_df[artists_df['Band Name'] == band].iloc[0]
            c1, c2, c3 = st.columns(3)
            # Displaying data from your Sheet2
            c1.metric("Avg Cost", f"{data['Average Cost']}")
            c2.metric("Total IG Followers", f"{data['Total IG Followers']}")
            c3.metric("Spotify Listeners", f"{data['Spotify Listeners']}")
            
            st.divider()
            st.write(f"**Potential:** {data['Bill Potential']}")
            st.write(f"**Affordable:** {data['Affordability']}")
            st.write(f"**Strength Score:** {data['Total Strength']}")

    elif choice == "New Projection":
        st.header("Calculator")
        with st.form("calc"):
            name = st.text_input("Band Name")
            cost = st.number_input("Average Cost ($)", min_value=0)
            ig = st.number_input("IG Followers", min_value=0)
            
            if st.form_submit_button("Run Analysis"):
                # Uses the Headliner budget ($600) from your Assumptions
                h_budget = int(assumptions_df.loc[assumptions_df['Bill Placement'] == 'Headliner', 'Budget'].values[0])
                status = "Yes" if cost <= h_budget else "No"
                st.success(f"Projection for {name}: Affordable (Headliner Tier)? {status}")

    elif choice == "Settings":
        st.header("Edit Assumptions")
        # Edit Headliner ($600), Direct Support ($200), etc.
        edited = st.data_editor(assumptions_df)
        if st.button("Save to Google Sheets"):
            conn.update(worksheet="Assumptions", data=edited)
            st.success("Updated!")
