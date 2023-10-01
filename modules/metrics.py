import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
from streamlit_extras.metric_cards import style_metric_cards
from st_aggrid import AgGrid, GridOptionsBuilder

from modules.menu import streamlit_menu

# 1=sidebar menu, 2=horizontal menu, 3=horizontal menu w/ custom menu
# DESIGN_NO = 2
selected = streamlit_menu()

def calculate_daily_rate(dataframe):
	earliest_date = dataframe['validated_date'].min()
	latest_date = dataframe['validated_date'].max()

	overall_customers_reviewed = int(dataframe["ac_no"].nunique())
	days_diff = (latest_date - earliest_date).days + 1
	daily_rate = overall_customers_reviewed / days_diff

	return daily_rate

def display_metrics_today(
    customers_reviewed_today, customers_reviewed_yesterday,
    customers_approved_today, customers_approved_yesterday,
    customers_rejected_today, customers_rejected_yesterday,
    assets_reviewed_today, assets_reviewed_yesterday,
    assets_approved_today, assets_approved_yesterday,
    assets_rejected_today, assets_rejected_yesterday,
    formatted_fail_rate_today, formatted_fail_rate_yesterday
):
    st.markdown("<div style='text-align:center; font-size:15px; font-weight:bold;'>Today Metrics</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Customers Reviewed", value=customers_reviewed_today, delta=customers_reviewed_yesterday, help="Customers reviewed today versus yesterday")
    col2.metric(label="Customers Approved", value=customers_approved_today, delta=customers_approved_yesterday, help="Customers approved today versus yesterday")
    col3.metric(label="Customers Rejected", value=customers_rejected_today, delta=customers_rejected_yesterday, help="Customers rejected today versus yesterday")

    col4, col5, col6 = st.columns(3)
    col4.metric(label="Assets Reviewed", value=assets_reviewed_today, delta=assets_reviewed_yesterday, help="Assets reviewed today versus yesterday")
    col5.metric(label="Assets Approved", value=assets_approved_today, delta=assets_approved_yesterday, help="Assets approved today versus yesterday")
    col6.metric(label="Assets Rejected", value=assets_rejected_today, delta=assets_rejected_yesterday, help="Assets rejected today versus yesterday")

    col7, col8, col9 = st.columns(3)
    col7.metric(label="Fail Rate", value=formatted_fail_rate_today, delta=formatted_fail_rate_yesterday, help="Fail Rate today versus yesterday")

def display_overall_metrics(
    overall_customers_reviewed, overall_customers_approved, overall_customers_rejected, overall_assets_reviewed, 
	overall_assets_approved, overall_assets_rejected,
    formatted_fail_rate_overall, formatted_daily_rate_overall
):
    st.markdown("<div style='text-align:center; font-size:15px; font-weight:bold;'>Overall Metrics</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Customers Reviewed", value=f"{overall_customers_reviewed:,}")
    col2.metric(label="Customers Approved", value=f"{overall_customers_approved:,}")
    col3.metric(label="Customers Rejected", value=f"{overall_customers_rejected:,}")

    col4, col5, col6 = st.columns(3)
    col4.metric(label="Assets Reviewed", value=f"{overall_assets_reviewed:,}")
    col5.metric(label="Assets Approved", value=f"{overall_assets_approved:,}")
    col6.metric(label="Assets Rejected", value=f"{overall_assets_rejected:,}")  

    col7, col8, col9 = st.columns(3)
    col7.metric(label="Fail Rate", value=f"{formatted_fail_rate_overall}")
    col8.metric(label="Daily Rate", value=f"{formatted_daily_rate_overall}")

