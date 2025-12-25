import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION & DATA LOADING ---
# Your specific link with the correct GID (sheet ID) for the analysis tab
SHEET_ID = "1rXgY7ZLw9wsnJIAopV6XWG41uJhXkKNrLQTvY8OH1m8"
GID = "2125624029"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=300)
def load_data():
    data = pd.read_csv(SHEET_URL)
    # Filter out empty rows where Artist Name (Column A) is missing
    return data.dropna(subset=[data.columns[0]])

try:
    df = load_data()
except Exception as e:
    st.error("⚠️ Connection Error: Please ensure your Google Sheet sharing is set to 'Anyone with the link can view'.")
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
artist_list = ["+ Add New Artist"] + df.iloc[:, 0].tolist()
selected_artist = st.selectbox("Search for an Artist in the Sheet:", artist_list)

# --- 4. DATA MAPPING & FORM ---
# Spreadsheet Columns: A=0 (Artist), C=2 (IG), D=3 (Assoc IG), H=7 (Spotify), J=9 (Avg Cost)
if selected_artist == "+ Add New Artist":
    name = st.text_input("New Artist Name")
    ig = st.number_input("IG Followers", value=0)
    assoc_ig = st.number_input("Associated IG Followers", value=0)
    spotify = st.number_input("Spotify Monthlies", value=0)
    cost = st.number_input("Average Cost ($)", value=0)
else:
    row = df[df.iloc[:, 0] == selected_artist].iloc[0]
    name = selected_artist
    
    # helper to clean data values
    def clean(val):
        try: return int(float(str(val).replace(',', '').replace('$', ''))) if pd.notnull(val) else 0
        except: return 0

    ig = st.number_input("IG Followers", value=clean(row.iloc[2]))
    assoc_ig = st.number_input("Associated IG Followers", value=clean(row.iloc[3]))
    spotify = st.number_input("Spotify Monthlies", value=clean(row.iloc[7]))
    cost = st.number_input("Average Cost ($)", value=clean(row.iloc[9]))

# --- 5. CALCULATION LOGIC ---
def score_metric(val):
    if val > 50000: return 5
    elif val > 20000: return 4
    elif val > 10000: return 3
    elif val > 5000: return 2
    return 1

total_strength = score_metric(ig + assoc_ig) + score_metric(spotify)

# Determine Bill Potential
if total_strength >= 8: bill = "Headliner"
elif total_strength >= 6: bill = "Direct Support"
elif total_strength >= 3: bill = "Indirect Support"
else: bill = "Opener"

affordable = cost <= budgets[bill]

# --- 6. DISPLAY RESULTS ---
st.divider()
st.subheader(f"Results for {name}")

c1, c2 = st.columns(2)
c1.metric("Strength Score", f"{total_strength}/10")
c1.metric("Bill Placement", bill)

if affordable:
    st.success(f"✅ AFFORDABLE\nFits {bill} budget of ${budgets[bill]}")
else:
    st.error(f"❌ OVER BUDGET\nExceeds {bill} budget by ${cost - budgets[bill]}")
