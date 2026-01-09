import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------------------
# CUSTOM PUNK/INDIE ROCK STYLING
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Show Brain | Booking", page_icon="🎸", layout="wide")

punk_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@400;700&display=swap');
    
    /* Main background - dark gritty texture */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
        color: #f0f0f0;
    }
    
    /* Headers - bold punk aesthetic */
    h1, h2, h3 {
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        color: #ff1744 !important;
        text-shadow: 3px 3px 0px rgba(0,0,0,0.7), 
                     0 0 20px rgba(255,23,68,0.5) !important;
    }
    
    h1 {
        font-size: 3.5rem !important;
        border-bottom: 4px solid #ff1744 !important;
        padding-bottom: 15px !important;
        margin-bottom: 30px !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f1f1f 0%, #151515 100%) !important;
        border-right: 3px solid #ff1744 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00e5ff !important;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.8),
                     0 0 15px rgba(0,229,255,0.5) !important;
    }
    
    /* Input boxes - neon accents */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 2px solid #00e5ff !important;
        border-radius: 4px !important;
        font-family: 'Roboto Condensed', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #ff1744 !important;
        box-shadow: 0 0 15px rgba(255,23,68,0.6) !important;
    }
    
    /* Buttons - punk rock style */
    .stButton button {
        background: linear-gradient(135deg, #ff1744 0%, #c51162 100%) !important;
        color: white !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.2rem !important;
        letter-spacing: 2px !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 12px 30px !important;
        text-transform: uppercase !important;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.5),
                    0 0 20px rgba(255,23,68,0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #00e5ff 0%, #00b8d4 100%) !important;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.7),
                    0 0 30px rgba(0,229,255,0.6) !important;
        transform: translate(-2px, -2px) !important;
    }
    
    /* Metrics - grungy cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        padding: 15px !important;
        border-left: 4px solid #ff1744 !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 2rem !important;
        text-shadow: 0 0 10px rgba(0,229,255,0.5) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
        font-family: 'Roboto Condensed', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.9rem !important;
    }
    
    /* Info/Success/Error boxes - vibrant */
    .stAlert {
        border-radius: 4px !important;
        border-left: 5px solid !important;
        font-family: 'Roboto Condensed', sans-serif !important;
        font-weight: 700 !important;
    }
    
    [data-baseweb="notification"] {
        background-color: #2a2a2a !important;
        border-radius: 4px !important;
    }
    
    /* Multiselect - styled */
    [data-baseweb="tag"] {
        background-color: #ff1744 !important;
        color: white !important;
        font-family: 'Roboto Condensed', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 3px !important;
    }
    
    /* Expander - accordion style */
    [data-testid="stExpander"] {
        background-color: #2a2a2a !important;
        border: 2px solid #00e5ff !important;
        border-radius: 4px !important;
    }
    
    /* Dividers - neon lines */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, 
            transparent 0%, 
            #ff1744 20%, 
            #00e5ff 50%, 
            #ff1744 80%, 
            transparent 100%) !important;
        margin: 30px 0 !important;
    }
    
    /* General text */
    p, li, label {
        font-family: 'Roboto Condensed', sans-serif !important;
        color: #e0e0e0 !important;
    }
    
    /* Column borders */
    [data-testid="column"] {
        border: 2px solid #2a2a2a;
        padding: 20px;
        border-radius: 4px;
        background: rgba(26, 26, 26, 0.5);
    }
</style>
"""

st.markdown(punk_css, unsafe_allow_html=True)

# Add header with logo
st.markdown("""
<div style="text-align: center; padding: 20px 0; margin-bottom: 30px;">
    <img src="https://i.postimg.cc/RFc3RLqy/show-brain-logo.png" style="max-width: 400px; width: 100%; margin-bottom: 10px;" alt="Show Brain">
    <p style="font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; color: #00e5ff; letter-spacing: 3px; margin: 10px 0 0 0;">
        BOOKING ANALYZER
    </p>