def calculate_weekly_performance(filtered_data, period):
	weekly_perf = filtered_data.pivot_table(
		index=[period],
		values=['slrn', 'ac_no'], 
		aggfunc={"slrn": "nunique", "ac_no": "nunique"}, 
		margins=False, 
		margins_name='Total', 
		fill_value=0
	).reset_index()  

	weekly_perf = weekly_perf.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})
					
	weekly_perf[period] = weekly_perf[period].astype(str)

	# Extract the week and month numbers
	weekly_perf['week_number'] = weekly_perf[period].str.extract(r'(\d+)').astype(int)
	weekly_perf['month'] = weekly_perf[period].str.extract(r'(\w+)$')

	# Define a dictionary to map month names to their numerical values
	month_to_num = {
		'January': 1, 
		'February': 2, 
		'March': 3, 
		'April': 4, 
		'May': 5, 
		'June': 6,
		'July': 7, 
		'August': 8, 
		'September': 9, 
		'October': 10, 
		'November': 11, 
		'December': 12
	}

	# Map month names to numerical values
	weekly_perf['month_number'] = weekly_perf['month'].map(month_to_num)

	# Create a composite sort key based on month and week numbers
	weekly_perf['sort_key'] = weekly_perf['month_number'] * 100 + weekly_perf['week_number']

	# Sort the DataFrame based on the sort key
	weekly_perf = weekly_perf.sort_values('sort_key')

	# Drop the auxiliary columns used for sorting
	weekly_perf = weekly_perf.drop(['week_number', 'month', 'month_number', 'sort_key'], axis=1)

	return weekly_perf

def display_weekly_performance(weekly_perf, period, approved_df, rejected_df, title, container_width):
    # Merge with approved_df and rejected_df on period column
    weekly_perf = weekly_perf.merge(
        approved_df.groupby(period)['ac_no'].nunique().reset_index(), on=period,
        how='left',
        suffixes=('', '_approved')
    )
    weekly_perf = weekly_perf.merge(
        rejected_df.groupby(period)['ac_no'].nunique().reset_index(), on=period,
        how='left',
        suffixes=('', '_rejected')
    )

    # Rename the columns
    weekly_perf = weekly_perf.rename(columns={'ac_no': 'Approved', 'ac_no_rejected': 'Rejected'})

    # Fill NaN values with 0
    weekly_perf = weekly_perf.fillna(0)

    # Set period as index
    weekly_perf.set_index(period, inplace=True)
    weekly_perf = weekly_perf.rename_axis(index={period: 'Week Month'})

    # Display the DataFrame
    st.markdown(f"<div style='text-align:center; font-size:15px; font-weight:bold;'>{title}</div>", unsafe_allow_html=True)
    st.dataframe(
        weekly_perf,
        height=700,
        use_container_width=container_width
    )

def calculate_week_month_metric(df, period):
	# Filter the DataFrame for the current and previous months
	filtered_df = df[
		(df['validated_date'].dt.month == period) 
	]

	# Calculate distinct counts for 'Approved' and 'Rejected'
	approved_counts = filtered_df[filtered_df['approval_status'] == 'Approved'].groupby(['validated_by', 'week_month'])['ac_no'].nunique()
	rejected_counts = filtered_df[filtered_df['approval_status'] == 'Rejected'].groupby(['validated_by', 'week_month'])['ac_no'].nunique()

	# Fill missing values with 0
	approved_counts = approved_counts.unstack().fillna(0)
	rejected_counts = rejected_counts.unstack().fillna(0)

	pivot_ac_no_slrn = filtered_df.pivot_table(
		index='validated_by',
		columns='week_month',
		values=['ac_no', 'slrn'],
		aggfunc={'ac_no': pd.Series.nunique, 'slrn': 'nunique'},
		fill_value=0,
		margins=True,
		margins_name='Grand Total'
	)

	pivot_approved_rejected = pd.concat([
		approved_counts,
		rejected_counts
	], keys=['Approved', 'Rejected'], axis=1)

	# Combine the two pivot tables
	pivot = pd.concat([pivot_ac_no_slrn, pivot_approved_rejected], axis=1)

	pivot = pivot.rename_axis(index={'week_month': 'Week - Month', 'validated_by': 'Validator'})
	pivot = pivot.rename(columns={'ac_no': 'Customers', 'slrn': 'Buildings'})

	pivot.columns.names = [None] * len(pivot.columns.names)

	return pivot

