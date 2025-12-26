import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost & ROI Analysis")

# Direct URL to ensure the connection finds the right file
# Make sure this sheet is set to "Anyone with the link can View"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit"

# Establish connection
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_currency(x):
    """Removes '$' and ',' from numbers so Python can do math."""
    if isinstance(x, str):
        return float(x.replace('$', '').replace(',', '').strip())
    return x

def load_data():
    try:
        # Load the "Log" tab (Artist Data)
        artists_df = conn.read(spreadsheet=SHEET_URL, worksheet="Log", ttl="0")
        
        # Load the "Assumptions" tab (Budget Tiers)
        assumptions_df = conn.read(spreadsheet=SHEET_URL, worksheet="Assumptions", ttl="0")
        
        # CLEAN THE DATA: Convert text like "$1,000" to number 1000.0
        cols_to_clean = ['Average Cost', 'IG Followers', 'Associated IG Followers', 'Total IG Followers', 'Spotify Listeners']
        for col in cols_to_clean:
            if col in artists_df.columns:
                artists_df[col] = artists_df[col].apply(clean_currency)
                
        return artists_df, assumptions_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None and assumptions_df is not None:
    # Create a dictionary for budgets: {'Headliner': 600, 'Direct Support': 200, ...}
    budgets = dict(zip(assumptions_df['Bill Placement'], assumptions_df['Budget']))

    # --- NAVIGATION ---
    menu = ["Artist Dashboard", "New Projection", "Manage Assumptions"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # --- PAGE 1: DASHBOARD ---
    if choice == "Artist Dashboard":
        st.header("Artist Database")
        # specific column 'Band Name' from your Log file
        band_name = st.selectbox("Select Band", artists_df['Band Name'].unique())
        
        if band_name:
            row = artists_df[artists_df['Band Name'] == band_name].iloc[0]
            
            # Top Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Average Cost", f"${row['Average Cost']:,.2f}")
            c2.metric("Total IG Followers", f"{row['Total IG Followers']:,.0f}")
            c3.metric("Spotify Listeners", f"{row['Spotify Listeners']:,.0f}")
            
            st.divider()
            
            # Detailed Metrics from your file
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Bill Potential:** {row['Bill Potential']}")
            c2.write(f"**Marketing Strength:** {row['Marketing Strength']}")
            c3.write(f"**Affordability:** {row['Affordability']}")

    # --- PAGE 2: CALCULATOR ---
    elif choice == "New Projection":
        st.header("New Artist Projector")
        with st.form("new_artist"):
            name = st.text_input("Band Name")
            cost = st.number_input("Proposed Cost ($)", min_value=0.0)
            ig = st.number_input("IG Followers", min_value=0)
            assoc_ig = st.number_input("Associated IG Followers", min_value=0)
            
            submitted = st.form_submit_button("Run Analysis")
            
            if submitted:
                total_ig = ig + assoc_ig
                # Logic: Check if Cost is <= Headliner Budget ($600)
                limit = budgets.get("Headliner", 600) 
                is_affordable = "Yes" if cost <= limit else "No"
                
                st.info(f"Results for {name}")
                col1, col2 = st.columns(2)
                col1.metric("Total Projected Reach", f"{total_ig:,}")
                col2.metric(f"Affordable (Limit: ${limit})?", is_affordable)

    # --- PAGE 3: ASSUMPTIONS ---
    elif choice == "Manage Assumptions":
        st.header("Configure Budget Tiers")
        # Edit the Assumptions table directly
        edited_df = st.data_editor(assumptions_df)
        
        if st.button("Save to Google Sheets"):
            try:
                conn.update(spreadsheet=SHEET_URL, worksheet="Assumptions", data=edited_df)
                st.success("Assumptions updated successfully!")
            except Exception as e:
                st.error(f"Could not save: {e}")
