import streamlit as st
import pandas as pd
import pyodbc
import datetime

from modules.columns import *
from .sql_queries import caims_v2

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

@st.cache_data(ttl=None, show_spinner="Fetching customer data from CAIMS V2 Database...")
def get_cus_data_from_database():
	cus_df = pd.read_sql(caims_v2, conn_v2)
	# Get the current date and time
	now = datetime.datetime.now()
	last_refresh_date = now.date().strftime("%Y-%m-%d")
	last_refresh_time = now.time().strftime("%H:%M:%S")


	# Add the last refresh date and time to the dataframe
	cus_df["last_refresh_date"] = last_refresh_date
	cus_df["last_refresh_time"] = last_refresh_time

	cus_df['validated_date'] = pd.to_datetime(cus_df['validated_date'])
	cus_df['week_month'] = cus_df.apply(calculate_week_month, axis=1)
	cus_df['week_month_year'] = cus_df.apply(calculate_week_month_year, axis=1)

	st.success("Fetched CAIMS V2 Customer data from Database!")
	return cus_df