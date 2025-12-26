import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_connection():
    """Authenticates and returns the gspread client."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_data():
    """Fetches data safely from the second tab (Log)."""
    client = get_connection()
    sheet_url = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit?usp=drivesdk"
    sh = client.open_by_url(sheet_url)
    
    # ---------------------------------------------------------
    # CRITICAL FIX: CHANGED INDEX TO 1 (The Second Tab)
    # If this still fails, try replacing 1 with "Log" (quotes included)
    # ---------------------------------------------------------
    try:
        worksheet = sh.get_worksheet(1) 
    except:
        # Fallback if there is only 1 tab or index error
        worksheet = sh.get_worksheet(0)

    raw_rows = worksheet.get_all_values()
    
    cleaned_data = []
    # Skip header row
    for row in raw_rows[1:]:
        try:
            # Helper to clean currency/numbers
            def clean_num(val):
                if isinstance(val, str):
                    return val.replace('$', '').replace(',', '').strip()
                return val

            # Map Columns based on your Log CSV
            # Col 0 = Name, Col 1 = Cost, Col 2 = IG, Col 3 = Assoc, Col 7 = Spotify
            name = row[0]
            if not name: continue # Skip empty rows

            c_cost = int(clean_num(row[1]) or 0) if len(row) > 1 else 0
            c_ig = int(clean_num(row[2]) or 0) if len(row) > 2 else 0
            c_assoc = int(clean_num(row[3]) or 0) if len(row) > 3 else 0
            c_spot = int(clean_num(row[7]) or 0) if len(row) > 7 else 0

            cleaned_data.append({
                "name": name,
                "cost": c_cost,
                "ig": c_ig,
                "assoc_ig": c_assoc,
                "spotify": c_spot
            })
        except Exception:
            continue
            
    return pd.DataFrame(cleaned_data)

def add_artist_to_sheet(name, cost, ig, assoc_ig, spotify):
    """Appends a new artist to the Log Sheet."""
    client = get_connection()
    sheet_url = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit?usp=drivesdk"
    sh = client.open_by_url(sheet_url)
    
    # Same Fix Here: Write to the second tab
    try:
        worksheet = sh.get_worksheet(1)
    except:
        worksheet = sh.get_worksheet(0)
    
    # Append row. 
    # Note: We leave empty strings "" for the columns that contain formulas in your sheet
    # (Total IG, Efficiency, etc.) so the sheet can calculate them.
    # Structure: Name | Cost | IG | Assoc | [Formula] | [Formula] | [Formula] | Spotify
    new_row = [name, cost, ig, assoc_ig, "", "", "", spotify]
    
    worksheet.append_row(new_row)
    st.cache_data.clear()

# -----------------------------------------------------------------------------
# CALCULATIONS (Same as before)
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
                with st.spinner("Saving..."):
                    try:
                        add_artist_to_sheet(new_name, new_base_cost, new_base_ig, new_base_assoc, new_base_spot)
                        st.success(f"Added {new_name}! Refreshing...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Name required.")

# --- Main Area ---
try:
    df = get_data()
    
    if not df.empty:
        artist_names = sorted(df['name'].unique().tolist())
        selected_artist_name = st.selectbox("Select an Artist", artist_names)
        artist_row = df[df['name'] == selected_artist_name].iloc[0]

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Edit: {selected_artist_name}")
            calc_cost = st.number_input("Avg Cost ($)", value=int(artist_row['cost']))
            calc_ig = st.number_input("IG Followers", value=int(artist_row['ig']))
            calc_assoc_ig = st.number_input("Assoc IG", value=int(artist_row['assoc_ig']))
            calc_spotify = st.number_input("Spotify", value=int(artist_row['spotify']))

        total_ig = calc_ig + calc_assoc_ig
        eff_divisor = calc_cost if calc_cost > 0 else 1
        cost_efficiency = total_ig / eff_divisor
        marketing_strength = get_marketing_strength(total_ig)
        donation_strength = get_donation_strength(calc_spotify)
        total_strength = marketing_strength + donation_strength
        bill_label, bill_tier = get_bill_potential_and_label(total_strength)
        affordability = check_affordability(bill_label, calc_cost, assumptions)

        with col2:
            st.subheader("Results")
            st.metric("Total IG", f"{total_ig:,.0f}")
            st.metric("IG/$", f"{cost_efficiency:,.0f}")
            
            st.markdown("#### Strength")
            c1, c2, c3 = st.columns(3)
            c1.metric("Mkt", marketing_strength)
            c2.metric("Don", donation_strength)
            c3.metric("Tot", total_strength)
            
            st.info(f"**Potential:** {bill_label}")
            if affordability == "Yes":
                st.success(f"**Affordable?** {affordability}")
            else:
                st.error(f"**Affordable?** {affordability}")
    else:
        st.warning("No data found in the second tab. Please check your sheet tabs.")

except Exception as e:
    st.error(f"Connection Error: {e}")
