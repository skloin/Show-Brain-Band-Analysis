import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# DATA & SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
def get_initial_data():
    # Only return this list if session state is empty
    return [
        {"name": "Bec Lauder and the Noise", "cost": 0, "ig": 140000, "assoc_ig": 0, "spotify": 28400},
        {"name": "Crazy and the Brains", "cost": 0, "ig": 9500, "assoc_ig": 0, "spotify": 20200},
        {"name": "Torture and The Desert Spiders", "cost": 0, "ig": 5300, "assoc_ig": 0, "spotify": 7200},
        {"name": "Puzzled Panther", "cost": 0, "ig": 7500, "assoc_ig": 64400, "spotify": 3600},
        {"name": "Jasno Swarez", "cost": 0, "ig": 16600, "assoc_ig": 0, "spotify": 3000},
        {"name": "Abby Jeane + The Shadow Band", "cost": 0, "ig": 7700, "assoc_ig": 0, "spotify": 2100},
        {"name": "Frida Kill", "cost": 0, "ig": 4300, "assoc_ig": 0, "spotify": 1200},
        {"name": "Two Man Giant Squid", "cost": 0, "ig": 2500, "assoc_ig": 0, "spotify": 900},
        {"name": "Joudy", "cost": 0, "ig": 4200, "assoc_ig": 0, "spotify": 700},
        {"name": "Dog Date", "cost": 0, "ig": 3000, "assoc_ig": 0, "spotify": 700},
        {"name": "Certain Death", "cost": 0, "ig": 2400, "assoc_ig": 0, "spotify": 460},
        {"name": "Crush Fund", "cost": 0, "ig": 4900, "assoc_ig": 0, "spotify": 400},
        {"name": "Adult Human Females", "cost": 0, "ig": 4000, "assoc_ig": 0, "spotify": 200},
        {"name": "Genre Is Death", "cost": 0, "ig": 2600, "assoc_ig": 0, "spotify": 160},
        {"name": "Toxic Tito", "cost": 0, "ig": 3500, "assoc_ig": 57800, "spotify": 100},
        {"name": "Bubbles", "cost": 0, "ig": 1500, "assoc_ig": 0, "spotify": 100},
        {"name": "Slashers", "cost": 0, "ig": 8500, "assoc_ig": 0, "spotify": 72},
        {"name": "Surgeon General", "cost": 0, "ig": 1300, "assoc_ig": 0, "spotify": 50},
        {"name": "Figure Of Fun", "cost": 0, "ig": 800, "assoc_ig": 0, "spotify": 28},
        {"name": "Wifeknife", "cost": 0, "ig": 1300, "assoc_ig": 0, "spotify": 25},
        {"name": "Pons", "cost": 93, "ig": 9800, "assoc_ig": 0, "spotify": 1300},
        {"name": "Tetchy", "cost": 100, "ig": 6900, "assoc_ig": 0, "spotify": 2200},
        {"name": "Pop Music Fever Dream", "cost": 140, "ig": 4100, "assoc_ig": 0, "spotify": 2400},
        {"name": "Big Girl", "cost": 150, "ig": 11800, "assoc_ig": 0, "spotify": 4800},
        {"name": "Desert Sharks", "cost": 150, "ig": 11700, "assoc_ig": 0, "spotify": 4800},
        {"name": "T!LT", "cost": 163, "ig": 4700, "assoc_ig": 0, "spotify": 10700},
        {"name": "Venus Twins", "cost": 175, "ig": 10500, "assoc_ig": 0, "spotify": 1800},
        {"name": "Avishag Rodrigues", "cost": 175, "ig": 4100, "assoc_ig": 0, "spotify": 2500},
        {"name": "Daniel August", "cost": 180, "ig": 200, "assoc_ig": 5200, "spotify": 20},
        {"name": "Tea Eater", "cost": 200, "ig": 4500, "assoc_ig": 0, "spotify": 1400},
        {"name": "Sunshine Spazz", "cost": 213, "ig": 8400, "assoc_ig": 0, "spotify": 3500},
        {"name": "95 Bulls", "cost": 233, "ig": 5200, "assoc_ig": 0, "spotify": 2500},
        {"name": "Um, Jennifer?", "cost": 250, "ig": 15400, "assoc_ig": 0, "spotify": 49100},
        {"name": "Dead Tooth", "cost": 250, "ig": 7300, "assoc_ig": 0, "spotify": 1800},
        {"name": "Skorts", "cost": 258, "ig": 7100, "assoc_ig": 0, "spotify": 14000},
        {"name": "Pinc Louds", "cost": 275, "ig": 25700, "assoc_ig": 0, "spotify": 29800},
        {"name": "Francie Moon", "cost": 275, "ig": 6800, "assoc_ig": 0, "spotify": 1000},
        {"name": "Balaclava", "cost": 300, "ig": 4000, "assoc_ig": 0, "spotify": 300},
        {"name": "The Thing", "cost": 375, "ig": 13300, "assoc_ig": 0, "spotify": 149400},
        {"name": "TVOD", "cost": 400, "ig": 8000, "assoc_ig": 0, "spotify": 4900},
        {"name": "Native Sun", "cost": 475, "ig": 6900, "assoc_ig": 0, "spotify": 8200},
        {"name": "Grace Bergere", "cost": 475, "ig": 3800, "assoc_ig": 0, "spotify": 7200},
        {"name": "Pinklids", "cost": 475, "ig": 2600, "assoc_ig": 0, "spotify": 1100},
        {"name": "Levitation Room", "cost": 500, "ig": 27000, "assoc_ig": 0, "spotify": 189300},
        {"name": "Shilpa Ray", "cost": 500, "ig": 8800, "assoc_ig": 0, "spotify": 27600},
        {"name": "Daddy Long Legs", "cost": 500, "ig": 18300, "assoc_ig": 0, "spotify": 21400},
        {"name": "Dion Lunadon", "cost": 600, "ig": 7500, "assoc_ig": 0, "spotify": 7600},
        {"name": "Soklo", "cost": 600, "ig": 32300, "assoc_ig": 0, "spotify": 1400},
        {"name": "P.H.0", "cost": 600, "ig": 5400, "assoc_ig": 0, "spotify": 800},
        {"name": "Nabihah Iqbal", "cost": 650, "ig": 60200, "assoc_ig": 0, "spotify": 208800},
        {"name": "Fine Mess", "cost": 827, "ig": 4000, "assoc_ig": 265000, "spotify": 2300},
        {"name": "Bodega", "cost": 900, "ig": 21500, "assoc_ig": 0, "spotify": 50200},
        {"name": "Vial", "cost": 1000, "ig": 73400, "assoc_ig": 0, "spotify": 100200},
        {"name": "A Place To Bury Strangers", "cost": 1100, "ig": 57300, "assoc_ig": 0, "spotify": 63900},
        {"name": "The Mystery Lights", "cost": 2100, "ig": 26700, "assoc_ig": 0, "spotify": 591400},
    ]

