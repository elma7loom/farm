import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Water Credit Farm Simulator", layout="wide")

st.title("🌾 Interactive Water Credit Farm Simulator")
st.markdown("Designed for Judges & Investors: Test how farm size, crop selection, and water-saving tiers impact water credits and financial revenue (**3.13 AED per credit**), ensuring smallholders are fully protected.")

# Sidebar / Input Section
st.sidebar.header("🎛️ Simulation Controls")

# Crop defaults (annual m3 per hectare)
crop_defaults = {
    "Palm Tree": 22000,
    "Cherry Tomato": 9000,
    "Potato": 6500,
    "Wheat": 4500
}

selected_crop = st.sidebar.selectbox("Select Crop Type", list(crop_defaults.keys()))
default_water = crop_defaults[selected_crop]

base_water_rate = st.sidebar.number_input(
    "Base Annual Water Consumption (m³ per hectare)",
    min_value=1000, max_value=50000, value=default_water, step=500,
    help="Annual water usage per hectare for the chosen crop."
)

farm_area = st.sidebar.slider(
    "Farm Area (Hectares)",
    min_value=1.0, max_value=150.0, value=5.0, step=1.0,
    help="Total land area of the example farm."
)

water_saved_pct = st.sidebar.slider(
    "Water Saved Percentage (%)",
    min_value=0.0, max_value=20.0, value=12.0, step=0.5,
    help="Percentage reduction in water use compared to the regional baseline."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Small Farm Protection Settings")
small_farm_threshold = st.sidebar.slider(
    "Small Farm Threshold (Hectares)",
    min_value=2.0, max_value=20.0, value=10.0, step=1.0,
    help="Farms at or below this size are classified as smallholders."
)

is_small_farm = farm_area <= small_farm_threshold

small_farm_multiplier = st.sidebar.slider(
    "Smallholder Bonus Multiplier",
    min_value=1.0, max_value=3.0, value=1.5, step=0.1,
    help="Bonus multiplier applied to small farms to ensure equitable earnings."
)

# --- Calculations ---
total_baseline_water = farm_area * base_water_rate
water_saved_m3 = total_baseline_water * (water_saved_pct / 100.0)

# Stepped Tiers for Water Saving Efficiency
if water_saved_pct <= 5:
    tier_name = "Tier 1 (0-5%)"
    tier_multiplier = 1.0
elif water_saved_pct <= 10:
    tier_name = "Tier 2 (5-10%)"
    tier_multiplier = 1.2
elif water_saved_pct <= 15:
    tier_name = "Tier 3 (10-15%)"
    tier_multiplier = 1.5
else:
    tier_name = "Tier 4 (15-20%)"
    tier_multiplier = 2.0

# Credits calculation (1 credit per 10 m³ saved, modified by tier)
base_credits = water_saved_m3 / 10.0 * tier_multiplier

# Apply small farm multiplier if eligible
final_multiplier = small_farm_multiplier if is_small_farm else 1.0
total_credits = base_credits * final_multiplier

# Financial Value in AED (1 Credit = 3.13 AED)
credit_value_aed = 3.13
total_revenue_aed = total_credits * credit_value_aed

# --- Main Dashboard Layout ---
col1, col2, col3, col4 = st.cols(4)

col1.metric("💧 Water Saved", f"{water_saved_m3:,.0f} m³", f"{water_saved_pct}% reduction")
col2.metric("⭐ Efficiency Tier", tier_name, f"Multiplier: {tier_multiplier}x")
col3.metric("🪙 Water Credits Earned", f"{total_credits:,.1f}", "Credits")
col4.metric("💰 Estimated Revenue", f"{total_revenue_aed:,.2f} AED", "@ 3.13 AED / credit")

st.markdown("---")

# Visual Analysis Section
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Farm Status & Equity Check")
    if is_small_farm:
        st.success(f"🛡️ **Small Farm Status ACTIVE**: This farm is **{farm_area} ha** (below the {small_farm_threshold} ha threshold). It benefits from the **{small_farm_multiplier}x** smallholder bonus multiplier to level the playing field against enterprise farms!")
    else:
        st.info(f"🏢 **Enterprise Farm Status**: This farm is **{farm_area} ha** (above the {small_farm_threshold} ha threshold). Standard tier multipliers apply without the smallholder bonus.")

    # Display breakdown table
    breakdown_df = pd.DataFrame({
        "Metric": ["Farm Size", "Crop Type", "Baseline Water Use", "Water Saved", "Tier Multiplier", "Smallholder Bonus", "Total Revenue"],
        "Value": [
            f"{farm_area} ha",
            selected_crop,
            f"{total_baseline_water:,.0f} m³",
            f"{water_saved_m3:,.0f} m³",
            f"{tier_multiplier}x",
            f"{final_multiplier}x",
            f"{total_revenue_aed:,.2f} AED"
        ]
    })
    st.table(breakdown_df)

with c2:
    st.subheader("📈 Revenue Scaling Across Tiers")
    percentages = list(range(0, 21, 1))
    revenues = []
    for p in percentages:
        s_m3 = total_baseline_water * (p / 100.0)
        if p <= 5: t_m = 1.0
        elif p <= 10: t_m = 1.2
        elif p <= 15: t_m = 1.5
        else: t_m = 2.0
        c = (s_m3 / 10.0) * t_m * final_multiplier
        revenues.append(c * credit_value_aed)

    chart_df = pd.DataFrame({"Water Saved (%)": percentages, "Revenue (AED)": revenues})
    fig = px.line(chart_df, x="Water Saved (%)", y="Revenue (AED)", markers=True, title=f"Revenue Growth for {farm_area} ha {selected_crop} Farm")
    fig.update_layout(xaxis_title="Water Saved (%)", yaxis_title="Revenue (AED)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 💡 Why this appeals to Judges & Investors:")
st.markdown("""
* **Fairness & Equity:** Visually proves small farms aren't priced out via the smallholder bonus multiplier.
* **Transparent Economics:** Direct mapping to local currency (**3.13 AED** per credit).
* **Behavioral Incentive:** Stepped tiers encourage higher efficiency savings up to the 20% cap.
""")
