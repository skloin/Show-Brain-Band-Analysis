import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost & ROI Analysis")

# Establish Connection
# You can also pass the URL directly here to avoid the "Spreadsheet must be specified" error
URL = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # worksheet names must match your tabs exactly
        artists_df = conn.read(spreadsheet=URL, worksheet="Sheet 2", ttl="0")
        assumptions_df = conn.read(spreadsheet=URL, worksheet="Assumptions", ttl="0")
        return artists_df, assumptions_df
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None:
    # Navigation
    page = st.sidebar.radio("Navigation", ["Dashboard", "New Projection", "Assumptions"])

    if page == "Dashboard":
        st.header("Artist Database")
        artist = st.selectbox("Select Band", artists_df['Band Name'].unique())
        
        if artist:
            # [span_2](start_span)Display values from Sheet 2[span_2](end_span)
            res = artists_df[artists_df['Band Name'] == artist].iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Cost", res['Average Cost'])
            col2.metric("Total IG Followers", res['Total IG Followers'])
            col3.metric("Spotify Listeners", res['Spotify Listeners'])
            
            st.divider()
            st.write(f"**Marketing Strength:** {res['Marketing Strength']}")
            st.write(f"**Bill Potential:** {res['Bill Potential']}")
            st.write(f"**Affordability:** {res['Affordability']}")

    elif page == "New Projection":
        st.header("New Artist Calculator")
        # Inputs for cost, IG, and Spotify followers
        with st.form("calc"):
            name = st.text_input("Band Name")
            cost = st.number_input("Cost ($)", min_value=0)
            ig = st.number_input("IG Followers", min_value=0)
            assoc_ig = st.number_input("Associated IG Followers", min_value=0)
            spotify = st.number_input("Spotify Followers", min_value=0)
            
            if st.form_submit_button("Run Analysis"):
                total_ig = ig + assoc_ig
                # [span_3](start_span)Compare against Headliner budget (600) from Assumptions[span_3](end_span)
                h_budget = assumptions_df.loc[assumptions_df['Bill Placement'] == 'Headliner', 'Budget'].values[0]
                affordable = "Yes" if cost <= int(h_budget) else "No"
                
                st.info(f"Analysis for {name}")
                st.metric("Total Projected IG", f"{total_ig:,}")
                st.metric("Affordable (Headliner Tier)?", affordable)

    elif page == "Assumptions":
        st.header("Configure Tiers")
        # [span_4](start_span)Edit the Assumptions tab (Bill Placement and Budget)[span_4](end_span)
        edited_df = st.data_editor(assumptions_df)
        if st.button("Save to Sheets"):
            conn.update(spreadsheet=URL, worksheet="Assumptions", data=edited_df)
            st.success("Sheet Updated!")
