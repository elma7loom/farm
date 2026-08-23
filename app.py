import streamlit as st
import pandas as pd

st.title("Farm Data Visualization")

# Enter the hectares of the farm
hectares = st.number_input("Enter the hectares of the farm:", min_value=0.0, format="%.2f")

# Blank for amount of crops grown (accepts 1-15 digits)
num_crops_input = st.text_input("Enter the amount of crops grown (1-15 digits):", value="1")

# Validate the 1-15 digits constraint
if num_crops_input.isdigit() and 1 <= len(num_crops_input) <= 15:
    num_crops = int(num_crops_input)
    
    # Limit UI rendering loop for practicality if the number is excessively large
    render_limit = min(num_crops, 50)
    if num_crops > 50:
        st.warning("Large number entered. Displaying input fields for the first 50 crops.")

    crop_data = []
    st.subheader("Crop Water Consumption Details")

    for i in range(render_limit):
        col1, col2 = st.columns(2)
        with col1:
            crop_name = st.text_input(f"Crop {i+1} Name", value=f"Crop {i+1}", key=f"name_{i}")
        with col2:
            water_consumption = st.number_input(f"Annual Water Consumption (kL) for {crop_name}", min_value=0.0, key=f"water_{i}")
        
        crop_data.append({"Crop": crop_name, "Water Consumption (kL)": water_consumption})

    if st.button("Visualize Data"):
        df = pd.DataFrame(crop_data)
        
        st.write("---")
        st.subheader("Summary")
        st.write(f"**Farm Size:** {hectares} hectares")
        st.write(f"**Total Crops:** {num_crops}")
        
        # Display data table and bar chart
        st.dataframe(df)
        st.bar_chart(df.set_index("Crop"))

else:
    st.error("Please enter a valid number containing between 1 and 15 digits.")
