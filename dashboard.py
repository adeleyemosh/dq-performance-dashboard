import streamlit as st
import pandas as pd
from PIL import Image
import datetime

from modules.ecg_connection import get_ecg_ex_cus_data_from_database, get_ecg_nw_cus_data_from_database
from modules.menu import streamlit_menu, filter_data
from modules.metrics import display_kpi_metrics
from modules.header import dashboard_header
from modules.data import show_raw_data

#--------------------------------------------------------#
#-------------- PAGE CONFIGURATION SETUP ----------------#
#--------------------------------------------------------#

st.set_page_config(
	page_title="DQ Performance Dashboard", 
    page_icon="💈", 
	layout="wide",
	initial_sidebar_state="collapsed"
)

selected = streamlit_menu()

#--------------------------------------------------------#
#------------------------ ECG ---------------------------#
#--------------------------------------------------------#
ecg_nw_cus_df = get_ecg_nw_cus_data_from_database()
ecg_ex_cus_df = get_ecg_ex_cus_data_from_database()

ecg_df = pd.concat([
	ecg_nw_cus_df,
	ecg_ex_cus_df
])


last_refresh_date = ecg_df["last_refresh_date"].iloc[0]
last_refresh_time = ecg_df["last_refresh_time"].iloc[0]

st.sidebar.markdown(f"<p style='font-weight: bold;'>Last refreshed on: {last_refresh_date} at {last_refresh_time}</p>", unsafe_allow_html=True)

#--------- VARIABLE DEFINITION ---------#
invalid_validators = [
    'DevAdmin', 
    'Christianbackend', 
]

ecg_df = ecg_df[
    (ecg_df['validated_by'].notnull()) & 
    (~ecg_df['validated_by'].isin(invalid_validators))
]

# Function to calculate the week-month value
# def calculate_week_month(row):
#     if pd.isnull(row['validated_date']):
#         return "N/A"  # Handle missing dates
#     week_number = row['validated_date'].week - (pd.to_datetime(row['validated_date']).to_period('M').start_time.week - 1)
#     month_name = row['validated_date'].strftime('%B')
#     return f"Week {week_number} - {month_name}"


ecg_df["validated_date"] = pd.to_datetime(ecg_df["validated_date"])
ecg_df["val_date"] = ecg_df["validated_date"].dt.strftime('%Y-%m-%d')
ecg_df['year'] = pd.DatetimeIndex(ecg_df['validated_date']).year
ecg_df['month'] = pd.DatetimeIndex(ecg_df['validated_date']).month  
# ecg_df['week_month'] = ecg_df.apply(calculate_week_month, axis=1)

validated_by = ecg_df["validated_by"]
source_tag = ecg_df["customer_status"]
year = ecg_df['year']
month = ecg_df['month']
region = ecg_df['region']
district = ecg_df['district']


today = datetime.datetime.now().date()
default_start = datetime.datetime(today.year, today.month, 1).date()

date_range_start = st.sidebar.date_input("Select a start date", key='date_range_start', value=default_start)
date_range_end = st.sidebar.date_input("Select an end date", key='date_range_end', value=today)

date_range_start = date_range_start.strftime('%Y-%m-%d')
date_range_end = date_range_end.strftime('%Y-%m-%d')

ecg_df_selection = ecg_df.query(
    "validated_by == @validated_by & "
    "customer_status == @source_tag &"
    "year == @year & "
    "month == @month & "
    "@date_range_start <= val_date <= @date_range_end & "
    "region == @region & "
    "district == @district"
)


#--------------------------------------------------------#
#---------------------- ECG MAIN ------------------------#
#--------------------------------------------------------#

def ecg():
	dashboard_header(image1 = Image.open("logo/bps_logo.png"), image2 = Image.open("logo/ecg_logo.png"), title="ECG Dashboard")
	display_kpi_metrics(ecg_df, ecg_df_selection)
	show_raw_data(ecg_df_selection)

	#Display Filters
	filter_data(ecg_df_selection)


#--------------------------------------------------------#
#------------------ MAIN FUNCTION CALL ------------------#
#--------------------------------------------------------#
if selected == "ECG":
	if __name__ == "__main__":
		ecg()
# if selected == "AEDC":
# 	if __name__ == "__main__":
# 		aedc()


#--------------------------------------------------------#
#---------------- HIDE STREAMLIT STYLE ------------------#
#--------------------------------------------------------#
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)