# Initialize Session State
if 'artists' not in st.session_state:
    st.session_state['artists'] = get_initial_data()

# Helper to add new artist
def add_artist(name, cost, ig, assoc_ig, spotify):
    new_entry = {
        "name": name, 
        "cost": cost, 
        "ig": ig, 
        "assoc_ig": assoc_ig, 
        "spotify": spotify
    }
    st.session_state['artists'].append(new_entry)
    # Rerun logic is automatic in buttons usually, but explicit rerun can ensure UI updates instantly
    # st.experimental_rerun() # Optional, depending on streamlit version

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
st.title("SB Artist Cost Analysis")

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
with st.sidebar.expander("➕ Add New Artist"):
    with st.form("add_artist_form"):
        new_name = st.text_input("Band Name")
        new_base_cost = st.number_input("Cost ($)", min_value=0, value=0)
        new_base_ig = st.number_input("IG Followers", min_value=0, value=0)
        new_base_assoc = st.number_input("Assoc. IG", min_value=0, value=0)
        new_base_spot = st.number_input("Spotify", min_value=0, value=0)
        
        submitted = st.form_submit_button("Add Artist")
        if submitted:
            if new_name:
                add_artist(new_name, new_base_cost, new_base_ig, new_base_assoc, new_base_spot)
                st.success(f"Added {new_name}!")
            else:
                st.error("Please enter a name.")

# --- Main Area ---

# Convert session state list to DataFrame for the dropdown
df = pd.DataFrame(st.session_state['artists'])
artist_names = df['name'].tolist()

# Sort names alphabetically for easier finding, but keep "new" ones visible? 
# Usually alphabetical is best.
artist_names.sort()

# Selector
selected_artist_name = st.selectbox("Select an Artist", artist_names, index=0)

# Get current data for selected artist
# We use the dataframe we just built from session state
artist_row = df[df['name'] == selected_artist_name].iloc[0]

st.markdown("---")
col1, col2 = st.columns(2)

# --- Input Section (Main) ---
with col1:
    st.subheader(f"Edit Values: {selected_artist_name}")
    st.caption("Adjust values here to see how metrics change without saving permanently.")
    
    # Defaults come from the stored data
    calc_cost = st.number_input("Average Cost ($)", value=int(artist_row['cost']))
    calc_ig = st.number_input("IG Followers", value=int(artist_row['ig']))
    calc_assoc_ig = st.number_input("Associated IG Followers", value=int(artist_row['assoc_ig']))
    calc_spotify = st.number_input("Spotify Listeners", value=int(artist_row['spotify']))

# --- Calculation Section ---
# 1. Total IG
total_ig = calc_ig + calc_assoc_ig

# 2. Cost Efficiency (IG per $1)
eff_divisor = calc_cost if calc_cost > 0 else 1
cost_efficiency = total_ig / eff_divisor

# 3. Strength Scores
marketing_strength = get_marketing_strength(total_ig)
donation_strength = get_donation_strength(calc_spotify)
total_strength = marketing_strength + donation_strength

# 4. Placement & Affordability
bill_label, bill_tier = get_bill_potential_and_label(total_strength)
affordability = check_affordability(bill_label, calc_cost, assumptions)

# --- Output Section ---
with col2:
    st.subheader("Analysis Results")
    
    st.metric("Total IG Followers", f"{total_ig:,.0f}")
    
    # Cost Efficiency
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

st.markdown("---")
st.caption("Data stored in temporary session. Refreshing the page will reset to default artists.")
