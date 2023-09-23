import streamlit as st
import pandas as pd
from PIL import Image
import datetime

from modules.ecg_connection import get_ecg_ex_cus_data_from_database
from modules.ecg_connection import get_ecg_nw_cus_data_from_database
from modules.menu import streamlit_menu
from modules.metrics import display_kpi_metrics
from modules.header import dashboard_header
from modules.data import show_raw_data
from modules.filter import filter_data

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

ecg_df["validated_date"] = pd.to_datetime(ecg_df["validated_date"])
ecg_df["val_date"] = ecg_df["validated_date"].dt.strftime('%Y-%m-%d')
ecg_df['year'] = pd.DatetimeIndex(ecg_df['validated_date']).year
ecg_df['month'] = pd.DatetimeIndex(ecg_df['validated_date']).month  

validated_by_ref = ecg_df["validated_by"]
source_tag = ecg_df["customer_status"]
year_ref = ecg_df['year']
month_ref = ecg_df['month']

ecg_df_selection = filter_data(ecg_df)

#--------------------------------------------------------#
#---------------------- ECG MAIN ------------------------#
#--------------------------------------------------------#

def ecg():
	dashboard_header(
		image1 = Image.open("logo/bps_logo.png"), 
		image2 = Image.open("logo/ecg_logo.png"), 
		title="ECG Dashboard"
	)
	display_kpi_metrics(ecg_df, ecg_df_selection)
	show_raw_data(ecg_df_selection)

	#Display Filters
	filter_data(ecg_df)


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