</div>
""", unsafe_allow_html=True)

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
    
    try:
        worksheet = sh.get_worksheet(1) 
    except:
        worksheet = sh.get_worksheet(0)

    raw_rows = worksheet.get_all_values()
    
    cleaned_data = []
    for row in raw_rows[1:]:
        try:
            def clean_num(val):
                if isinstance(val, str):
                    return val.replace('$', '').replace(',', '').strip()
                return val

            name = row[0]
            if not name: continue 

            c_cost = int(clean_num(row[1]) or 0) if len(row) > 1 else 0
            c_ig = int(clean_num(row[2]) or 0) if len(row) > 2 else 0
            c_assoc = int(clean_num(row[3]) or 0) if len(row) > 3 else 0
            c_spot = int(clean_num(row[7]) or 0) if len(row) > 7 else 0
            c_year = str(row[8]).strip() if len(row) > 8 and row[8].strip() != "" else "2025"

            cleaned_data.append({
                "name": name,
                "cost": c_cost,
                "ig": c_ig,
                "assoc_ig": c_assoc,
                "spotify": c_spot,
                "year": c_year
            })
        except Exception:
            continue
            
    return pd.DataFrame(cleaned_data)

def add_artist_to_sheet(name, cost, ig, assoc_ig, spotify, year):
    """Appends a new artist to the Log Sheet with Year."""
    client = get_connection()
    sheet_url = "https://docs.google.com/spreadsheets/d/1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ/edit?usp=drivesdk"
    sh = client.open_by_url(sheet_url)
    
    try:
        worksheet = sh.get_worksheet(1)
    except:
        worksheet = sh.get_worksheet(0)
    
    new_row = [name, cost, ig, assoc_ig, "", "", "", spotify, year]
    worksheet.append_row(new_row)
    st.cache_data.clear()

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
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ CONFIGURATION")

config_year = st.sidebar.selectbox(
    "PRIMARY YEAR",
    options=["2026", "2025", "2000"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 💰 BUDGETS")
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
with st.sidebar.expander("➕ ADD NEW ARTIST"):
    with st.form("add_artist_form"):
        new_name = st.text_input("Band Name")
        new_base_cost = st.number_input("Cost ($)", min_value=0, value=0)
        new_base_ig = st.number_input("IG Followers", min_value=0, value=0)
        new_base_assoc = st.number_input("Assoc. IG", min_value=0, value=0)
        new_base_spot = st.number_input("Spotify", min_value=0, value=0)
        
        year_options = ["2026", "2025", "2000"]
        default_index = year_options.index(config_year) if config_year in year_options else 0
        new_year = st.selectbox("Year", year_options, index=default_index)
        
        submitted = st.form_submit_button("SAVE TO SHEET")
        if submitted:
            if new_name:
                with st.spinner("Saving..."):
                    try:
                        add_artist_to_sheet(new_name, new_base_cost, new_base_ig, new_base_assoc, new_base_spot, new_year)
                        st.success(f"Added {new_name} ({new_year})! Refreshing...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Name required.")

# -----------------------------------------------------------------------------
# MAIN AREA
# -----------------------------------------------------------------------------
try:
    df = get_data()
    
    if not df.empty:
        available_years = sorted(df['year'].unique())
        
        if config_year not in available_years and available_years:
             default_view = available_years 
        else:
             default_view = [config_year]

        selected_years = st.multiselect(
            "🎯 FILTER VIEW BY YEAR", 
            options=available_years, 
            default=default_view
        )
        
        if selected_years:
            df_filtered = df[df['year'].isin(selected_years)]
        else:
            df_filtered = df 
            
        if not df_filtered.empty:
            artist_names = sorted(df_filtered['name'].unique().tolist())
            selected_artist_name = st.selectbox("🎤 SELECT AN ARTIST", artist_names)
            
            artist_rows = df_filtered[df_filtered['name'] == selected_artist_name]
            
            avg_cost = int(artist_rows['cost'].mean())
            curr_ig = int(artist_rows['ig'].max())
            curr_assoc = int(artist_rows['assoc_ig'].max())
            curr_spot = int(artist_rows['spotify'].max())
            
            years_found = sorted(artist_rows['year'].unique().tolist())
            year_label = ", ".join(years_found)

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📝 EDIT ARTIST DATA")
                
                calc_cost = st.number_input("Avg Cost ($)", value=avg_cost)
                calc_ig = st.number_input("IG Followers", value=curr_ig)
                calc_assoc_ig = st.number_input("Assoc IG", value=curr_assoc)
                calc_spotify = st.number_input("Spotify", value=curr_spot)
                
                if len(artist_rows) > 1:
                    st.info(f"📊 Avg Cost / Max Socials from: {year_label}")
                else:
                    st.caption(f"📅 Record Year: {year_label}")

            total_ig = calc_ig + calc_assoc_ig
            eff_divisor = calc_cost if calc_cost > 0 else 1
            cost_efficiency = total_ig / eff_divisor
            marketing_strength = get_marketing_strength(total_ig)
            donation_strength = get_donation_strength(calc_spotify)
            total_strength = marketing_strength + donation_strength
            bill_label, bill_tier = get_bill_potential_and_label(total_strength)
            affordability = check_affordability(bill_label, calc_cost, assumptions)

            with col2:
                st.markdown("### 🔥 RESULTS")
                st.metric("TOTAL IG REACH", f"{total_ig:,.0f}")
                st.metric("IG PER DOLLAR", f"{cost_efficiency:,.0f}")
                
                st.markdown("#### ⚡ STRENGTH BREAKDOWN")
                c1, c2, c3 = st.columns(3)
                c1.metric("Marketing", marketing_strength)
                c2.metric("Draw", donation_strength)
                c3.metric("Total", total_strength)
                
                st.markdown(f"### 🎯 BILL POTENTIAL: **{bill_label.upper()}**")
                
                if affordability == "Yes":
                    st.success(f"✅ **AFFORDABLE** (within ${assumptions[bill_label]} budget)")
                else:
                    st.error(f"❌ **OVER BUDGET** (exceeds ${assumptions[bill_label]} budget)")
        else:
            st.warning(f"No artists found for years: {', '.join(selected_years)}")
    else:
        st.warning("No data found in the second tab. Please check your sheet tabs.")

except Exception as e:
    st.error(f"Connection Error: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; opacity: 0.6;">
    <p style="font-family: 'Roboto Condensed', sans-serif; font-size: 0.9rem; letter-spacing: 2px;">
        SHOW BRAIN BOOKING ANALYZER
    </p>
</div>
""", unsafe_allow_html=True)
