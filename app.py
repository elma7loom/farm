import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Water Credit Farm Simulator", layout="wide", initial_sidebar_state="expanded"
)

# --- WARM MINIMALIST CUSTOM CSS STYLING ---
st.markdown(
    """
    <style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #FDFBF7;
        color: #2D2D2D;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F4EFE6;
        color: #2D2D2D;
    }

    /* Headings & General Text */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #2D2D2D !important;
    }

    /* Metric Cards Customization */
    [data-testid="stMetricValue"] {
        color: #D97757 !important; /* Terracotta Accent */
    }
    
    [data-testid="stMetricLabel"] {
        color: #2D2D2D !important;
    }

    /* Custom Success Box (Terracotta & Sage Vibe) */
    .stSuccess {
        background-color: #E6EFEA !important;
        border-color: #87A99A !important; /* Sage Green */
        color: #2D2D2D !important;
    }
    
    /* Info Box */
    .stInfo {
        background-color: #F7EBE8 !important;
        border-color: #D97757 !important; /* Terracotta */
        color: #2D2D2D !important;
    }

    /* Tables */
    table {
        color: #2D2D2D !important;
        background-color: #FDFBF7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌾 Advanced Interactive Water Credit Farm Simulator")
st.markdown(
    "Designed for Judges & Investors: Configure multiple crops, adjust water"
    " savings **up to 60%**, and watch the credits and revenue update in"
    " real-time. Farms **3.5 hectares or below** automatically receive the"
    " smallholder protection bonus!"
)

# Sidebar / Input Section
st.sidebar.header("🎛️ Simulation Controls")

crop_defaults = {
    "Palm Tree": 22000,
    "Cherry Tomato": 9000,
    "Potato": 6500,
    "Wheat": 4500,
    "Custom Crop": 10000,
}

# 3. How many crops grown?
num_crops = st.sidebar.selectbox(
    "How many crops grown on the farm?", [1, 2, 3], index=1
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌱 Crop Breakdown & Water Rates")

crop_data_list = []
total_farm_area = 0
total_baseline_water = 0

# 4 & 5. What crops are grown and their water consumption / area
for i in range(num_crops):
  st.sidebar.markdown(f"**Crop #{i+1}**")
  c_type = st.sidebar.selectbox(
      f"Crop Type #{i+1}", list(crop_defaults.keys()), key=f"crop_{i}"
  )
  default_rate = crop_defaults[c_type]

  c_rate = st.sidebar.number_input(
      f"Annual Water Rate ($m^3$/ha) for Crop #{i+1}",
      min_value=500,
      max_value=500000,
      value=default_rate,
      step=500,
      key=f"rate_{i}",
  )

  c_area = st.sidebar.slider(
      f"Area (Hectares) for Crop #{i+1}",
      min_value=0.5,
      max_value=30.0,
      value=2.0 if i == 0 else 1.0,
      step=0.5,
      key=f"area_{i}",
  )

  crop_water = c_area * c_rate
  total_farm_area += c_area
  total_baseline_water += crop_water

  crop_data_list.append({
      "Crop": c_type,
      "Hectares": c_area,
      "Water Rate": c_rate,
      "Total Water": crop_water,
  })

st.sidebar.markdown("---")
st.sidebar.subheader("💧 Conservation & Equity Settings")

# 2. Percentage of water saved up to 60%
water_saved_pct = st.sidebar.slider(
    "Percentage of Water Saved (%)",
    min_value=0.0,
    max_value=60.0,
    value=20.0,
    step=0.5,
    help="Total percentage reduction in water consumption across the farm.",
)

# Small Farm Protection Settings
SMALL_FARM_LIMIT = 3.5
is_small_farm = total_farm_area <= SMALL_FARM_LIMIT

small_farm_multiplier = st.sidebar.slider(
    "Smallholder Bonus Multiplier",
    min_value=1.0,
    max_value=3.0,
    value=1.5,
    step=0.1,
    help=(
        "Extra multiplier added automatically if total farm area is 3.5 ha or"
        " below."
    ),
)

# --- Calculations ---
water_saved_m3 = total_baseline_water * (water_saved_pct / 100.0)

# Expanded Stepped Tiers for up to 60% Water Saving Efficiency
if water_saved_pct <= 15:
  tier_name = "Tier 1 (0-15%)"
  tier_multiplier = 1.0
elif water_saved_pct <= 30:
  tier_name = "Tier 2 (15-30%)"
  tier_multiplier = 1.2
elif water_saved_pct <= 45:
  tier_name = "Tier 3 (30-45%)"
  tier_multiplier = 1.5
else:
  tier_name = "Tier 4 (45-60%)"
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
    "💧 Total Water Saved",
    f"{water_saved_m3:,.0f} m³",
    f"{water_saved_pct}% reduction",
)
col2.metric("⭐ Efficiency Tier", tier_name, f"Multiplier: {tier_multiplier}x")
col3.metric("🪙 Water Credits Earned", f"{total_credits:,.1f}", "WC")

st.markdown("---")

# THE MONEY SECTION - EXPLICIT FOR JUDGES
st.subheader("💵 The Actual Money The Farmer Makes")
st.success(
    f"## 💰 Total Farmer Take-Home: **{total_revenue_aed:,.2f} AED**\n\n"
    f"**Calculation Breakdown:**\n"
    f"1. **Total Farm Size:** {total_farm_area} hectares ({num_crops} crops"
    f" combined)\n"
    f"2. **Base Credits:** {base_credits:,.1f} WC (Based on {water_saved_m3:,.0f}"
    f" $m^3$ saved & {tier_name})\n"
    f"3. **Small Farm Bonus:** × {final_multiplier} Multiplier ➔"
    f" **{total_credits:,.1f} Final WC**\n"
    f"4. **Cash Conversion:** {total_credits:,.1f} WC × 3.13 AED ="
    f" **{total_revenue_aed:,.2f} AED**"
)

st.markdown("---")

# Farm Status & Table Section
st.subheader("📊 Farm Status & Equity Check")
if is_small_farm:
  st.info(
      f"🛡️ **Small Farm Protection ACTIVE**: Total farm area is"
      f" **{total_farm_area} ha** (which is <= {SMALL_FARM_LIMIT} ha). The"
      f" **{small_farm_multiplier}x** smallholder bonus is automatically"
      " applied!"
  )
else:
  st.info(
      f"🏢 **Enterprise Farm Status**: Total farm area is"
      f" **{total_farm_area} ha** (above the {SMALL_FARM_LIMIT} ha"
      " threshold). Standard rates apply."
  )

# Display individual crop breakdown table
crop_df = pd.DataFrame(crop_data_list)
st.markdown("### 📋 Crop Allocation Summary")
st.table(crop_df)

st.markdown("---")

# Dual Graphs Section: Water Credits vs. Profit/Revenue (0% to 60%)
st.subheader("📈 Simulation Graphs (Scaling from 0% to 60% Water Savings)")

percentages = [i * 1.5 for i in range(41)]  # 0% to 60% in steps of 1.5%
credits_list = []
revenues_list = []

for p in percentages:
  s_m3 = total_baseline_water * (p / 100.0)
  if p <= 15:
    t_m = 1.0
  elif p <= 30:
    t_m = 1.2
  elif p <= 45:
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