def display_weekly_results(df, container_width):
    current_month = datetime.datetime.now().month
    previous_month = (datetime.datetime.now().month - 2) % 12 + 1  # Adjust for January
    weekly_results = calculate_week_month_metric(df, current_month)

    gb = GridOptionsBuilder()

    gb.configure_column(
        field="validated_by",
        header_name="Validated By",
        width=100,
        pivot=True,
    )

    # Display the results in a Streamlit table
    st.markdown("<div style='text-align:center; font-size:15px; font-weight:bold;'>Weekly Customer-Building Stats by Validator (Current Month)</div>", unsafe_allow_html=True)
    st.dataframe(
        weekly_results, 
        height=700,
        use_container_width=container_width
    )

def calculate_kpis(df, df_selection=None):
    def calculate_fail_rate(rejected, reviewed):
        return (
            rejected / reviewed
        ) if reviewed != 0 else 0.0

    def format_percentage(value):
        return "{:.2%}".format(value)

    def format_float(value):
        return "{:.2f}".format(value)

    today = datetime.date.today()
    formatted_today = today.strftime('%Y-%m-%d')
    yesterday = today - datetime.timedelta(days=1)
    formatted_yesterday = yesterday.strftime('%Y-%m-%d')

    overall_assets_reviewed = int(df["slrn"].nunique())
    overall_customers_reviewed = int(df["ac_no"].nunique())
    overall_assets_approved = int(df[df["approval_status"] == "Approved"]["slrn"].nunique())
    overall_assets_rejected = int(df[df["approval_status"] == "Rejected"]["slrn"].nunique())
    overall_customers_approved = int(df[df["approval_status"] == "Approved"]["ac_no"].nunique())
    overall_customers_rejected = int(df[df["approval_status"] == "Rejected"]["ac_no"].nunique())
    fail_rate_overall = calculate_fail_rate(overall_customers_rejected, overall_customers_reviewed)
    formatted_fail_rate_overall = format_percentage(fail_rate_overall)
    daily_rate_overall = calculate_daily_rate(df)
    formatted_daily_rate_overall = format_float(daily_rate_overall)

    kpis = {
        "overall_assets_reviewed": overall_assets_reviewed,
        "overall_customers_reviewed": overall_customers_reviewed,
        "overall_assets_approved": overall_assets_approved,
        "overall_assets_rejected": overall_assets_rejected,
        "overall_customers_approved": overall_customers_approved,
        "overall_customers_rejected": overall_customers_rejected,
        "fail_rate_overall": formatted_fail_rate_overall,
        "daily_rate_overall": formatted_daily_rate_overall,
    }

    if df_selection is not None:
        filtered_overall_assets_reviewed = int(df_selection["slrn"].nunique())
        filtered_overall_customers_reviewed = int(df_selection["ac_no"].nunique())
        filtered_overall_assets_approved = int(df_selection[df_selection["approval_status"] == "Approved"]["slrn"].nunique())
        filtered_overall_assets_rejected = int(df_selection[df_selection["approval_status"] == "Rejected"]["slrn"].nunique())
        filtered_overall_customers_approved = int(df_selection[df_selection["approval_status"] == "Approved"]["ac_no"].nunique())
        filtered_overall_customers_rejected = int(df_selection[df_selection["approval_status"] == "Rejected"]["ac_no"].nunique())
        fail_rate_filtered = calculate_fail_rate(filtered_overall_customers_rejected, filtered_overall_customers_reviewed)
        formatted_fail_rate_filtered = format_percentage(fail_rate_filtered)
        daily_rate_filtered = calculate_daily_rate(df_selection)
        formatted_daily_rate_filtered = format_float(daily_rate_filtered)

        kpis.update({
            "filtered_overall_assets_reviewed": filtered_overall_assets_reviewed,
            "filtered_overall_customers_reviewed": filtered_overall_customers_reviewed,
            "filtered_overall_assets_approved": filtered_overall_assets_approved,
            "filtered_overall_assets_rejected": filtered_overall_assets_rejected,
            "filtered_overall_customers_approved": filtered_overall_customers_approved,
            "filtered_overall_customers_rejected": filtered_overall_customers_rejected,
            "fail_rate_filtered": formatted_fail_rate_filtered,
            "daily_rate_filtered": formatted_daily_rate_filtered,
        })

    today_data = df[df["validated_date"] == formatted_today]
    assets_reviewed_today = int(today_data["slrn"].nunique())
    customers_reviewed_today = int(today_data["ac_no"].nunique())
    assets_approved_today = int(today_data[today_data["approval_status"] == "Approved"]["slrn"].nunique())
    assets_rejected_today = int(today_data[today_data["approval_status"] == "Rejected"]["slrn"].nunique())
    customers_approved_today = int(today_data[today_data["approval_status"] == "Approved"]["ac_no"].nunique())
    customers_rejected_today = int(today_data[today_data["approval_status"] == "Rejected"]["ac_no"].nunique())
    fail_rate_today = calculate_fail_rate(customers_rejected_today, customers_reviewed_today)
    formatted_fail_rate_today = format_percentage(fail_rate_today)

    yesterday_data = df[df["validated_date"] == formatted_yesterday]
    assets_reviewed_yesterday = int(yesterday_data["slrn"].nunique())
    customers_reviewed_yesterday = int(yesterday_data["ac_no"].nunique())
    assets_approved_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Approved"]["slrn"].nunique())
    assets_rejected_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Rejected"]["slrn"].nunique())
    customers_approved_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Approved"]["ac_no"].nunique())
    customers_rejected_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Rejected"]["ac_no"].nunique())
    fail_rate_yesterday = calculate_fail_rate(customers_rejected_yesterday, customers_reviewed_yesterday)
    formatted_fail_rate_yesterday = format_percentage(fail_rate_yesterday)

    kpis.update({
        "assets_reviewed_today": assets_reviewed_today,
        "customers_reviewed_today": customers_reviewed_today,
        "assets_approved_today": assets_approved_today,
        "assets_rejected_today": assets_rejected_today,
        "customers_approved_today": customers_approved_today,
        "customers_rejected_today": customers_rejected_today,
        "fail_rate_today": formatted_fail_rate_today,
        "assets_reviewed_yesterday": assets_reviewed_yesterday,
        "customers_reviewed_yesterday": customers_reviewed_yesterday,
        "assets_approved_yesterday": assets_approved_yesterday,
        "assets_rejected_yesterday": assets_rejected_yesterday,
        "customers_approved_yesterday": customers_approved_yesterday,
        "customers_rejected_yesterday": customers_rejected_yesterday,
        "fail_rate_yesterday": formatted_fail_rate_yesterday,
    })

    return kpis

