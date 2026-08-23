import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Farm Water Credit & Visualization Dashboard",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Farm Water Credit & Data Visualization Dashboard")
st.markdown("Calculate water savings, evaluate efficiency gaps, and estimate water credits for sustainable farming.")

# --- SIDEBAR INPUTS (The 7 Parameters) ---
st.sidebar.header("🛠️ Farm Configuration")

# 1. Size of farm
farm_size = st.sidebar.slider("1. Size of Farm (Acres)", 1.0, 1000.0, 50.0, step=1.0)

# 2. Actual water consumption yearly
actual_water = st.sidebar.number_input("2. Actual Yearly Water Consumption (m³)", min_value=0.0, value=50000.0, step=1000.0)

# 3. How many crops grown
num_crops = st.sidebar.slider("3. Number of Crops Grown", 1, 6, 2)

st.sidebar.markdown("---")
st.sidebar.subheader("🌱 Crop Breakdown & Requirements")

crop_data = []
crop_options = ["Wheat", "Corn", "Rice", "Cotton", "Soybean", "Barley", "Fruits/Vegetables", "Sugarcane"]
total_standard_water = 0

# Dynamic inputs based on the number of crops grown
for i in range(num_crops):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # 4. What are the types of crops grown
        crop_type = st.selectbox(f"Crop {i+1} Type", crop_options, key=f"crop_{i}")
    with col2:
        # 5. Annual water consumption of each crop to sustain a healthy crop (per acre)
        crop_std_water = st.number_input(f"Crop {i+1} Std Water/Acre (m³)", min_value=0.0, value=1200.0, step=100.0, key=f"std_water_{i}")
    
    # Allocating farm portions evenly for simplicity in multi-crop simulations
    crop_share = farm_size / num_crops
    crop_total_std = crop_std_water * crop_share
    total_standard_water += crop_total_std
    
    crop_data.append({
        "Crop": crop_type,
        "Standard Water/Acre (m³)": crop_std_water,
        "Allocated Share (Acres)": crop_share,
        "Total Standard Need (m³)": crop_total_std
    })

df_crops = pd.DataFrame(crop_data)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Efficiency & Savings")

# 6. Water efficiency gap
efficiency_gap = st.sidebar.slider("6. Water Efficiency Gap (%)", 0.0, 50.0, 12.5, step=0.5, 
                                 help="The efficiency variance margin compared to optimized modern practices.")

# 7. Water % saved
water_pct_saved = st.sidebar.slider("7. Water % Saved (%)", 0.0, 100.0, 20.0, step=1.0,
                                    help="Percentage of water saved relative to conventional baseline consumption.")

# --- CALCULATIONS ---
water_saved_volume = actual_water * (water_pct_saved / 100.0)

# Water credit formula factoring in volume saved and the efficiency gap bonus
credit_multiplier = 1.0 + (efficiency_gap / 100.0)
water_credits = (water_saved_volume / 1000.0) * credit_multiplier

# --- MAIN DASHBOARD LAYOUT ---
col1, col2, col3 = st.columns(3)
col1.metric("💧 Total Water Saved", f"{water_saved_volume:,.2f} m³", f"{water_pct_saved}% reduction")
col2.metric("🏆 Water Credits Earned", f"{water_credits:,.2f} Credits", f"Bonus Factor: +{efficiency_gap}%")
col3.metric("📏 Total Farm Scale", f"{farm_size:,.1f} Acres", f"{num_crops} Crop Varieties")

st.markdown("---")

# Visualizations
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📊 Standard Water Requirement by Crop")
    fig_crops = px.bar(
        df_crops, 
        x="Crop", 
        y="Total Standard Need (m³)", 
        color="Crop",
        title="Sustainable Water Need per Crop Sub-section",
        text_auto=True
    )
    st.plotly_chart(fig_crops, use_container_width=True)

with chart_col2:
    st.subheader("⚖️ Actual vs. Target Water Metrics")
    comparison_df = pd.DataFrame({
        "Metric Category": ["Actual Consumption", "Standard Health Requirement", "Water Saved"],
        "Volume (m³)": [actual_water, total_standard_water, water_saved_volume]
    })
    fig_comp = px.bar(
        comparison_df,
        x="Metric Category",
        y="Volume (m³)",
        color="Metric Category",
        title="Overall Water Balance Overview",
        color_discrete_map={
            "Actual Consumption": "#EF553B", 
            "Standard Health Requirement": "#636EFA", 
            "Water Saved": "#00CC96"
        }
    )
    st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")
st.subheader("📋 Farm Breakdown Table")
st.dataframe(df_crops, use_container_width=True)

# --- DEPLOYMENT HELPER ---
with st.expander("🚀 Guide: How to deploy this on GitHub & Streamlit Community Cloud"):
    st.markdown("""
    1. **Create a GitHub Repository**: Upload this code as a file named `app.py`.
    2. **Add a Requirements File**: Create an accompanying file named `requirements.txt` containing the required dependencies:
       ```text
       streamlit
       pandas
       plotly
       ```
    3. **Deploy via Streamlit Cloud**:
       - Go to [share.streamlit.io](https://share.streamlit.io/)
       - Log in with GitHub, select your new repository, and point the main file path to `app.py`.
       - Click **Deploy**!
    """)
