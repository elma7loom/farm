import streamlit as st
import pandas as pd

# Page configuration for a wider layout
st.set_page_config(layout="wide", page_title="Farm Data & Digital Falaj Dashboard")

st.title("🌱 Farm Data Visualization & Digital Falaj Network")

# --- SIDEBAR MODE SWITCHER (Mutual Exclusion: Only one open at a time) ---
st.sidebar.markdown("### 🎛️ Dashboard Control Panel")
sidebar_mode = st.sidebar.radio(
    "Select Active Workflow:",
    ["Standard Crop Inputs", "🌴 Digital Falaj Network (ICBA)"],
    label_visibility="collapsed"
)

st.sidebar.divider()

if sidebar_mode == "Standard Crop Inputs":
    # =========================================================================
    # SIDEBAR: STANDARD CROP INPUTS
    # =========================================================================
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
        render_limit = min(num_crops, 50)
        if num_crops > 50:
            st.sidebar.warning("Large number entered. Displaying input fields for the first 50 crops.")

        crop_data = []
        with st.sidebar.expander("📋 Manage Crop Details", expanded=True):
            for i in range(render_limit):
                default_name = "tomato" if i == 0 else ("dates" if i == 1 else f"Crop {i+1}")
                default_water = 119.0 if i == 0 else (210.0 if i == 1 else 100.0)
                
                st.markdown(f"**Crop {i+1}**")
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown("<p style='padding-top:8px; font-size:14px;'>Name</p>", unsafe_allow_html=True)
                with c2:
                    crop_name = st.text_input(f"Name_{i}", value=default_name, key=f"name_{i}", label_visibility="collapsed")
                
                c3, c4 = st.columns([1, 2])
                with c3:
                    st.markdown("<p style='padding-top:8px; font-size:14px;'>Water (kL)</p>", unsafe_allow_html=True)
                with c4:
                    crop_water = st.number_input(f"Water_{i}", min_value=0.0, value=default_water, key=f"water_{i}", label_visibility="collapsed")
                
                if i < render_limit - 1:
                    st.divider()
                
                final_name = crop_name if crop_name.strip() else f"Crop {i+1}"
                crop_data.append({"Crop": final_name, "Water Consumption (kL)": crop_water})

        # Updated default multipliers to 2.0, 2.5, and 3.0
        if "tier_df" not in st.session_state:
            st.session_state.tier_df = pd.DataFrame([
                {"Tier": "Tier 1", "Range": "0 - 20%", "Multiplier": 2.0},
                {"Tier": "Tier 2", "Range": "21 - 40%", "Multiplier": 2.5},
                {"Tier": "Tier 3", "Range": "41 - 60%", "Multiplier": 3.0},
            ])

        df = pd.DataFrame(crop_data)
        efficient_baseline = df["Water Consumption (kL)"].sum()

    else:
        st.sidebar.error("Please enter a valid number containing between 1 and 15 digits.")

else:
    # =========================================================================
    # SIDEBAR: DIGITAL FALAJ NETWORK (3-QUESTION APPROACH)
    # =========================================================================
    st.sidebar.header("🌴 Digital Falaj Setup")
    st.sidebar.markdown("*Simulated via ICBA & ADFSC research baselines.*")
    
    num_palms = st.sidebar.number_input("1. Number of Date Palms:", min_value=100, max_value=50000, value=2500, step=100)
    current_litres_per_tree = st.sidebar.slider("2. Current Watering Rate (Litres/Day/Tree):", min_value=100.0, max_value=400.0, value=275.0, step=5.0)
    water_source = st.sidebar.selectbox("3. Water Source:", ["Network (Subsidized)", "Own Well"])
    
    st.sidebar.divider()
    st.sidebar.header("⚙️ Economics & Credits")
    install_cost = st.sidebar.number_input("Infrastructure Setup Cost (AED):", min_value=10000.0, max_value=1000000.0, value=150000.0, step=10000.0)
    falaj_credit_price = st.sidebar.slider("Credit Price Sweet Spot (AED/cube):", min_value=2.0, max_value=5.0, value=2.5, step=0.1)


