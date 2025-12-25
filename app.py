import streamlit as st

st.title("SB Artist Affordability Calculator")

# --- Configuration Sidebar ---
st.sidebar.header("Budget Configuration")
budgets = {
    "Headliner": st.sidebar.number_input("Headliner Budget ($)", value=600),
    "Direct Support": st.sidebar.number_input("Direct Support Budget ($)", value=200),
    "Indirect Support": st.sidebar.number_input("Indirect Support Budget ($)", value=100),
    "Opener": st.sidebar.number_input("Opener Budget ($)", value=0)
}

# --- Data Input ---
st.header("Band Metrics")
col1, col2 = st.columns(2)

with col1:
    band_name = st.text_input("Band Name", "New Artist")
    avg_cost = st.number_input("Average Cost ($)", min_value=0, value=0)
    ig_followers = st.number_input("IG Followers (Col C)", min_value=0, value=0)

with col2:
    assoc_ig = st.number_input("Associated IG Followers (Col D)", min_value=0, value=0)
    spotify_monthlies = st.number_input("Spotify Monthlies (Col H)", min_value=0, value=0)

# --- Logic Processing ---
# Note: In your sheet, Strength is a tiered score (1-5) based on followers.
# This logic approximates your sheet's scoring system.
def get_score(value):
    if value > 50000: return 5
    if value > 20000: return 4
    if value > 10000: return 3
    if value > 5000: return 2
    return 1

marketing_strength = get_score(ig_followers + assoc_ig)
donation_strength = get_score(spotify_monthlies)
total_strength = marketing_strength + donation_strength

# Determine Bill Potential (Column K)
if total_strength >= 8:
    bill_potential = "Headliner"
elif total_strength >= 6:
    bill_potential = "Direct Support"
elif total_strength >= 3:
    bill_potential = "Indirect Support"
else:
    bill_potential = "Opener"

# Determine Affordability (Column L)
max_budget = budgets[bill_potential]
is_affordable = avg_cost <= max_budget

# --- Results Display ---
st.divider()
st.subheader(f"Analysis for: {band_name}")
res_col1, res_col2, res_col3 = st.columns(3)

res_col1.metric("Total Strength Score", total_strength)
res_col2.metric("Bill Potential", bill_potential)
res_col3.metric("Affordable?", "Yes" if is_affordable else "No", 
                delta=f"${max_budget - avg_cost} margin")

if is_affordable:
    st.success(f"This artist fits within the {bill_potential} budget of ${max_budget}.")
else:
    st.error(f"This artist exceeds the {bill_potential} budget of ${max_budget}.")
