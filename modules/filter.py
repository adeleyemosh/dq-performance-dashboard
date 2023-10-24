import streamlit as st
import datetime
import pandas as pd

# FILTER 
###################################################
today = datetime.datetime.now().date()
default_start = datetime.datetime(today.year, today.month, 1).date()

def filter_data(data, title):
    last_refresh_date = data["last_refresh_date"].iloc[0]
    last_refresh_time = data["last_refresh_time"].iloc[0]

    st.sidebar.markdown(
        f"<p style='font-weight: bold;'>Last refreshed on: {last_refresh_date} at {last_refresh_time}</p>", 
        unsafe_allow_html=True
    )
    
    st.sidebar.header(f"Filter Data for {title}")

    # Generate unique keys based on the title
    date_range_start_key = f'date_range_start_{title}'
    date_range_end_key = f'date_range_end_{title}'
    selected_months_key = f'selected_months_{title}'
    selected_years_key = f'selected_years_{title}'
    selected_source_tags_key = f'selected_source_tags_{title}'
    selected_validated_bys_key = f'selected_validated_bys_{title}'

    date_range_start = st.sidebar.date_input(
        "Select a start date:", 
        key=date_range_start_key, 
        value=default_start
    )
        
    date_range_end = st.sidebar.date_input(
        "Select an end date:", 
        key=date_range_end_key, 
        value=today
    )

    months = data["month"].unique()
    selected_months = st.sidebar.multiselect(
        "Select Month:", 
        months, 
        default=months,
        key=selected_months_key
    )

    years = data["year"].unique()
    selected_years = st.sidebar.multiselect(
        "Select Year:", 
        years, 
        default=years,
        key=selected_years_key
    )

    source_tags = data["customer_status"].unique()
    selected_source_tags = st.sidebar.multiselect(
        "Select Customer Status:", 
        source_tags, 
        default=source_tags,
        key=selected_source_tags_key
    )

    validated_bys = data["validated_by"].unique()
    selected_validated_bys = st.sidebar.multiselect(
        "Select Validator:", 
        validated_bys, 
        default=validated_bys,
        key=selected_validated_bys_key
    )

    data['val_date'] = pd.to_datetime(data['val_date']).dt.date

    data_selection = data[
        (data["val_date"] >= date_range_start) &  
        (data["val_date"] <= date_range_end) &
        (data["month"].isin(selected_months)) &
        (data["year"].isin(selected_years)) &
        (data["validated_by"].isin(selected_validated_bys)) &
        (data["customer_status"].isin(selected_source_tags)) 
    ]

    st.sidebar.markdown('''
    ---
    Made with ❤️ by [Beacon Power Services](https://beaconpowerservices.com/).
    ''')

    return data_selection