import streamlit as st
import pandas as pd
import pyodbc
import datetime

from modules.columns import *
from .sql_queries import aedc_nw_cus_query
from .sql_queries import aedc_ex_cus_query

# AEDC
###################################################
@st.cache_resource
def aedc_init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER="
        + st.secrets["aedc_server"]
        + ";DATABASE="
        + st.secrets["aedc_database"]
        + ";UID="
        + st.secrets["aedc_username"]
        + ";PWD="
        + st.secrets["aedc_password"]
    )

conn = aedc_init_connection()

@st.cache_data(ttl=None, show_spinner="Fetching existing customer data from AEDC Database...")
def get_aedc_ex_cus_data_from_database():
	aedc_ex_cus_df = pd.read_sql(aedc_ex_cus_query, conn)
	# Get the current date and time
	now = datetime.datetime.now()
	last_refresh_date = now.date().strftime("%Y-%m-%d")
	last_refresh_time = now.time().strftime("%H:%M:%S")

	# Add the last refresh date and time to the dataframe
	aedc_ex_cus_df["last_refresh_date"] = last_refresh_date
	aedc_ex_cus_df["last_refresh_time"] = last_refresh_time

	aedc_ex_cus_df['validated_date'] = pd.to_datetime(aedc_ex_cus_df['validated_date'])
	aedc_ex_cus_df['week_month'] = aedc_ex_cus_df.apply(calculate_week_month, axis=1)
	aedc_ex_cus_df['week_month_year'] = aedc_ex_cus_df.apply(calculate_week_month_year, axis=1)

	st.success("Fetched AEDC Customer data from Database!")
	return aedc_ex_cus_df

@st.cache_data(ttl=None, show_spinner="Fetching new customer data from AEDC Database...")
def get_aedc_nw_cus_data_from_database():
	aedc_nw_cus_df = pd.read_sql(aedc_nw_cus_query, conn)
	# Get the current date and time
	now = datetime.datetime.now()
	last_refresh_date = now.date().strftime("%Y-%m-%d")
	last_refresh_time = now.time().strftime("%H:%M:%S")


	# Add the last refresh date and time to the dataframe
	aedc_nw_cus_df["last_refresh_date"] = last_refresh_date
	aedc_nw_cus_df["last_refresh_time"] = last_refresh_time

	aedc_nw_cus_df['validated_date'] = pd.to_datetime(aedc_nw_cus_df['validated_date'])
	aedc_nw_cus_df['week_month'] = aedc_nw_cus_df.apply(calculate_week_month, axis=1)
	aedc_nw_cus_df['week_month_year'] = aedc_nw_cus_df.apply(calculate_week_month_year, axis=1)

	st.success("Fetched AEDC New Customer data from Database!")
	return aedc_nw_cus_df
