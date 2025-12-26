import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SB Artist Analysis", layout="wide")
st.title("📊 SB Artist Cost & ROI Analysis")

# Establish connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Fetching specifically by tab name from your provided files
        artists_df = conn.read(worksheet="Log", ttl="0")
        assumptions_df = conn.read(worksheet="Assumptions", ttl="0")
        return artists_df, assumptions_df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, None

artists_df, assumptions_df = load_data()

if artists_df is not None:
    # [span_0](start_span)Build Budget Lookup from Assumptions[span_0](end_span)
    # [span_1](start_span)Headliner: 600, Direct Support: 200, Indirect Support: 100[span_1](end_span)
    budgets = dict(zip(assumptions_df['Bill Placement'], assumptions_df['Budget']))

    menu = ["Artist Dashboard", "New Projection", "Manage Assumptions"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Artist Dashboard":
        st.header("Search Existing Artist Data")
        band = st.selectbox("Select Band", artists_df['Band Name'].unique())
        
        if band:
            data = artists_df[artists_df['Band Name'] == band].iloc[0]
            c1, c2, c3 = st.columns(3)
            # [span_2](start_span)Display metrics from Log file[span_2](end_span)
            c1.metric("Average Cost", f"{data['Average Cost']}")
            c2.metric("Total IG Followers", f"{data['Total IG Followers']}")
            c3.metric("Spotify Listeners", f"{data['Spotify Listeners']}")
            
            st.divider()
            st.subheader("Analysis Results")
            m1, m2, m3 = st.columns(3)
            m1.write(f"**Bill Potential:** {data['Bill Potential']}")
            m2.write(f"**Affordability:** {data['Affordability']}")
            m3.write(f"**Total Strength:** {data['Total Strength']}")

    elif choice == "New Projection":
        st.header("New Artist Cost Projection")
        with st.form("calc_form"):
            name = st.text_input("Band Name")
            cost = st.number_input("Average Cost ($)", min_value=0)
            ig = st.number_input("IG Followers", min_value=0)
            assoc_ig = st.number_input("Associated IG Followers", min_value=0)
            
            if st.form_submit_button("Calculate"):
                total_ig = ig + assoc_ig
                # [span_3](start_span)Logic: Compare against Headliner budget ($600)[span_3](end_span)
                h_budget = budgets.get("Headliner", 600)
                affordable = "Yes" if cost <= h_budget else "No"
                
                st.success(f"Projections for {name}")
                res1, res2 = st.columns(2)
                res1.metric("Projected Total IG", f"{total_ig:,}")
                res2.metric("Affordable (Headliner Tier)?", affordable)

    elif choice == "Manage Assumptions":
        st.header("Edit Tier Budgets")
        # [span_4](start_span)Direct editor for your budget tiers[span_4](end_span)
        edited_df = st.data_editor(assumptions_df)
        
        if st.button("Save to Google Sheets"):
            conn.update(worksheet="Assumptions", data=edited_df)
            st.success("Google Sheet successfully updated!")
