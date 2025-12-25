import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Basic Page Setup
st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost & ROI Analysis")

# Establish the connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # worksheet names match your provided files exactly
        artists_df = conn.read(worksheet="Log", ttl="0")
        assumptions_df = conn.read(worksheet="Assumptions", ttl="0")
        return artists_df, assumptions_df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None:
    # Sidebar Navigation
    menu = ["Artist Dashboard", "New Projection", "Manage Assumptions"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # --- PAGE 1: VIEW EXISTING DATA ---
    if choice == "Artist Dashboard":
        st.header("Search Artist Metrics")
        band = st.selectbox("Select Band", artists_df['Band Name'].unique())
        
        if band:
            # Extract row for selected artist
            data = artists_df[artists_df['Band Name'] == band].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Average Cost", f"{data['Average Cost']}")
            c2.metric("Total IG Followers", f"{data['Total IG Followers']}")
            c3.metric("Spotify Listeners", f"{data['Spotify Listeners']}")
            
            st.divider()
            st.subheader("Analysis Results")
            m1, m2, m3 = st.columns(3)
            m1.write(f"**Bill Potential:** {data['Bill Potential']}")
            m2.write(f"**Affordability:** {data['Affordability']}")
            m3.write(f"**Total Strength Score:** {data['Total Strength']}")

    # --- PAGE 2: CALCULATOR FOR NEW ARTISTS ---
    elif choice == "New Projection":
        st.header("New Artist Cost Projection")
        with st.form("calc_form"):
            name = st.text_input("Band Name")
            cost = st.number_input("Average Cost ($)", min_value=0)
            ig = st.number_input("IG Followers", min_value=0)
            assoc_ig = st.number_input("Associated IG Followers", min_value=0)
            
            if st.form_submit_button("Calculate"):
                total_ig = ig + assoc_ig
                # Use Headliner budget ($600) from Assumptions file
                headliner_budget = int(assumptions_df.loc[assumptions_df['Bill Placement'] == 'Headliner', 'Budget'].values[0])
                affordable = "Yes" if cost <= headliner_budget else "No"
                
                st.success(f"Projections for {name}")
                res1, res2 = st.columns(2)
                res1.metric("Projected Total IG", f"{total_ig:,}")
                res2.metric("Affordable (Headliner Tier)?", affordable)

    # --- PAGE 3: EDIT ASSUMPTIONS ---
    elif choice == "Manage Assumptions":
        st.header("Edit Tier Budgets")
        st.write("Current budget tiers (e.g., Headliner: $600)")
        # Direct editor for your budget tiers
        edited_df = st.data_editor(assumptions_df)
        
        if st.button("Save to Google Sheets"):
            try:
                conn.update(worksheet="Assumptions", data=edited_df)
                st.success("Google Sheet successfully updated!")
            except Exception as e:
                st.error(f"Update failed: {e}")
