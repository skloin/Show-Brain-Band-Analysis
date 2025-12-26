import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------------------------------------------------------
# Define the scope
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_connection():
    """Authenticates and returns the gspread client."""
    # Load credentials from secrets.toml
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_data():
    """Fetches data from the Google Sheet."""
    client = get_connection()
    # Open the sheet by URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit?usp=drivesdk"
    sh = client.open_by_url(sheet_url)
    
    # Selecting the worksheet. 
    # Adjust this if your data is on "Sheet1" or "Sheet 2"
    # Using index 0 (first tab) usually works best if it's the main list.
    worksheet = sh.get_worksheet(0) 
    
    # Get all records as a list of dicts
    data = worksheet.get_all_records()
    
    # Clean up keys to match our internal logic if headers are different in the sheet
    # Assuming Sheet Headers: Band Name, Avg Cost, IG, Assoc IG, Spotify
    # We map them to our internal simple keys: name, cost, ig, assoc_ig, spotify
    cleaned_data = []
    for row in data:
        cleaned_data.append({
            "name": str(row.get("Band Name", "")), # Adjust "Band Name" to exact header in sheet
            "cost": int(row.get("Avg Cost", 0) or 0),
            "ig": int(row.get("IG", 0) or 0),
            "assoc_ig": int(row.get("Assoc IG", 0) or 0),
            "spotify": int(row.get("Spotify", 0) or 0)
        })
    
    return pd.DataFrame(cleaned_data), worksheet

def add_artist_to_sheet(name, cost, ig, assoc_ig, spotify):
    """Appends a new artist to the Google Sheet."""
    client = get_connection()
    sheet_url = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit?usp=drivesdk"
    sh = client.open_by_url(sheet_url)
    worksheet = sh.get_worksheet(0)
    
    # Create the row to append
    # MUST MATCH THE ORDER OF COLUMNS IN YOUR GOOGLE SHEET
    # Example: Band Name | Avg Cost | IG | Assoc IG | Spotify
    new_row = [name, cost, ig, assoc_ig, spotify]
    
    worksheet.append_row(new_row)
    st.cache_data.clear() # Clear cache to force reload of data next time

# -----------------------------------------------------------------------------
# CALCULATIONS
# -----------------------------------------------------------------------------
def get_marketing_strength(total_ig):
    if total_ig < 3000: return 1
    if total_ig < 7000: return 2
    if total_ig < 11000: return 3
    if total_ig <= 20000: return 4
    return 5

def get_donation_strength(spotify):
    if spotify < 4900: return 1
    if spotify < 6000: return 2
    if spotify < 15000: return 3
    if spotify <= 25000: return 4
    return 5

def get_bill_potential_and_label(total_strength):
    if total_strength <= 2: return "Opener", "Opener"
    if total_strength <= 5: return "Indirect Support", "Indirect Support"
    if total_strength <= 7: return "Direct Support", "Direct Support"
    return "Headliner", "Headliner"

def check_affordability(bill_label, cost, assumptions):
    budget = assumptions.get(bill_label, 0)
    return "Yes" if cost <= budget else "No"

# -----------------------------------------------------------------------------
# UI LAYOUT
# -----------------------------------------------------------------------------
st.title("SB Artist Cost Analysis (Live Sync)")

# --- Sidebar ---
st.sidebar.header("Configuration")

# 1. Budget Assumptions
st.sidebar.subheader("Budget Assumptions")
budget_headliner = st.sidebar.number_input("Headliner Budget ($)", value=600)
budget_direct = st.sidebar.number_input("Direct Support Budget ($)", value=200)
budget_indirect = st.sidebar.number_input("Indirect Support Budget ($)", value=100)
budget_opener = st.sidebar.number_input("Opener Budget ($)", value=0)

assumptions = {
    "Headliner": budget_headliner,
    "Direct Support": budget_direct,
    "Indirect Support": budget_indirect,
    "Opener": budget_opener
}

# 2. Add New Artist Section
st.sidebar.markdown("---")
with st.sidebar.expander("➕ Add New Artist to Sheet"):
    with st.form("add_artist_form"):
        new_name = st.text_input("Band Name")
        new_base_cost = st.number_input("Cost ($)", min_value=0, value=0)
        new_base_ig = st.number_input("IG Followers", min_value=0, value=0)
        new_base_assoc = st.number_input("Assoc. IG", min_value=0, value=0)
        new_base_spot = st.number_input("Spotify", min_value=0, value=0)
        
        submitted = st.form_submit_button("Save to Google Sheet")
        if submitted:
            if new_name:
                with st.spinner("Saving to Google Sheet..."):
                    try:
                        add_artist_to_sheet(new_name, new_base_cost, new_base_ig, new_base_assoc, new_base_spot)
                        st.success(f"Added {new_name} to the live sheet! Refreshing...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving to sheet: {e}")
            else:
                st.error("Please enter a name.")

# --- Main Area ---

# Load Data Live
try:
    df, _ = get_data()
    
    # Sort names
    artist_names = sorted(df['name'].unique().tolist())
    
    # Selector
    selected_artist_name = st.selectbox("Select an Artist", artist_names)

    # Get current data for selected artist
    artist_row = df[df['name'] == selected_artist_name].iloc[0]

    st.markdown("---")
    col1, col2 = st.columns(2)

    # --- Input Section (Main) ---
    with col1:
        st.subheader(f"Edit Values: {selected_artist_name}")
        st.caption("Adjust values here to see how metrics change (Local simulation only).")
        
        calc_cost = st.number_input("Average Cost ($)", value=int(artist_row['cost']))
        calc_ig = st.number_input("IG Followers", value=int(artist_row['ig']))
        calc_assoc_ig = st.number_input("Associated IG Followers", value=int(artist_row['assoc_ig']))
        calc_spotify = st.number_input("Spotify Listeners", value=int(artist_row['spotify']))

    # --- Calculation Section ---
    total_ig = calc_ig + calc_assoc_ig
    eff_divisor = calc_cost if calc_cost > 0 else 1
    cost_efficiency = total_ig / eff_divisor

    marketing_strength = get_marketing_strength(total_ig)
    donation_strength = get_donation_strength(calc_spotify)
    total_strength = marketing_strength + donation_strength

    bill_label, bill_tier = get_bill_potential_and_label(total_strength)
    affordability = check_affordability(bill_label, calc_cost, assumptions)

    # --- Output Section ---
    with col2:
        st.subheader("Analysis Results")
        
        st.metric("Total IG Followers", f"{total_ig:,.0f}")
        
        eff_val = f"{cost_efficiency:,.0f}"
        if calc_cost == 0: eff_val += " (Infinite/Base)"
        st.metric("Cost Efficiency (IG/$)", eff_val)
        
        st.markdown("#### Strength Metrics")
        c_m, c_d, c_t = st.columns(3)
        c_m.metric("Marketing", marketing_strength)
        c_d.metric("Donation", donation_strength)
        c_t.metric("Total", total_strength)
        
        st.markdown("#### Booking")
        st.info(f"**Bill Potential:** {bill_label}")
        
        if affordability == "Yes":
            st.success(f"**Affordable?** {affordability}")
        else:
            st.error(f"**Affordable?** {affordability}")

except Exception as e:
    st.error("Could not connect to Google Sheet.")
    st.write("1. Check your `secrets.toml` file.")
    st.write("2. Ensure you shared the sheet with the Service Account Email.")
    st.write(f"Error details: {e}")

st.markdown("---")
st.caption("Live Connection Active. 'Add Artist' writes directly to the Sheet.")