#--------------------------------------------------------#
#------------------------- MAIN -------------------------#
#--------------------------------------------------------#
def display_main_tab(df):
	kpis = calculate_kpis(df)

	overall_customers_reviewed = kpis["overall_customers_reviewed"]
	overall_customers_approved = kpis["overall_customers_approved"]
	overall_customers_rejected = kpis["overall_customers_rejected"]
	overall_assets_reviewed = kpis["overall_assets_reviewed"]
	overall_assets_approved = kpis["overall_assets_approved"]
	overall_assets_rejected = kpis["overall_assets_rejected"]
	formatted_fail_rate_overall = kpis["fail_rate_overall"]
	formatted_daily_rate_overall = kpis["daily_rate_overall"]

	customers_reviewed_today= kpis["customers_reviewed_today"]
	customers_approved_today= kpis["customers_approved_today"]
	customers_rejected_today= kpis["customers_rejected_today"]
	assets_reviewed_today = kpis["assets_reviewed_today"]
	assets_approved_today = kpis["assets_approved_today"]
	assets_rejected_today = kpis["assets_rejected_today"]
	customers_reviewed_yesterday = kpis["customers_reviewed_yesterday"]
	customers_approved_yesterday = kpis["customers_approved_yesterday"]
	customers_rejected_yesterday = kpis["customers_rejected_yesterday"]
	assets_reviewed_yesterday = kpis["assets_reviewed_yesterday"]
	assets_approved_yesterday = kpis["assets_approved_yesterday"]
	assets_rejected_yesterday = kpis["assets_rejected_yesterday"]
	formatted_fail_rate_today = kpis["fail_rate_today"]
	formatted_fail_rate_yesterday = kpis["fail_rate_yesterday"]

	st.markdown("<div style='text-align:left; font-size:25px; font-weight:bold;'>Main</div>", unsafe_allow_html=True)

	ct1, ct2 = st.columns((5,5))
	with ct1:
		display_overall_metrics(
			overall_customers_reviewed, overall_customers_approved, overall_customers_rejected, overall_assets_reviewed,
			overall_assets_approved, overall_assets_rejected,
			formatted_fail_rate_overall, formatted_daily_rate_overall
		)

	with ct2:
		display_metrics_today(
			customers_reviewed_today, customers_reviewed_yesterday,
			customers_approved_today, customers_approved_yesterday,
			customers_rejected_today, customers_rejected_yesterday,
			assets_reviewed_today, assets_reviewed_yesterday,
			assets_approved_today, assets_approved_yesterday,
			assets_rejected_today, assets_rejected_yesterday,
			formatted_fail_rate_today, formatted_fail_rate_yesterday
		)

	st.markdown("""---""")

	st.checkbox("Use container width", value=True, key="use_main_container_width")
	c1, c2 = st.columns((4,6))
	with c1:
		approved_df = df[df['approval_status'] == 'Approved']
		rejected_df = df[df['approval_status'] == 'Rejected']

		source_pivot = df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
		source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})

		source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
		source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()

		source_pivot = source_pivot.fillna(0)
		source_pivot = source_pivot.rename_axis(index={'validated_by': 'Validator'})

		gb = GridOptionsBuilder()

		gb.configure_column(
			field="validated_by",
			header_name="Validated By",
			width=100,
			pivot=True,
		)

		st.markdown("<div style='text-align:center; font-size:15px; font-weight:bold;'>Customer-Building Breakdown By Validator (Overall)</div>", unsafe_allow_html=True)
		st.dataframe(
			source_pivot, 
			height = 700,
			use_container_width=st.session_state.use_main_container_width
		)

	with c2:
		period_main = 'week_month_year'
		weekly_perf = calculate_weekly_performance(df, period_main) 
		title = "Customer-Building Weekly Breakdown"
		container_width = st.session_state.use_main_container_width 
		display_weekly_performance(
			weekly_perf,
			period_main, 
			approved_df, 
			rejected_df,
			title,
			container_width
		)

	st.markdown("""---""") 

	if 'key' not in st.session_state:
		st.session_state['use_filtered_wkly_container_width'] = True
	with st.container():
		display_weekly_results(df, container_width)

