import streamlit as st
import pandas as pd

# --- 1. DATA LOADING ---
# New Sheet ID from your latest link
SHEET_ID = "1CSOn7X-pL_WACa-RloS7g_rgxVwd6e_DkZbsax7liGQ"
# Using /export?format=csv pulls the first sheet (Sheet2) automatically
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    # Load the CSV data
    data = pd.read_csv(SHEET_URL)
    # Ensure we only keep rows where there is an actual artist name
    return data.dropna(subset=[data.columns[0]])

try:
    df = load_data()
    # [span_2](start_span)Based on your sheet structure[span_2](end_span):
    # Col 0: Band Name
    # Col 1: Average Cost
    # Col 2: IG Followers
    # Col 3: Associated IG Followers
    # Col 7: Spotify Listeners
except Exception as e:
    st.error("Connection Error: Please ensure your Google Sheet sharing is set to 'Anyone with the link can view'.")
    st.stop()

st.set_page_config(page_title="Band Scout", layout="centered")
st.title("🎸 Band Affordability Scout")

# --- 2. SIDEBAR BUDGET CONFIG ---
st.sidebar.header("Configure Budgets")
budgets = {
    "Headliner": st.sidebar.number_input("Headliner Max ($)", value=600),
    "Direct Support": st.sidebar.number_input("Direct Support Max ($)", value=200),
    "Indirect Support": st.sidebar.number_input("Indirect Support Max ($)", value=100),
    "Opener": st.sidebar.number_input("Opener Max ($)", value=0)
}

# --- 3. ARTIST SELECTION ---
# Fixed: Get unique names from Column 0 and remove header text if present
artist_list = df.iloc[:, 0].astype(str).tolist()
artist_list = [a for a in artist_list if a not in ["Band Name", "Artist", "nan"]]
selected_artist = st.selectbox("Search for an Artist:", ["+ Add New Artist"] + sorted(artist_list))

# --- 4. FORM LOGIC ---
if selected_artist == "+ Add New Artist":
    name = st.text_input("New Artist Name")
    ig = st.number_input("IG Followers", value=0)
    assoc_ig = st.number_input("Associated IG", value=0)
    spotify = st.number_input("Spotify Monthlies", value=0)
    cost = st.number_input("Average Cost ($)", value=0)
else:
    # Match the row by name
    row = df[df.iloc[:, 0] == selected_artist].iloc[0]
    name = selected_artist
    
    def clean_num(val):
        try:
            return int(float(str(val).replace(',', '').replace('$', ''))) if pd.notnull(val) else 0
        except: return 0

    # [span_3](start_span)Map to columns[span_3](end_span)
    cost = st.number_input("Average Cost ($)", value=clean_num(row.iloc[1]))
    ig = st.number_input("IG Followers", value=clean_num(row.iloc[2]))
    assoc_ig = st.number_input("Associated IG", value=clean_num(row.iloc[3]))
    spotify = st.number_input("Spotify Monthlies", value=clean_num(row.iloc[7]))

# --- 5. CALCULATION LOGIC ---
def score_metric(val):
    if val > 50000: return 5
    elif val > 20000: return 4
    elif val > 10000: return 3
    elif val > 5000: return 2
    return 1

# [span_4](start_span)Logic based on spreadsheet strength totals[span_4](end_span)
total_strength = score_metric(ig + assoc_ig) + score_metric(spotify)

if total_strength >= 8: bill = "Headliner"
elif total_strength >= 6: bill = "Direct Support"
elif total_strength >= 3: bill = "Indirect Support"
else: bill = "Opener"

is_affordable = cost <= budgets[bill]

# --- 6. RESULTS DISPLAY ---
st.divider()
st.subheader(f"Analysis: {name}")

c1, c2 = st.columns(2)
c1.metric("Strength Score", f"{total_strength}/10")
c1.metric("Placement", bill)

if is_affordable:
    st.success(f"✅ AFFORDABLE: Fits the {bill} budget of ${budgets[bill]}.")
else:
    st.error(f"❌ TOO EXPENSIVE: Exceeds the {bill} budget by ${cost - budgets[bill]}.")
