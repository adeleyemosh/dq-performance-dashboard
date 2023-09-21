import streamlit as st
import datetime
from streamlit_option_menu import option_menu

#--------------------------------------------------------#
#---------------- MULTI-PAGE VIEW SETUP -----------------#
#--------------------------------------------------------#

def streamlit_menu(design=1):
    if design == 1:
        # 1. as sidebar menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",  # required
                options=["ECG", "AEDC",],  # required
                icons=["collection", "collection-fill",],  # optional
                menu_icon="cast",  # optional
                default_index=0,  # optional
            )
        return selected

    if design == 2:
        # 2. horizontal menu w/o custom style
        selected = option_menu(
            menu_title=None,  # required
            options=["ECG", "AEDC",],  # required
            icons=["collection", "collection-fill",],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )
        return selected

    if design == 3:
        # 2. horizontal menu with custom style
        selected = option_menu(
            menu_title=None,  # required
            options=["ECG", "AEDC",],  # required
            icons=["collection", "collection-fill",],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "25px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "green"},
            },
        )
        return selected


today = datetime.datetime.now().date()
default_start = datetime.datetime(today.year, today.month, 1).date()

global date_range_start
date_range_start = st.sidebar.date_input("Select a start date", key='date_range_start', value=default_start)

global date_range_end
date_range_end = st.sidebar.date_input("Select a end date", key='date_range_end', value=today)

date_range_start_str = date_range_start.strftime('%Y-%m-%d')
date_range_end_str = date_range_end.strftime('%Y-%m-%d')

#--------------------------------------------------------#
#----------------- GENERAL FUNCTIONS --------------------#
#--------------------------------------------------------#
def filter_data(df):
    st.sidebar.header("Please Filter Here:")
    date_range_start_str = date_range_start.strftime('%Y-%m-%d')
    date_range_end_str = date_range_end.strftime('%Y-%m-%d')

    month = st.sidebar.multiselect(
        "Select Month:",
        options=df["month"].unique(),
        default=df["month"].unique()
    )

    year = st.sidebar.multiselect(
        "Select Year:",
        options=df["year"].unique(),
        default=df["year"].unique()
    )

    validated_by = st.sidebar.multiselect(
        "Select Validator:",
        options=df["validated_by"].unique(),
        default=df["validated_by"].unique()
    )
        
    source_tag = st.sidebar.multiselect(
        "Select Customer Status:",
        options=df["customer_status"].unique(),
        default=df["customer_status"].unique(),
    )
        
    region = st.sidebar.multiselect(
    	"Select Region:",
    	options=df["region"].unique(),
    	default=df["region"].unique()
    )

    # district = st.sidebar.multiselect(
    # 	"Select District:",
    # 	options=df["district"].unique(),
    # 	default=df["district"].unique()
    # )

    st.sidebar.markdown('''
    ---
    Made with ❤️ by [Beacon Power Services](https://beaconpowerservices.com/).
    ''')