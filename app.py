import streamlit as st
import pandas as pd

# --- 1. DATA LOADING ---
SHEET_ID = "1rXgY7ZLw9wsnJIAopV6XWG41uJhXkKNrLQTvY8OH1m8"
GID = "2125624029"
# Using the /pub export format for better stability
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    # Load the sheet and find where the actual data starts
    raw_df = pd.read_csv(SHEET_URL)
    
    # Clean up: Find the first row that actually contains "Artist" or "Headliner"
    # To ensure we get column A, we'll look for the column that has 'Artist' in the header
    return raw_df

try:
    df = load_data()
    # Find the correct column indices based on your sheet's headers
    # We'll use the column names directly to avoid index shifting
    artist_col = df.columns[0]   # Column A
    ig_col = df.columns[2]       # Column C
    assoc_col = df.columns[3]    # Column D
    spotify_col = df.columns[7]  # Column H
    cost_col = df.columns[9]     # Column J
except Exception as e:
    st.error("Sheet Error: Please make sure 'Anyone with the link' can View.")
    st.stop()

st.title("🎸 Band Affordability Scout")

# --- 2. SIDEBAR BUDGETS ---
st.sidebar.header("Configure Budgets")
budgets = {
    "Headliner": st.sidebar.number_input("Headliner Max ($)", value=600),
    "Direct Support": st.sidebar.number_input("Direct Support Max ($)", value=200),
    "Indirect Support": st.sidebar.number_input("Indirect Support Max ($)", value=100),
    "Opener": st.sidebar.number_input("Opener Max ($)", value=0)
}

# --- 3. ARTIST SELECTION ---
# We filter out any rows where the Artist name is a number or a formula error
clean_artist_list = df[artist_col].dropna().astype(str).tolist()
# Filter out "Header" text if it accidentally got pulled in
clean_artist_list = [x for x in clean_artist_list if x not in ["Artist", "nan", "0"]]

artist_choice = st.selectbox("Select an Artist:", ["+ Add New Artist"] + clean_artist_list)

# --- 4. DATA INPUTS ---
if artist_choice == "+ Add New Artist":
    name = st.text_input("New Artist Name")
    ig = st.number_input("IG Followers", value=0)
    assoc_ig = st.number_input("Associated IG", value=0)
    spotify = st.number_input("Spotify Monthlies", value=0)
    cost = st.number_input("Average Cost ($)", value=0)
else:
    # Find the specific row for that artist
    row = df[df[artist_col] == artist_choice].iloc[0]
    name = artist_choice
    
    def to_int(val):
        try:
            if pd.isna(val): return 0
            return int(float(str(val).replace(',', '').replace('$', '')))
        except: return 0

    ig = st.number_input("IG Followers", value=to_int(row[ig_col]))
    assoc_ig = st.number_input("Associated IG", value=to_int(row[assoc_col]))
    spotify = st.number_input("Spotify Monthlies", value=to_int(row[spotify_col]))
    cost = st.number_input("Average Cost ($)", value=to_int(row[cost_col]))

# --- 5. LOGIC ---
def score_metric(val):
    if val > 50000: return 5
    elif val > 20000: return 4
    elif val > 10000: return 3
    elif val > 5000: return 2
    return 1

total_strength = score_metric(ig + assoc_ig) + score_metric(spotify)

if total_strength >= 8: bill = "Headliner"
elif total_strength >= 6: bill = "Direct Support"
elif total_strength >= 3: bill = "Indirect Support"
else: bill = "Opener"

# Check affordability
max_allowed = budgets[bill]
affordable = cost <= max_allowed

# --- 6. DISPLAY ---
st.divider()
col1, col2 = st.columns(2)
col1.metric("Strength", f"{total_strength}/10")
col1.metric("Placement", bill)

if affordable:
    st.success(f"✅ AFFORDABLE\nFits {bill} budget of ${max_allowed}")
else:
    st.error(f"❌ OVER BUDGET\nExceeds {bill} budget by ${cost - max_allowed}")
