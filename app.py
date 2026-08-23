import pandas as pd
import streamlit as st

st.set_page_config(page_title="Water Credit Farm Simulator", layout="wide")

st.title("🌾 Interactive Water Credit Farm Simulator")
st.markdown(
    "Designed for Judges & Investors: Adjust the **Farm Area** slider. If it is"
    " **3.5 hectares or below**, the smallholder bonus applies automatically to"
    " protect small farms!"
)

# Sidebar / Input Section
st.sidebar.header("🎛️ Simulation Controls")

crop_defaults = {
    "Palm Tree": 22000,
    "Cherry Tomato": 9000,
    "Potato": 6500,
    "Wheat": 4500,
}

selected_crop = st.sidebar.selectbox(
    "Select Crop Type", list(crop_defaults.keys())
)
default_water = crop_defaults[selected_crop]

base_water_rate = st.sidebar.number_input(
    "Base Annual Water Consumption (m³ per hectare)",
    min_value=1000,
    max_value=50000,
    value=default_water,
    step=500,
)

farm_area = st.sidebar.slider(
    "Farm Area (Hectares)",
    min_value=0.5,
    max_value=50.0,
    value=3.0,
    step=0.5,
    help="Adjust the size of your single example farm.",
)

water_saved_pct = st.sidebar.slider(
    "Water Saved Percentage (%)",
    min_value=0.0,
    max_value=20.0,
    value=12.0,
    step=0.5,
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Small Farm Protection")

# Fixed threshold at 3.5 hectares
SMALL_FARM_LIMIT = 3.5
is_small_farm = farm_area <= SMALL_FARM_LIMIT

small_farm_multiplier = st.sidebar.slider(
    "Smallholder Bonus Multiplier",
    min_value=1.0,
    max_value=3.0,
    value=1.5,
    step=0.1,
    help=(
        "Extra multiplier added automatically if the farm is 3.5 ha or below."
    ),
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

# Credits calculation
base_credits = water_saved_m3 / 10.0 * tier_multiplier
final_multiplier = small_farm_multiplier if is_small_farm else 1.0
total_credits = base_credits * final_multiplier

# Financial Value in AED (1 Credit = 3.13 AED)
credit_value_aed = 3.13
total_revenue_aed = total_credits * credit_value_aed

# --- Main Dashboard Layout ---
col1, col2, col3 = st.columns(3)

col1.metric(
    "💧 Water Saved", f"{water_saved_m3:,.0f} m³", f"{water_saved_pct}% reduction"
)
col2.metric("⭐ Efficiency Tier", tier_name, f"Multiplier: {tier_multiplier}x")
col3.metric("🪙 Water Credits Earned", f"{total_credits:,.1f}", "WC")

st.markdown("---")

# THE MONEY SECTION - VERY EXPLICIT FOR JUDGES
st.subheader("💵 The Actual Money The Farmer Makes")
st.success(
    f"## 💰 Total Farmer Take-Home: **{total_revenue_aed:,.2f} AED**\n\n"
    f"**How the final payout is calculated:**\n"
    f"1. **Base Credits:** {base_credits:,.1f} WC (Based on water saved & tier)\n"
    f"2. **Small Farm Bonus:** × {final_multiplier} Multiplier ➔ **{total_credits:,.1f} Final WC**\n"
    f"3. **Cash Conversion:** {total_credits:,.1f} WC × 3.13 AED = **{total_revenue_aed:,.2f} AED**"
)

st.markdown("---")

# Farm Status & Table Section
st.subheader("📊 Farm Status & Equity Check")
if is_small_farm:
  st.info(
      f"🛡️ **Small Farm Protection ACTIVE**: This farm is **{farm_area} ha**"
      f" (which is <= {SMALL_FARM_LIMIT} ha). The"
      f" **{small_farm_multiplier}x** smallholder bonus is automatically"
      " applied to their payout!"
  )
else:
  st.info(
      f"🏢 **Enterprise Farm Status**: This farm is **{farm_area} ha** (above"
      f" the {SMALL_FARM_LIMIT} ha smallholder cutoff). Standard rates apply."
  )

# Dual Graphs Section: Water Credits vs. Profit/Revenue
st.subheader("📈 Simulation Graphs (0% to 20% Savings)")

percentages = list(range(0, 21, 1))
credits_list = []
revenues_list = []

for p in percentages:
  s_m3 = total_baseline_water * (p / 100.0)
  if p <= 5:
    t_m = 1.0
  elif p <= 10:
    t_m = 1.2
  elif p <= 15:
    t_m = 1.5
  else:
    t_m = 2.0
  c = (s_m3 / 10.0) * t_m * final_multiplier
  credits_list.append(c)
  revenues_list.append(c * credit_value_aed)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
  st.markdown("### 🪙 Water Credits (WC) Earned")
  credits_df = pd.DataFrame(
      {"Water Saved (%)": percentages, "Water Credits (WC)": credits_list}
  )
  st.line_chart(credits_df.set_index("Water Saved (%)"))

with chart_col2:
  st.markdown("### 💰 Financial Profit / Revenue (AED)")
  revenue_df = pd.DataFrame(
      {"Water Saved (%)": percentages, "Profit (AED)": revenues_list}
  )
  st.line_chart(revenue_df.set_index("Water Saved (%)"))
