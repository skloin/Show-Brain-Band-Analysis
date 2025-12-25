import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Artist Cost Analysis", layout="wide")
st.title("🎨 Artist Cost & ROI Analysis")

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CACHED DATA FETCHING ---
def get_data():
    # Load Sheet 2 (Artist Data) and Assumptions
    artists_df = conn.read(worksheet="Sheet 2", ttl="0")
    assumptions_df = conn.read(worksheet="Assumptions", ttl="0")
    return artists_df, assumptions_df

artists_df, assumptions_df = get_data()

# Helper to get assumption values as a dict
config = dict(zip(assumptions_df.iloc[:, 0], assumptions_df.iloc[:, 1]))

# --- NAVIGATION ---
menu = ["Artist Dashboard", "Add New Artist", "Configure Assumptions"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- CALCULATOR LOGIC ---
def calculate_metrics(cost, ig, spotify, config):
    # Example logic based on common analysis formulas
    # Replace these with your specific math from the spreadsheet
    cost_per_ig = cost / ig if ig > 0 else 0
    cost_per_spotify = cost / spotify if spotify > 0 else 0
    total_reach = ig + spotify
    reach_score = (total_reach * config.get('Reach Multiplier', 1.0))
    
    return {
        "Cost per IG Follower": f"${cost_per_ig:.4f}",
        "Cost per Spotify Follower": f"${cost_per_spotify:.4f}",
        "Total Reach": f"{total_reach:,}",
        "Projected ROI": f"{reach_score / cost:.2f}x" if cost > 0 else "0"
    }

# --- PAGES ---
if choice == "Artist Dashboard":
    st.header("Existing Artist Analysis")
    artist_list = artists_df['Artist'].tolist()
    selected_artist = st.selectbox("Select an Artist", artist_list)
    
    if selected_artist:
        data = artists_df[artists_df['Artist'] == selected_artist].iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Cost", f"${data['Cost']:,}")
        col2.metric("IG Followers", f"{data['IG Followers']:,}")
        col3.metric("Spotify Followers", f"{data['Spotify']:,}")
        
        st.subheader("Calculated Fields (from Sheet)")
        # This displays the calculated columns already present in your sheet
        st.dataframe(artists_df[artists_df['Artist'] == selected_artist])

elif choice == "Add New Artist":
    st.header("New Artist Projection")
    with st.form("new_artist_form"):
        name = st.text_input("Artist Name")
        cost = st.number_input("Proposed Cost ($)", min_value=0.0)
        ig = st.number_input("IG Followers", min_value=0)
        spotify = st.number_input("Spotify Followers", min_value=0)
        submit = st.form_submit_button("Calculate & Preview")
        
        if submit:
            results = calculate_metrics(cost, ig, spotify, config)
            st.success(f"Projections for {name}:")
            cols = st.columns(len(results))
            for i, (label, val) in enumerate(results.items()):
                cols[i].metric(label, val)

elif choice == "Configure Assumptions":
    st.header("Settings & Assumptions")
    st.info("Update the values below to change how the 'New Artist' formulas calculate.")
    
    # Enable editing of the assumptions table
    edited_df = st.data_editor(assumptions_df, num_rows="dynamic")
    
    if st.button("Save Assumptions to Google Sheets"):
        conn.update(worksheet="Assumptions", data=edited_df)
        st.success("Assumptions updated successfully!")
