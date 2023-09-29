import streamlit as st
from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards

from modules.connection_ecg import get_ecg_ex_cus_data_from_database
from modules.connection_ecg import get_ecg_nw_cus_data_from_database
from modules.connection_aedc import get_aedc_ex_cus_data_from_database
from modules.connection_aedc import get_aedc_nw_cus_data_from_database
from modules.data import show_raw_data
from modules.data import load_and_preprocess_data
from modules.filter import filter_data
from modules.menu import streamlit_menu
from modules.metrics import display_metrics_tabs
from modules.header import dashboard_header

# Function to load and preprocess data
def load_data(dashboard_type):
    if dashboard_type == 'ECG':
        nw_cus_df = get_ecg_nw_cus_data_from_database()
        ex_cus_df = get_ecg_ex_cus_data_from_database()
    elif dashboard_type == 'AEDC':
        nw_cus_df = get_aedc_nw_cus_data_from_database()
        ex_cus_df = get_aedc_ex_cus_data_from_database()
    
    df = load_and_preprocess_data(nw_cus_df, ex_cus_df)
    df_selection = filter_data(df, dashboard_type)
    return df, df_selection

#--------------------------------------------------------#
#-------------- PAGE CONFIGURATION SETUP ----------------#
#--------------------------------------------------------#

st.set_page_config(
    page_title="DQ Performance Dashboard", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

DESIGN_NO = 2
selected = streamlit_menu(design=DESIGN_NO)

# Load data and filter selection based on the selected dashboard
if selected == 'ECG':
    ecg_df, ecg_df_selection = load_data('ECG')
elif selected == 'AEDC':
    aedc_df, aedc_df_selection = load_data('AEDC')

# Logos
bps_logo = Image.open("logo/bps_logo.png")
ecg_logo = Image.open("logo/ecg_logo.png")
aedc_logo = Image.open("logo/aedc_logo.png")

#--------------------------------------------------------#
#---------------------- ECG MAIN ------------------------#
#--------------------------------------------------------#

def ecg():
    dashboard_header(
        image1 = bps_logo, 
        image2 = ecg_logo, 
        title="ECG Dashboard"
    )
    display_metrics_tabs(ecg_df, ecg_df_selection)
    show_raw_data(ecg_df_selection)

#--------------------------------------------------------#
#---------------------- AEDC MAIN -----------------------#
#--------------------------------------------------------#

def aedc():
    dashboard_header(
        image1 = bps_logo, 
        image2 = aedc_logo, 
        title="AEDC Dashboard"
    )
    display_metrics_tabs(aedc_df, aedc_df_selection)
    show_raw_data(aedc_df_selection)

#--------------------------------------------------------#
#------------------- KPI CARD STYLING -------------------#
#--------------------------------------------------------#
# Apply styles based on the selected dashboard
if selected == 'ECG':
    style_metric_cards(
        border_left_color="red", 
        box_shadow=True, 
        border_radius_px=5, 
        background_color="#FFF"
    )
elif selected == 'AEDC':
    style_metric_cards(
        border_left_color="blue",  
        box_shadow=True, 
        border_radius_px=5, 
        background_color="#FFF"
    )

#--------------------------------------------------------#
#------------------ MAIN FUNCTION CALL ------------------#
#--------------------------------------------------------#
if selected == "ECG":
    if __name__ == "__main__":
        ecg()
elif selected == "AEDC":
    if __name__ == "__main__":
        aedc()

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
