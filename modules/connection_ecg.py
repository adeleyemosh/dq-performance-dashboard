import streamlit as st
import pandas as pd
import pyodbc
import datetime

from modules.columns import *
from .sql_queries import ecg_nw_cus_query
from .sql_queries import ecg_ex_cus_query

# ECG 
###################################################
@st.cache_resource
def ecg_init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER="
        + st.secrets["ecg_server"]
        + ";DATABASE="
        + st.secrets["ecg_database"]
        + ";UID="
        + st.secrets["ecg_username"]
        + ";PWD="
        + st.secrets["ecg_password"]
    )

conn = ecg_init_connection()

@st.cache_resource
def v2_init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER="
        + st.secrets["v2_server"]
        + ";DATABASE="
        + st.secrets["v2_database"]
        + ";UID="
        + st.secrets["v2_username"]
        + ";PWD="
        + st.secrets["v2_password"]
    )

conn_v2 = v2_init_connection()

@st.cache_data(ttl=None, show_spinner="Fetching existing customer data from ECG Database...")
def get_ecg_ex_cus_data_from_database():
	ecg_ex_cus_df = pd.read_sql(ecg_ex_cus_query, conn)
	# Get the current date and time
	now = datetime.datetime.now()
	last_refresh_date = now.date().strftime("%Y-%m-%d")
	last_refresh_time = now.time().strftime("%H:%M:%S")

	# Add the last refresh date and time to the dataframe
	ecg_ex_cus_df["last_refresh_date"] = last_refresh_date
	ecg_ex_cus_df["last_refresh_time"] = last_refresh_time

	ecg_ex_cus_df['validated_date'] = pd.to_datetime(ecg_ex_cus_df['validated_date'])
	ecg_ex_cus_df['week_month'] = ecg_ex_cus_df.apply(calculate_week_month, axis=1)
	ecg_ex_cus_df['week_month_year'] = ecg_ex_cus_df.apply(calculate_week_month_year, axis=1)

	st.success("Fetched ECG Customer data from Database!")
	return ecg_ex_cus_df

@st.cache_data(ttl=None, show_spinner="Fetching new customer data from ECG Database...")
def get_ecg_nw_cus_data_from_database():
	ecg_nw_cus_df = pd.read_sql(ecg_nw_cus_query, conn)
	# Get the current date and time
	now = datetime.datetime.now()
	last_refresh_date = now.date().strftime("%Y-%m-%d")
	last_refresh_time = now.time().strftime("%H:%M:%S")


	# Add the last refresh date and time to the dataframe
	ecg_nw_cus_df["last_refresh_date"] = last_refresh_date
	ecg_nw_cus_df["last_refresh_time"] = last_refresh_time

	ecg_nw_cus_df['validated_date'] = pd.to_datetime(ecg_nw_cus_df['validated_date'])
	ecg_nw_cus_df['week_month'] = ecg_nw_cus_df.apply(calculate_week_month, axis=1)
	ecg_nw_cus_df['week_month_year'] = ecg_nw_cus_df.apply(calculate_week_month_year, axis=1)

	st.success("Fetched ECG New Customer data from Database!")
	return ecg_nw_cus_df
