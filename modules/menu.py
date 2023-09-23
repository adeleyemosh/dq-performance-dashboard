import streamlit as st
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