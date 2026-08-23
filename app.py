import streamlit as st
import pandas as pd

# Page configuration for a wider layout
st.set_page_config(layout="wide")

st.title("🌱 Farm Data Visualization & Water Efficiency Dashboard")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Farm Data Inputs")

# Enter the hectares of the farm
hectares = st.sidebar.number_input("Enter the hectares of the farm:", min_value=0.0, format="%.2f")

# Enter actual water consumption for the farm
actual_water = st.sidebar.number_input("Enter actual water consumption for the farm (kL):", min_value=0.0, format="%.2f")

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
    st.sidebar.subheader("Crop Details")

    for i in range(render_limit):
        crop_name = st.sidebar.text_input(f"Crop {i+1} Name", value=f"Crop {i+1}", key=f"name_{i}")
        water_consumption = st.sidebar.number_input(f"Annual Water (kL) for {crop_name}", min_value=0.0, key=f"water_{i}")
        
        crop_data.append({"Crop": crop_name, "Water Consumption (kL)": water_consumption})

    # --- MAIN SCREEN OUTPUTS ---
    df = pd.DataFrame(crop_data)
    
    # Efficient water consumption is the sum of all crop water consumptions
    efficient_water = df["Water Consumption (kL)"].sum()
    
    # Water efficiency gap calculations (Note: 1 kL = 1 m³)
    water_efficiency_gap_kl = actual_water - efficient_water
    water_efficiency_gap_m3 = water_efficiency_gap_kl  
    
    # Water efficiency gap percentage calculation (guarding against division by zero)
    if efficient_water > 0:
        water_efficiency_gap_pct = (water_efficiency_gap_kl / efficient_water) * 100
    else:
        water_efficiency_gap_pct = 0.0

    st.subheader("📊 Summary & Water Efficiency Analysis")
    
    # Display tables and bar chart cleanly on the main screen first so we can extract table values
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("### Crop Data Table")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### Efficiency Tiers (Editable Multipliers)")
        
        # Initialize default editable table data for tiers if not already present
        if "tier_df_state" not in st.session_state:
            st.session_state.tier_df_state = pd.DataFrame([
                {"Tier": "Tier 1", "Range": "0 - 20%", "Multiplier": 1.0},
                {"Tier": "Tier 2", "Range": "21 - 40%", "Multiplier": 1.5},
                {"Tier": "Tier 3", "Range": "41 - 60%", "Multiplier": 2.0},
                {"Tier": "Tier 4", "Range": "61%+", "Multiplier": 2.5},
            ])

        # Editable data table with limits (1.0 to 2.5)
        edited_tier_df = st.data_editor(
            st.session_state.tier_df_state,
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
        
        # Extract multipliers from the user-edited table
        tier_1_mult = edited_tier_df.loc[edited_tier_df["Tier"] == "Tier 1", "Multiplier"].values[0]
        tier_2_mult = edited_tier_df.loc[edited_tier_df["Tier"] == "Tier 2", "Multiplier"].values[0]
        tier_3_mult = edited_tier_df.loc[edited_tier_df["Tier"] == "Tier 3", "Multiplier"].values[0]
        tier_4_mult = edited_tier_df.loc[edited_tier_df["Tier"] == "Tier 4", "Multiplier"].values[0]

    # Determine active tier and multiplier based on efficiency gap percentage
    if 0 <= water_efficiency_gap_pct <= 20:
        current_tier = "Tier 1 (0-20%)"
        tier_multiplier = tier_1_mult
    elif 20 < water_efficiency_gap_pct <= 40:
        current_tier = "Tier 2 (21-40%)"
        tier_multiplier = tier_2_mult
    elif 40 < water_efficiency_gap_pct <= 60:
        current_tier = "Tier 3 (41-60%)"
        tier_multiplier = tier_3_mult
    else:
        current_tier = "Tier 4 (61%+)"
        tier_multiplier = tier_4_mult

    # Calculate final water credits using the base value and active tier multiplier
    base_water_credits = water_efficiency_gap_m3 / water_credit_value if water_credit_value > 0 else 0.0
    water_credits = base_water_credits * tier_multiplier
    
    with right_col:
        st.markdown("### Water Consumption by Crop")
        st.bar_chart(df.set_index("Crop"))

    # Display key metrics across two rows above the tables for clear visibility
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
    row1_col1.metric("Actual Water", f"{actual_water:,.2f} kL")
    row1_col2.metric("Efficient Water", f"{efficient_water:,.2f} kL")
    row1_col3.metric("Gap (kL)", f"{water_efficiency_gap_kl:,.2f} kL")
    row1_col4.metric("Gap (m³)", f"{water_efficiency_gap_m3:,.2f} m³")
    
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
    row2_col1.metric("Gap %", f"{water_efficiency_gap_pct:,.2f}%")
    row2_col2.metric("Active Tier", current_tier)
    row2_col3.metric("Tier Multiplier", f"{tier_multiplier}x")
    row2_col4.metric("Water Credits", f"{water_credits:,.2f}", help=f"Calculated using base credits * {tier_multiplier}x tier multiplier")
    
    st.write(f"**Farm Size:** {hectares} hectares &nbsp;&nbsp;|&nbsp;&nbsp; **Total Crops:** {num_crops}")
    st.write("---")

else:
    st.sidebar.error("Please enter a valid number containing between 1 and 15 digits.")
    st.warning("👈 Please enter a valid number of crops in the sidebar to view the dashboard.")