#--------------------------------------------------------#
#----------------------- FILTERED -----------------------#
#--------------------------------------------------------#
def display_filtered_tab(df, df_selection):
	kpis = calculate_kpis(df, df_selection)

	filtered_overall_customers_reviewed = kpis["filtered_overall_customers_reviewed"]
	filtered_overall_customers_approved = kpis["filtered_overall_customers_approved"]
	filtered_overall_customers_rejected = kpis["filtered_overall_customers_rejected"]
	filtered_overall_assets_reviewed = kpis["filtered_overall_assets_reviewed"]
	filtered_overall_assets_approved = kpis["filtered_overall_assets_approved"]
	filtered_overall_assets_rejected = kpis["filtered_overall_assets_rejected"]
	formatted_fail_rate_filtered = kpis["fail_rate_filtered"]
	formatted_daily_rate_filtered = kpis["daily_rate_filtered"]

	customers_reviewed_today= kpis["customers_reviewed_today"]
	customers_approved_today= kpis["customers_approved_today"]
	customers_rejected_today= kpis["customers_rejected_today"]
	assets_reviewed_today = kpis["assets_reviewed_today"]
	assets_approved_today = kpis["assets_approved_today"]
	assets_rejected_today = kpis["assets_rejected_today"]
	customers_reviewed_yesterday = kpis["customers_reviewed_yesterday"]
	customers_approved_yesterday = kpis["customers_approved_yesterday"]
	customers_rejected_yesterday = kpis["customers_rejected_yesterday"]
	assets_reviewed_yesterday = kpis["assets_reviewed_yesterday"]
	assets_approved_yesterday = kpis["assets_approved_yesterday"]
	assets_rejected_yesterday = kpis["assets_rejected_yesterday"]
	formatted_fail_rate_today = kpis["fail_rate_today"]
	formatted_fail_rate_yesterday = kpis["fail_rate_yesterday"]

	st.markdown("<div style='text-align:left; font-size:25px; font-weight:bold;'>Filtered</div>", unsafe_allow_html=True)
	st.markdown("<div style='text-align:left; font-size:15px; font-weight:bold; font-style:italic;'>Figures here can be sliced and diced!</div>", unsafe_allow_html=True)

	ct1, ct2 = st.columns((5,5))
	with ct1:
		display_overall_metrics(
			filtered_overall_customers_reviewed, filtered_overall_customers_approved, filtered_overall_customers_rejected, filtered_overall_assets_reviewed,
			filtered_overall_assets_approved, filtered_overall_assets_rejected,
			formatted_fail_rate_filtered, formatted_daily_rate_filtered
		)
		
	with ct2:
		display_metrics_today(
			customers_reviewed_today, customers_reviewed_yesterday,
			customers_approved_today, customers_approved_yesterday,
			customers_rejected_today, customers_rejected_yesterday,
			assets_reviewed_today, assets_reviewed_yesterday,
			assets_approved_today, assets_approved_yesterday,
			assets_rejected_today, assets_rejected_yesterday,
			formatted_fail_rate_today, formatted_fail_rate_yesterday
		)

	st.markdown("""---""")  

	st.checkbox("Use container width", value=True, key="use_filtered_container_width")
	c1, c2 = st.columns((4,6))
	with c1:
		approved_df_selection = df_selection[df_selection['approval_status'] == 'Approved']
		rejected_df_selection = df_selection[df_selection['approval_status'] == 'Rejected']

		if df_selection is None:
			st.markdown("#### (No data available)")
		else:
			filtered_source_pivot = df_selection.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total', fill_value=0)
			filtered_source_pivot = filtered_source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})

			# Calculate the unique counts for Approved and Rejected
			filtered_source_pivot['Approved'] = approved_df_selection.groupby('validated_by')['ac_no'].nunique()
			filtered_source_pivot['Rejected'] = rejected_df_selection.groupby('validated_by')['ac_no'].nunique()

			# Fill NaN values with 0
			filtered_source_pivot = filtered_source_pivot.fillna(0)
			filtered_source_pivot = filtered_source_pivot.rename_axis(index={'validated_by': 'Validator'})

			# Display the pivot table
			st.markdown("<div style='text-align:center; font-size:15px; font-weight:bold;'>Customer-Building Breakdown By Validator (Filtered)</div>", unsafe_allow_html=True)
			st.dataframe(
				filtered_source_pivot,
				height = 700,  
				use_container_width=st.session_state.use_filtered_container_width
			)

	with c2:
		period_fil = 'week_month'
		weekly_perf = calculate_weekly_performance(df_selection, period_fil) 
		title = "Customer-Building Weekly Breakdown (Filtered)"
		container_width = st.session_state.use_filtered_container_width 
		display_weekly_performance(
			weekly_perf, 
			period_fil,
			approved_df_selection, 
			rejected_df_selection,
			title,
			container_width
		)

	st.markdown("""---""") 

	if 'key' not in st.session_state:
		st.session_state['use_filtered_wkly_container_width'] = True
	with st.container():
		display_weekly_results(df, container_width)


def display_metrics_tabs(df, df_selection):
	st.markdown("<div style='text-align:center; font-size:30px; font-weight:bold;'>Metrics</div>", unsafe_allow_html=True)
	st.markdown("""---""")

	main_tab, filtered_tab = st.tabs(["Main", "Filtered"])

	with main_tab:
		display_main_tab(df)

	with filtered_tab:
		display_filtered_tab(df, df_selection)

	st.markdown("""---""")  