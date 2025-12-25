import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Basic Page Setup
st.set_page_config(page_title="SB Artist Cost Analysis", layout="wide")
st.title("🎵 SB Artist Cost Analysis")

# Establish the connection to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Load your two specific sheets
    # ttl=0 ensures the app fetches fresh data on every manual refresh
    try:
        artists = conn.read(worksheet="Sheet 2", ttl="0")
        assumptions = conn.read(worksheet="Assumptions", ttl="0")
        return artists, assumptions
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None:
    # Build a lookup for budget thresholds (Headliner: 600, etc.)
    budgets = dict(zip(assumptions_df['Bill Placement'], assumptions_df['Budget']))

    # Sidebar Navigation
    menu = ["Artist Dashboard", "New Artist Projection", "Configure Assumptions"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # --- PAGE 1: DASHBOARD ---
    if choice == "Artist Dashboard":
        st.header("Search Artist Metrics")
        band_name = st.selectbox("Select a Band", artists_df['Band Name'].unique())
        
        if band_name:
            data = artists_df[artists_df['Band Name'] == band_name].iloc[0]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Cost", f"{data['Average Cost']}")
            c2.metric("Total IG Followers", f"{data['Total IG Followers']}")
            c3.metric("Spotify Listeners", f"{data['Spotify Listeners']}")
            
            st.divider()
            st.subheader("Placement Analysis")
            m1, m2, m3 = st.columns(3)
            m1.write(f"**Bill Potential:** {data['Bill Potential']}")
            m2.write(f"**Affordability:** {data['Affordability']}")
            m3.write(f"**Total Strength Score:** {data['Total Strength']}")

    # --- PAGE 2: CALCULATOR ---
    elif choice == "New Artist Projection":
        st.header("New Artist Cost Projection")
        with st.form("calc_form"):
            name = st.text_input("Band Name")
            cost = st.number_input("Average Cost ($)", min_value=0)
            ig = st.number_input("IG Followers", min_value=0)
            assoc_ig = st.number_input("Associated IG Followers", min_value=0)
            
            if st.form_submit_button("Calculate Results"):
                total_ig = ig + assoc_ig
                # Logic: Is the cost within the Headliner budget ($600)?
                headliner_budget = budgets.get("Headliner", 600)
                affordable = "Yes" if cost <= headliner_budget else "No"
                
                st.info(f"Projections for {name}")
                res1, res2 = st.columns(2)
                res1.metric("Projected Total IG", f"{total_ig:,}")
                res2.metric("Affordable (Headliner Tier)?", affordable)

    # --- PAGE 3: SETTINGS ---
    elif choice == "Configure Assumptions":
        st.header("Edit Tier Budgets")
        st.write("Modify the budgets for each placement level below.")
        
        # This table allows you to edit the "Assumptions" sheet directly
        edited_df = st.data_editor(assumptions_df, num_rows="dynamic")
        
        if st.button("Save Changes to Sheet"):
            conn.update(worksheet="Assumptions", data=edited_df)
            st.success("Successfully updated Google Sheets!")
