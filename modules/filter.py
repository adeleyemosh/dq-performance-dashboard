import streamlit as st
import datetime
import pandas as pd

#--------------------------------------------------------#
#---------------------- FILTER --------------------------#
#--------------------------------------------------------#
today = datetime.datetime.now().date()
default_start = datetime.datetime(today.year, today.month, 1).date()

def filter_data(data):
	st.sidebar.header("Filter Data")

	date_range_start = st.sidebar.date_input(
			"Select a start date", 
			key='date_range_start', 
			value=default_start
		)
		
	date_range_end = st.sidebar.date_input(
		"Select a end date", 
		key='date_range_end', 
		value=today
	)

	# Define filter options
	months = data["month"].unique()
	selected_months = st.sidebar.multiselect(
		"Select Month:", 
		months, 
		default=months
	)

	years = data["year"].unique()
	selected_years = st.sidebar.multiselect(
		"Select Year:", 
		years, 
		default=years
	)

	validated_bys = data["validated_by"].unique()
	selected_validated_bys = st.sidebar.multiselect(
		"Select Validator:", 
		validated_bys, 
		default=validated_bys
	)

	source_tags = data["customer_status"].unique()
	selected_source_tags = st.sidebar.multiselect(
		"Select Customer Status:", 
		source_tags, 
		default=source_tags
	)

	data['val_date'] = pd.to_datetime(data['val_date']).dt.date

	# Apply filters to the data
	data_selection = data[
        (data["month"].isin(selected_months)) &
        (data["year"].isin(selected_years)) &
        (data["validated_by"].isin(selected_validated_bys)) &
        (data["customer_status"].isin(selected_source_tags)) &
        (data["val_date"] >= date_range_start) &  
        (data["val_date"] <= date_range_end)  
    ]

	st.sidebar.markdown('''
	---
	Made with ❤️ by [Beacon Power Services](https://beaconpowerservices.com/).
	''')

	return data_selection