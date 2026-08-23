import streamlit as st
import pandas as pd

# Page configuration for a wider layout to make best use of side-by-side display
st.set_page_config(layout="wide")

st.title("🌱 Farm Data Visualization & Water Efficiency Dashboard")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Farm Data Inputs")

# Enter the hectares of the farm
hectares = st.sidebar.number_input("Enter the hectares of the farm:", min_value=0.0, format="%.2f")

# Enter actual water consumption for the farm
actual_water = st.sidebar.number_input("Enter actual water consumption for the farm (kL):", min_value=0.0, format="%.2f")

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
    
    # Water efficiency gap calculation
    water_efficiency_gap = actual_water - efficient_water
    
    # Water efficiency gap percentage calculation (guarding against division by zero)
    if efficient_water > 0:
        water_efficiency_gap_pct = (water_efficiency_gap / efficient_water) * 100
    else:
        water_efficiency_gap_pct = 0.0
    
    st.subheader("📊 Summary & Water Efficiency Analysis")
    
    # Display key metrics using Streamlit metrics across 4 columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Actual Water", f"{actual_water:,.2f} kL")
    col2.metric("Efficient Water", f"{efficient_water:,.2f} kL")
    col3.metric("Efficiency Gap", f"{water_efficiency_gap:,.2f} kL")
    col4.metric("Gap %", f"{water_efficiency_gap_pct:,.2f}%")
    
    st.write(f"**Farm Size:** {hectares} hectares &nbsp;&nbsp;|&nbsp;&nbsp; **Total Crops:** {num_crops}")
    st.write("---")

    # Display data table and bar chart side-by-side on the main screen
    table_col, chart_col = st.columns(2)
    
    with table_col:
        st.markdown("### Crop Data Table")
        st.dataframe(df, use_container_width=True)
        
    with chart_col:
        st.markdown("### Water Consumption by Crop")
        st.bar_chart(df.set_index("Crop"))

else:
    st.sidebar.error("Please enter a valid number containing between 1 and 15 digits.")
    st.warning("👈 Please enter a valid number of crops in the sidebar to view the dashboard.")
