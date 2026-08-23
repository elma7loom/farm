import streamlit as st
import pandas as pd

# Page configuration for a wider layout
st.set_page_config(layout="wide")

st.title("🌱 Farm Data Visualization & Water Efficiency Dashboard")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Farm Data Inputs")

# Enter the hectares of the farm
hectares = st.sidebar.number_input("Enter the hectares of the farm:", min_value=0.1, value=1.0, format="%.2f")

# Starting vs Current Water Consumption inputs
starting_water = st.sidebar.number_input("Starting Water Consumption (Before Reduction in kL):", min_value=0.0, format="%.2f")
current_water = st.sidebar.number_input("Current Water Consumption (After Reduction in kL):", min_value=0.0, format="%.2f")

# Water Credit slider configuration
st.sidebar.header("Water Credit Settings")
water_credit_value = st.sidebar.slider("1 Water Credit = (m³)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)

# Blank for amount of crops grown (accepts 1-15 digits)
num_crops_input = st.sidebar.text_input("Enter the amount of crops grown (1-15 digits):", value="1")

# Validate the 1-15 digits constraint
if num_crops_input.isdigit() and 1 <= len(num_crops_input) <= 15:
    num_crops = int(num_crops_input)
    
    # Limit UI rendering loop for practicality if the number is excessively large
    render_limit = min(num_crops, 50)
    if num_crops > 50:
        st.sidebar.warning("Large number entered. Displaying input fields for the first 50 crops.")

    crop_data = []
    st.sidebar.subheader("Crop Details (Per Hectare)")

    for i in range(render_limit):
        crop_name = st.sidebar.text_input(f"Crop {i+1} Name", value=f"Crop {i+1}", key=f"name_{i}")
        crop_water_per_ha = st.sidebar.number_input(f"Water requirement (kL/ha) for {crop_name}", min_value=0.0, key=f"water_{i}")
        
        crop_data.append({"Crop": crop_name, "Water Requirement (kL/ha)": crop_water_per_ha})

    # --- STATE INITIALIZATION FOR TIERS ---
    if "tier_df" not in st.session_state:
        st.session_state.tier_df = pd.DataFrame([
            {"Tier": "Tier 1", "Range": "0 - 20%", "Multiplier": 1.0},
            {"Tier": "Tier 2", "Range": "21 - 40%", "Multiplier": 1.5},
            {"Tier": "Tier 3", "Range": "41 - 60%", "Multiplier": 2.0},
        ])

    # Grab the active tier data instantly from the editor state if available
    active_tier_df = st.session_state.get("tier_editor", st.session_state.tier_df)

    # --- CALCULATIONS ---
    df = pd.DataFrame(crop_data)
    
    # Calculate total efficient water requirement for reference
    df["Total Efficient Water (kL)"] = df["Water Requirement (kL/ha)"] * hectares
    efficient_baseline = df["Total Efficient Water (kL)"].sum()
    
    # Savings calculations (Starting vs Current)
    water_saved_kl = max(0.0, starting_water - current_water)
    water_saved_m3 = water_saved_kl  
    
    if starting_water > 0:
        water_savings_pct = (water_saved_kl / starting_water) * 100
    else:
        water_savings_pct = 0.0

    # Extract multipliers safely from active_tier_df
    try:
        tier_1_mult = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 1", "Multiplier"].values[0])
        tier_2_mult = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 2", "Multiplier"].values[0])
        tier_3_mult = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 3", "Multiplier"].values[0])
    except Exception:
        tier_1_mult, tier_2_mult, tier_3_mult = 1.0, 1.5, 2.0

    # Determine active tier and multiplier (3 tiers only)
    if 0 <= water_savings_pct <= 20:
        current_tier = "Tier 1 (0-20%)"
        tier_multiplier = tier_1_mult
    elif 20 < water_savings_pct <= 40:
        current_tier = "Tier 2 (21-40%)"
        tier_multiplier = tier_2_mult
    else:
        current_tier = "Tier 3 (41-60%)"
        tier_multiplier = tier_3_mult

    # Calculate financial values
    water_credits = water_saved_m3 / water_credit_value if water_credit_value > 0 else 0.0
    water_credits_value = water_credits * tier_multiplier

    # =========================================================================
    # ROW 1: VISUAL PROGRESS BAR & WATER REDUCTION OVERVIEW ALONGSIDE CHART
    # =========================================================================
    st.subheader("🎯 Visual Water Savings Progress")
    
    top_col1, top_col2 = st.columns([1, 1])
    
    with top_col1:
        progress_val = min(1.0, max(0.0, water_savings_pct / 100.0))
        st.markdown(f"**Water Reduction Progress: {water_savings_pct:,.2f}% Saved**")
        st.progress(progress_val)
        
        b_col1, b_col2, b_col3 = st.columns(3)
        b_col1.metric("Original (Starting)", f"{starting_water:,.2f} kL")
        b_col2.metric("Current Use", f"{current_water:,.2f} kL")
        b_col3.metric("Water Saved", f"{water_saved_kl:,.2f} kL")

        ref_col1, ref_col2 = st.columns(2)
        ref_col1.metric("Water Saved (m³)", f"{water_saved_m3:,.2f} m³")
        ref_col2.metric("Efficient Target", f"{efficient_baseline:,.2f} kL", help="Requirement × Hectares (Reference)")

    with top_col2:
        st.markdown("**Efficient Water Requirement by Crop**")
        chart_df = df[["Crop", "Total Efficient Water (kL)"]].set_index("Crop")
        st.bar_chart(chart_df, height=240)

    st.write("---")

    # =========================================================================
    # ROW 2: FINANCIAL REWARDS & ACTIVE TIERS
    # =========================================================================
    st.subheader("💰 Financial Rewards & Active Tiers")
    
    fin_col1, fin_col2 = st.columns(2)
    with fin_col1:
        st.metric("🏆 Active Tier", current_tier)
        st.metric("Water Credits", f"{water_credits:,.2f}")
    with fin_col2:
        st.metric("⚡ Tier Multiplier", f"{tier_multiplier}x")
        st.metric("Credits Value", f"AED {water_credits_value:,.2f}")

    st.write("---")

    # =========================================================================
    # ROW 3: CROP DATA TABLE
    # =========================================================================
    st.subheader("📋 Crop Data Table")
    st.dataframe(df, use_container_width=True)

    st.write("---")

    # =========================================================================
    # ROW 4: EFFICIENCY TIERS TABLE (PLACED AT THE BOTTOM)
    # =========================================================================
    st.subheader("⚙️ Efficiency Tiers (Editable Multipliers)")
    st.markdown("*(Scroll down here anytime you want to customize your tier multiplier values)*")
    
    edited_df = st.data_editor(
        st.session_state.tier_df,
        column_config={
            "Multiplier": st.column_config.NumberColumn(
                "Multiplier",
                min_value=1.0,
                max_value=2.5,
                step=0.1,
                format="%.1f"
            )
        },
        disabled=["Tier", "Range"],
        use_container_width=True,
        key="tier_editor"
    )
    st.session_state.tier_df = edited_df

    st.write("---")
    st.write(f"**Farm Size:** {hectares} hectares &nbsp;&nbsp;|&nbsp;&nbsp; **Total Crops Managed:** {num_crops}")

else:
    st.sidebar.error("Please enter a valid number containing between 1 and 15 digits.")
    st.warning("👈 Please enter a valid number of crops in the sidebar to view the dashboard.")
