import streamlit as st
import pandas as pd

# Page configuration for a wider layout
st.set_page_config(layout="wide")

st.title("🌱 Farm Data Visualization & Water Efficiency Dashboard")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Farm Data Inputs")

starting_water = st.sidebar.number_input("Starting Water Consumption (kL):", min_value=0.0, format="%.2f", value=564.0)
current_water = st.sidebar.number_input("Current Water Consumption (kL):", min_value=0.0, format="%.2f", value=431.0)

st.sidebar.divider()

st.sidebar.header("Water Credit Settings")
water_credit_value = st.sidebar.slider("1 Water Credit = (m³)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)

st.sidebar.divider()

st.sidebar.header("Crop Configuration")
num_crops_input = st.sidebar.text_input("Enter amount of crops grown (1-15 digits):", value="2")

# Validate the 1-15 digits constraint
if num_crops_input.isdigit() and 1 <= len(num_crops_input) <= 15:
    num_crops = int(num_crops_input)
    
    # Limit UI rendering loop for practicality if the number is excessively large
    render_limit = min(num_crops, 50)
    if num_crops > 50:
        st.sidebar.warning("Large number entered. Displaying input fields for the first 50 crops.")

    crop_data = []
    
    # Streamlined crop inputs with inline side-by-side layout to reduce visual clutter
    with st.sidebar.expander("📋 Manage Crop Details", expanded=True):
        for i in range(render_limit):
            default_name = "tomato" if i == 0 else ("dates" if i == 1 else f"Crop {i+1}")
            default_water = 119.0 if i == 0 else (210.0 if i == 1 else 100.0)
            
            st.markdown(f"**Crop {i+1}**")
            
            # Inline row for Name
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("<p style='padding-top:8px; font-size:14px;'>Name</p>", unsafe_allow_html=True)
            with c2:
                crop_name = st.text_input(f"Name_{i}", value=default_name, key=f"name_{i}", label_visibility="collapsed")
            
            # Inline row for Water
            c3, c4 = st.columns([1, 2])
            with c3:
                st.markdown("<p style='padding-top:8px; font-size:14px;'>Water (kL)</p>", unsafe_allow_html=True)
            with c4:
                crop_water = st.number_input(f"Water_{i}", min_value=0.0, value=default_water, key=f"water_{i}", label_visibility="collapsed")
            
            if i < render_limit - 1:
                st.divider()
            
            final_name = crop_name if crop_name.strip() else f"Crop {i+1}"
            crop_data.append({"Crop": final_name, "Water Consumption (kL)": crop_water})

    # --- STATE INITIALIZATION FOR TIERS ---
    if "tier_df" not in st.session_state:
        st.session_state.tier_df = pd.DataFrame([
            {"Tier": "Tier 1", "Range": "0 - 20%", "Multiplier": 1.0},
            {"Tier": "Tier 2", "Range": "21 - 40%", "Multiplier": 1.5},
            {"Tier": "Tier 3", "Range": "41 - 60%", "Multiplier": 2.0},
        ])

    df = pd.DataFrame(crop_data)
    efficient_baseline = df["Water Consumption (kL)"].sum()

    # =========================================================================
    # 1. CHARTS FIRST
    # =========================================================================
    st.subheader("📊 Visual Analytics & Comparisons")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**📉 Water Consumption by Crop**")
        chart_df = df.set_index("Crop")
        st.bar_chart(chart_df, horizontal=True, height=210)

    with chart_col2:
        st.markdown("**📊 Performance Comparison**")
        macro_df = pd.DataFrame({
            "Metric": ["Starting", "Current", "Target"],
            "Water (kL)": [starting_water, current_water, efficient_baseline]
        }).set_index("Metric")
        st.bar_chart(macro_df, horizontal=True, height=210)

    st.write("---")

    # =========================================================================
    # 2. TIERS TABLE SECOND
    # =========================================================================
    st.subheader("⚙️ Efficiency Tiers Settings")
    st.session_state.tier_df = st.data_editor(
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
        height="content",
        hide_index=True,
        num_rows="fixed"
    )

    st.write("---")

    # =========================================================================
    # 3. VALUES AND EVERYTHING ELSE THIRD
    # =========================================================================
    # --- CALCULATIONS ---
    water_saved_kl = max(0.0, starting_water - current_water)
    water_saved_m3 = water_saved_kl  
    
    if starting_water > 0:
        water_savings_pct = (water_saved_kl / starting_water) * 100
    else:
        water_savings_pct = 0.0

    # Extract multipliers safely from the updated session state table
    active_tier_df = st.session_state.tier_df
    try:
        tier_1_mult = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 1", "Multiplier"].iloc[0])
        tier_2_mult = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 2", "Multiplier"].iloc[0])
        tier_3_mult = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 3", "Multiplier"].iloc[0])
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

    # Visual Water Savings Progress Card
    with st.container(border=True):
        st.subheader("🎯 Visual Water Savings Progress (Target Max: 60%)")
        
        progress_val = min(1.0, max(0.0, water_savings_pct / 60.0))
        st.markdown(f"**Water Reduction Progress: {water_savings_pct:,.2f}% Saved**")
        st.progress(progress_val)
        
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        b_col1.metric("Original (Starting)", f"{starting_water:,.2f} kL")
        b_col2.metric("Current Use", f"{current_water:,.2f} kL")
        b_col3.metric("Water Saved", f"{water_saved_kl:,.2f} kL")
        b_col4.metric("Efficient Target", f"{efficient_baseline:,.2f} kL", help="Sum of crop water consumptions")

    st.write("") # Small spacer between cards

    # Financial Rewards & Active Tiers Card
    with st.container(border=True):
        st.subheader("💰 Financial Rewards & Active Tiers")
        
        fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
        fin_col1.metric("🏆 Active Tier", current_tier)
        fin_col2.metric("⚡ Multiplier", f"{tier_multiplier}x")
        fin_col3.metric("Water Credits", f"{water_credits:,.2f}")
        fin_col4.metric("Credits Value", f"AED {water_credits_value:,.2f}")

    st.write("---")

    # Crop Data Table (Formatted with 1, 2, 3... index column)
    st.subheader("📋 Crop Data Table")
    display_df = df.copy()
    display_df.insert(0, "No.", range(1, len(display_df) + 1))
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.sidebar.error("Please enter a valid number containing between 1 and 15 digits.")
    st.sidebar.warning("👈 Please enter a valid number of crops in the sidebar to view the dashboard.")