# =========================================================================
# MAIN BODY RENDERING
# =========================================================================
if sidebar_mode == "Standard Crop Inputs" and 'df' in locals():
    # --- RENDER STANDARD DASHBOARD ---
    st.subheader("📊 Visual Analytics & Comparisons")
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("**📉 Water Consumption by Crop**")
        st.bar_chart(df.set_index("Crop"), horizontal=True, height=210)

    with chart_col2:
        st.markdown("**📊 Performance Comparison**")
        macro_df = pd.DataFrame({
            "Metric": ["Starting", "Current", "Target"],
            "Water (kL)": [starting_water, current_water, efficient_baseline]
        }).set_index("Metric")
        st.bar_chart(macro_df, horizontal=True, height=210)

    st.write("---")
    st.subheader("⚙️ Efficiency Tiers Settings")
    st.session_state.tier_df = st.data_editor(
        st.session_state.tier_df,
        column_config={
            "Multiplier": st.column_config.NumberColumn(
                "Multiplier", 
                min_value=1.0, 
                max_value=5.0,  # Expanded to allow values up to 5.0 (accommodating 3.0+)
                step=0.1, 
                format="%.1f"
            )
        },
        disabled=["Tier", "Range"], use_container_width=True, height="content", hide_index=True, num_rows="fixed"
    )

    st.write("---")
    water_saved_kl = max(0.0, starting_water - current_water)
    water_savings_pct = (water_saved_kl / starting_water) * 100 if starting_water > 0 else 0.0

    active_tier_df = st.session_state.tier_df
    try:
        t1_m = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 1", "Multiplier"].iloc[0])
        t2_m = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 2", "Multiplier"].iloc[0])
        t3_m = float(active_tier_df.loc[active_tier_df["Tier"] == "Tier 3", "Multiplier"].iloc[0])
    except Exception:
        t1_m, t2_m, t3_m = 2.0, 2.5, 3.0

    if 0 <= water_savings_pct <= 20:
        current_tier, tier_multiplier = "Tier 1 (0-20%)", t1_m
    elif 20 < water_savings_pct <= 40:
        current_tier, tier_multiplier = "Tier 2 (21-40%)", t2_m
    else:
        current_tier, tier_multiplier = "Tier 3 (41-60%)", t3_m

    water_credits = water_saved_kl / water_credit_value if water_credit_value > 0 else 0.0
    water_credits_value = water_credits * tier_multiplier

    with st.container(border=True):
        st.subheader("🎯 Visual Water Savings Progress")
        st.progress(min(1.0, max(0.0, water_savings_pct / 60.0)))
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Original (Starting)", f"{starting_water:,.2f} kL")
        b2.metric("Current Use", f"{current_water:,.2f} kL")
        b3.metric("Water Saved", f"{water_saved_kl:,.2f} kL")
        b4.metric("Efficient Target", f"{efficient_baseline:,.2f} kL")

    with st.container(border=True):
        st.subheader("💰 Financial Rewards & Active Tiers")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("🏆 Active Tier", current_tier)
        f2.metric("⚡ Multiplier", f"{tier_multiplier}x")
        f3.metric("Water Credits", f"{water_credits:,.2f}")
        f4.metric("Credits Value", f"AED {water_credits_value:,.2f}")

elif sidebar_mode == "🌴 Digital Falaj Network (ICBA)":
    # --- RENDER DIGITAL FALAJ NETWORK DASHBOARD ---
    st.subheader("🌾 Digital Falaj Network: Farm Story & Subsidy Analysis")
    st.markdown("Evaluating your date palm farm through international **Water Benefit Standard** principles, factoring in ICBA sap flow metrics, soil preservation, and the national subsidy gap.")

    # Calculations
    baseline_kL = (num_palms * current_litres_per_tree * 365) / 1000.0
    efficient_litres_per_tree = 150.0  # ICBA science baseline including salt leaching
    efficient_kL = (num_palms * efficient_litres_per_tree * 365) / 1000.0
    
    raw_savings_kL = max(0.0, baseline_kL - efficient_kL)
    verified_savings_kL = raw_savings_kL * 0.9  # Conservativeness discount factor
    
    yearly_income = verified_savings_kL * falaj_credit_price
    payback_years = install_cost / yearly_income if yearly_income > 0 else 0.0
    state_subsidy_saved = verified_savings_kL * 7.0  # 10 AED true cost minus 3 AED tariff

    # Metrics layout
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Baseline Consumption", f"{baseline_kL:,.0f} m³/yr", f"{current_litres_per_tree} L/day/tree")
    m2.metric("Efficient Target (ICBA)", f"{efficient_kL:,.0f} m³/yr", f"{efficient_litres_per_tree} L/day/tree")
    m3.metric("Verified Savable Water", f"{verified_savings_kL:,.0f} Credits", "Locked at entry")
    m4.metric("Yearly Credit Income", f"AED {yearly_income:,.2f}", f"at {falaj_credit_price} AED/credit")

    st.write("")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.subheader("💰 Payback Stream (7-Year Window)")
            st.markdown(f"""
            - **Setup Capital:** AED {install_cost:,.2f}
            - **Calculated Payback:** **{payback_years:.1f} Years** if calculated... wait, let's look at variable name: `payback_years`
            - *Note:* Structured to recover solar, treatment, and infrastructure expenses quickly, turning into long-term surplus revenue.
            """)
            
    with col_b:
        with st.container(border=True):
            st.subheader("🌍 The Soil & Country Lines")
            st.markdown(f"""
            - **🌱 The Soil Line:** Halting overwatering stabilizes soil salinity, keeping the land productive for the next generation.
            - **🏛️ The Country Line:** Frees up state production subsidies, saving the government ~7 AED per cube (**AED {state_subsidy_saved:,.2f}/year**).
            """)

    st.write("---")
    st.subheader("📊 The Water Economy Scale (AED per Cubic Metre)")
    st.markdown("The 3-point economic reality: the user tariff bill (~3 AED), the true production cost (~10 AED), and the credit sweet spot sitting right between them.")
    
    economy_df = pd.DataFrame({
        "Economic Tier": ["User Tariff Bill", "Credit Sweet Spot", "True Production Cost"],
        "AED / m³": [3.0, falaj_credit_price, 10.0]
    }).set_index("Economic Tier")
    
    st.bar_chart(economy_df, horizontal=True, height=200)
    
    st.info("💡 **Local Standard Rule:** Water savings carry strict regional value. A cube conserved in the UAE means something a cube saved elsewhere does not.")
