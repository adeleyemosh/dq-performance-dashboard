import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
from streamlit_extras.metric_cards import style_metric_cards
from modules.menu import streamlit_menu

# 1=sidebar menu, 2=horizontal menu, 3=horizontal menu w/ custom menu
# DESIGN_NO = 2
selected = streamlit_menu()

def display_kpi_metrics(df, df_selection):
	# ---- TOP KPI's ----
	overall_assets_reviewed = int(df["slrn"].nunique())
	overall_customers_reviewed = int(df["ac_no"].nunique())
	total_assets_approved = int(df[df["approval_status"] == "Approved"]["slrn"].nunique())
	total_assets_rejected = int(df[df["approval_status"] == "Rejected"]["slrn"].nunique())
	total_customers_approved = int(df[df["approval_status"] == "Approved"]["ac_no"].nunique())
	total_customers_rejected = int(df[df["approval_status"] == "Rejected"]["ac_no"].nunique())
	
	filtered_overall_assets_reviewed = int(df_selection["slrn"].nunique())
	filtered_overall_customers_reviewed = int(df_selection["ac_no"].nunique())
	filtered_total_assets_approved = int(df_selection[df_selection["approval_status"] == "Approved"]["slrn"].nunique())
	filtered_total_assets_rejected = int(df_selection[df_selection["approval_status"] == "Rejected"]["slrn"].nunique())
	filtered_total_customers_approved = int(df_selection[df_selection["approval_status"] == "Approved"]["ac_no"].nunique())
	filtered_total_customers_rejected = int(df_selection[df_selection["approval_status"] == "Rejected"]["ac_no"].nunique())

	# today = datetime.date.today().strftime('%Y-%m-%d')
	today = datetime.date.today()
	formatted_today = today.strftime('%Y-%m-%d')
	today_data = df[df["validated_date"] == formatted_today] # dataframe for today data only
	assets_reviewed_today = int(today_data["slrn"].nunique())
	customers_reviewed_today = int(today_data["ac_no"].nunique())
	assets_approved_today = int(today_data[today_data["approval_status"] == "Approved"]["slrn"].nunique())
	assets_rejected_today = int(today_data[today_data["approval_status"] == "Rejected"]["slrn"].nunique())
	customers_approved_today = int(today_data[today_data["approval_status"] == "Approved"]["ac_no"].nunique())
	customers_rejected_today = int(today_data[today_data["approval_status"] == "Rejected"]["ac_no"].nunique())

	yesterday = today - datetime.timedelta(days=1)
	formatted_yesterday = yesterday.strftime('%Y-%m-%d')
	yesterday_data = df[df["validated_date"] == formatted_yesterday] # dataframe for yesterday's data only
	assets_reviewed_yesterday = int(yesterday_data["slrn"].nunique())
	customers_reviewed_yesterday = int(yesterday_data["ac_no"].nunique())
	assets_approved_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Approved"]["slrn"].nunique())
	assets_rejected_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Rejected"]["slrn"].nunique())
	customers_approved_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Approved"]["ac_no"].nunique())
	customers_rejected_yesterday = int(yesterday_data[yesterday_data["approval_status"] == "Rejected"]["ac_no"].nunique())

	
	st.markdown("<div style='text-align:center; font-size:30px; font-weight:bold;'>Metrics</div>", unsafe_allow_html=True)
	st.markdown("""---""")

	main_tab, filtered_tab = st.tabs(["Main", "Filtered"])

	with main_tab:
		st.markdown("<div style='text-align:left; font-size:25px; font-weight:bold;'>Main</div>", unsafe_allow_html=True)
		# st.markdown("""---""")
		
		col1, col2, col3, col4, col5, col6 = st.columns(6)

		col1.metric(label="Overall Assets Reviewed", value=f"{overall_assets_reviewed:,}")
		col2.metric(label="Overall Customers Reviewed", value=f"{overall_customers_reviewed:,}")
		col3.metric(label="Total Assets Approved", value=f"{total_assets_approved:,}")
		col4.metric(label="Total Assets Rejected", value=f"{total_assets_rejected:,}")
		col5.metric(label="Total Customers Approved", value=f"{total_customers_approved:,}")
		col6.metric(label="Total Customers Rejecetd", value=f"{total_customers_rejected:,}")

		col1.metric(label="Assets Reviewed Today", value=assets_reviewed_today, delta=assets_reviewed_yesterday, help="Assets reviewed today versus yesterday")
		col2.metric(label="Customers Reviewed Today", value=customers_reviewed_today, delta=customers_reviewed_yesterday, help="Customers reviewed today versus yesterday")
		col3.metric(label="Assets Approved Today", value=assets_approved_today, delta=assets_approved_yesterday, help="Assets approved today versus yesterday")
		col4.metric(label="Assets Rejected Today", value=assets_rejected_today, delta=assets_rejected_yesterday, help="Assets rejected today versus yesterday")
		col5.metric(label="Customers Approved Today", value=customers_approved_today, delta=customers_approved_yesterday, help="Customers approved today versus yesterday")
		col6.metric(label="Customers Rejected Today", value=customers_rejected_today, delta=customers_rejected_yesterday, help="Customers rejected today versus yesterday")


		st.markdown("""---""")  

		st.checkbox("Use container width", value=True, key="use_container_width")
		c1, c2 = st.columns((4,6))
		with c1:

			# Filter the DataFrame for Approved and Rejected rows
			approved_df = df[df['approval_status'] == 'Approved']
			rejected_df = df[df['approval_status'] == 'Rejected']

			# Calculate the unique counts for Customers and Buildings for each 'validated_by'
			source_pivot = df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
			source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})

			# Calculate the unique counts for Approved and Rejected
			source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
			source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()

			# Fill NaN values with 0
			source_pivot = source_pivot.fillna(0)

			# Display the pivot table
			st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status</div>", unsafe_allow_html=True)
			st.dataframe(source_pivot, use_container_width=st.session_state.use_container_width)


		with c2:
			df['validated_date'] = pd.to_datetime(df['validated_date'])

			# Filter the DataFrame for the current month
			current_month = datetime.datetime.now().month
			filtered_df = df[df['validated_date'].dt.month == current_month]

			# Create a date range for the current month
			start_date = datetime.datetime(datetime.datetime.now().year, current_month, 1)
			end_date = start_date + timedelta(days=30)  # Adjust the number of days as needed
			date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')

			# Initialize an empty list to store weekly DataFrames
			weekly_dfs = []

			# Iterate through the date range and calculate counts for each week
			for i in range(len(date_range) - 1):
				week_start = date_range[i]
				week_end = date_range[i + 1]
				
				week_df = filtered_df[(filtered_df['validated_date'] >= week_start) & (filtered_df['validated_date'] < week_end)]
				
				# Filter the DataFrame for Approved and Rejected rows
				approved_df = week_df[week_df['approval_status'] == 'Approved']
				rejected_df = week_df[week_df['approval_status'] == 'Rejected']
				
				# Calculate the unique counts for Customers and Buildings for each 'validated_by'
				source_pivot = week_df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
				source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})
				
				# Calculate the unique counts for Approved and Rejected
				source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
				source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()
				
				# Fill NaN values with 0
				source_pivot = source_pivot.fillna(0)
				
				# Append the week's DataFrame to the list
				weekly_dfs.append(source_pivot)

			# Merge the weekly DataFrames based on 'validated_by'
			weekly_results = pd.concat(weekly_dfs)

			# Display the results in a Streamlit table
			st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status (Weekly)</div>", unsafe_allow_html=True)
			st.dataframe(weekly_results, use_container_width=st.session_state.use_container_width)

	with filtered_tab:
		st.markdown("<div style='text-align:left; font-size:25px; font-weight:bold;'>Filtered</div>", unsafe_allow_html=True)
		st.markdown("<div style='text-align:left; font-size:15px; font-weight:bold; font-style:italic;'>Figures here can be sliced and diced!</div>", unsafe_allow_html=True)
		# st.markdown("""---""")
		
		col1, col2, col3, col4, col5, col6 = st.columns(6)

		col1.metric(label="Overall Assets Reviewed", value=f"{filtered_overall_assets_reviewed:,}")
		col2.metric(label="Overall Customers Reviewed", value=f"{filtered_overall_customers_reviewed:,}")
		col3.metric(label="Total Assets Approved", value=f"{filtered_total_assets_approved:,}")
		col4.metric(label="Total Assets Rejected", value=f"{filtered_total_assets_rejected:,}")
		col5.metric(label="Total Customers Approved", value=f"{filtered_total_customers_approved:,}")
		col6.metric(label="Total Customers Rejecetd", value=f"{filtered_total_customers_rejected:,}")

		col1.metric(label="Assets Reviewed Today", value=assets_reviewed_today, delta=assets_reviewed_yesterday, help="Assets reviewed today versus yesterday")
		col2.metric(label="Customers Reviewed Today", value=customers_reviewed_today, delta=customers_reviewed_yesterday, help="Customers reviewed today versus yesterday")
		col3.metric(label="Assets Approved Today", value=assets_approved_today, delta=assets_approved_yesterday, help="Assets approved today versus yesterday")
		col4.metric(label="Assets Rejected Today", value=assets_rejected_today, delta=assets_rejected_yesterday, help="Assets rejected today versus yesterday")
		col5.metric(label="Customers Approved Today", value=customers_approved_today, delta=customers_approved_yesterday, help="Customers approved today versus yesterday")
		col6.metric(label="Customers Rejected Today", value=customers_rejected_today, delta=customers_rejected_yesterday, help="Customers rejected today versus yesterday")

		st.markdown("""---""")  

		st.checkbox("Use container width", value=True, key="use_filtered_container_width")
		c1, c2 = st.columns((4,6))
		with c1:
			# Filter the DataFrame for Approved and Rejected rows
			approved_df = df[df['approval_status'] == 'Approved']
			rejected_df = df[df['approval_status'] == 'Rejected']

			if df_selection is None:
				st.markdown("#### Figures by Field Enumerator (No data available)")
			else:
				filtered_source_pivot = df_selection.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total', fill_value=0)
				filtered_source_pivot = filtered_source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})

				# Calculate the unique counts for Approved and Rejected
				filtered_source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
				filtered_source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()

				# Fill NaN values with 0
				filtered_source_pivot = filtered_source_pivot.fillna(0)

				# Display the pivot table
				st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status</div>", unsafe_allow_html=True)
				st.dataframe(filtered_source_pivot, use_container_width=st.session_state.use_filtered_container_width)


		with c2:
			# from datetime import datetime, timedelta

			df_selection['validated_date'] = pd.to_datetime(df_selection['validated_date'])

			# Filter the DataFrame for the current month
			current_month = datetime.datetime.now().month
			filtered_df = df_selection[df_selection['validated_date'].dt.month == current_month]

			# Create a date range for the current month
			start_date = datetime.datetime(datetime.datetime.now().year, current_month, 1)
			end_date = start_date + timedelta(days=30)  # Adjust the number of days as needed
			date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')

			# Initialize an empty list to store weekly DataFrames
			weekly_dfs = []

			# Iterate through the date range and calculate counts for each week
			for i in range(len(date_range) - 1):
				week_start = date_range[i]
				week_end = date_range[i + 1]
				
				week_df = filtered_df[(filtered_df['validated_date'] >= week_start) & (filtered_df['validated_date'] < week_end)]
				
				# Filter the DataFrame for Approved and Rejected rows
				approved_df = week_df[week_df['approval_status'] == 'Approved']
				rejected_df = week_df[week_df['approval_status'] == 'Rejected']
				
				# Calculate the unique counts for Customers and Buildings for each 'validated_by'
				source_pivot = week_df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
				source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})
				
				# Calculate the unique counts for Approved and Rejected
				source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
				source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()
				
				# Fill NaN values with 0
				source_pivot = source_pivot.fillna(0)
				
				# Append the week's DataFrame to the list
				weekly_dfs.append(source_pivot)

			# Merge the weekly DataFrames based on 'validated_by'
			weekly_results = pd.concat(weekly_dfs)

			# Display the results in a Streamlit table
			st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status (Weekly)</div>", unsafe_allow_html=True)
			st.dataframe(weekly_results, use_container_width=st.session_state.use_filtered_container_width)

	
	# Styling the KPI cards
	if selected == 'AEDC':
		style_metric_cards(border_left_color="blue",  box_shadow=True, border_radius_px=5, background_color="#FFF")
	if selected == 'ECG':
		style_metric_cards(border_left_color="red", box_shadow=True, border_radius_px=5, background_color="#FFF", )



# def display_table_metrics(df, df_selection=None):
# 	# st.checkbox("Use container width", value=True, key="use_container_width")
# 	# main_tab, filtered_tab = st.tabs(["Main", "Filtered"])
# 	# with main_tab:
# 	c1, c2 = st.columns((4,6))
# 	with c1:

# 		# Filter the DataFrame for Approved and Rejected rows
# 		approved_df = df[df['approval_status'] == 'Approved']
# 		rejected_df = df[df['approval_status'] == 'Rejected']

# 		# Calculate the unique counts for Customers and Buildings for each 'validated_by'
# 		source_pivot = df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
# 		source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})

# 		# Calculate the unique counts for Approved and Rejected
# 		source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
# 		source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()

# 		# Fill NaN values with 0
# 		source_pivot = source_pivot.fillna(0)

# 		# Display the pivot table
# 		st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status</div>", unsafe_allow_html=True)
# 		st.dataframe(source_pivot, use_container_width=st.session_state.use_container_width)


# 	with c2:
# 		from datetime import datetime, timedelta

# 		df['validated_date'] = pd.to_datetime(df['validated_date'])

# 		# Filter the DataFrame for the current month
# 		current_month = datetime.now().month
# 		filtered_df = df[df['validated_date'].dt.month == current_month]

# 		# Create a date range for the current month
# 		start_date = datetime(datetime.now().year, current_month, 1)
# 		end_date = start_date + timedelta(days=30)  # Adjust the number of days as needed
# 		date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')

# 		# Initialize an empty list to store weekly DataFrames
# 		weekly_dfs = []

# 		# Iterate through the date range and calculate counts for each week
# 		for i in range(len(date_range) - 1):
# 			week_start = date_range[i]
# 			week_end = date_range[i + 1]
			
# 			week_df = filtered_df[(filtered_df['validated_date'] >= week_start) & (filtered_df['validated_date'] < week_end)]
			
# 			# Filter the DataFrame for Approved and Rejected rows
# 			approved_df = week_df[week_df['approval_status'] == 'Approved']
# 			rejected_df = week_df[week_df['approval_status'] == 'Rejected']
			
# 			# Calculate the unique counts for Customers and Buildings for each 'validated_by'
# 			source_pivot = week_df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
# 			source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})
			
# 			# Calculate the unique counts for Approved and Rejected
# 			source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
# 			source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()
			
# 			# Fill NaN values with 0
# 			source_pivot = source_pivot.fillna(0)
			
# 			# Append the week's DataFrame to the list
# 			weekly_dfs.append(source_pivot)

# 		# Merge the weekly DataFrames based on 'validated_by'
# 		weekly_results = pd.concat(weekly_dfs)

# 		# Display the results in a Streamlit table
# 		st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status (Weekly)</div>", unsafe_allow_html=True)
# 		st.dataframe(weekly_results, use_container_width=st.session_state.use_container_width)

# 	# # with filtered_tab:
# 	# c1, c2 = st.columns((4,6))
# 	# with c1:
# 	# 	# Filter the DataFrame for Approved and Rejected rows
# 	# 	approved_df = df[df['approval_status'] == 'Approved']
# 	# 	rejected_df = df[df['approval_status'] == 'Rejected']

# 	# 	if df_selection is None:
# 	# 		st.markdown("#### Figures by Field Enumerator (No data available)")
# 	# 	else:
# 	# 		filtered_source_pivot = df_selection.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total', fill_value=0)
# 	# 		filtered_source_pivot = filtered_source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})

# 	# 		# Calculate the unique counts for Approved and Rejected
# 	# 		filtered_source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
# 	# 		filtered_source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()

# 	# 		# Fill NaN values with 0
# 	# 		filtered_source_pivot = filtered_source_pivot.fillna(0)

# 	# 		# Display the pivot table
# 	# 		st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status</div>", unsafe_allow_html=True)
# 	# 		st.dataframe(filtered_source_pivot, use_container_width=st.session_state.use_container_width)


# 	# with c2:
# 	# 	from datetime import datetime, timedelta

# 	# 	df_selection['validated_date'] = pd.to_datetime(df_selection['validated_date'])

# 	# 	# Filter the DataFrame for the current month
# 	# 	current_month = datetime.now().month
# 	# 	filtered_df = df_selection[df_selection['validated_date'].dt.month == current_month]

# 	# 	# Create a date range for the current month
# 	# 	start_date = datetime(datetime.now().year, current_month, 1)
# 	# 	end_date = start_date + timedelta(days=30)  # Adjust the number of days as needed
# 	# 	date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')

# 	# 	# Initialize an empty list to store weekly DataFrames
# 	# 	weekly_dfs = []

# 	# 	# Iterate through the date range and calculate counts for each week
# 	# 	for i in range(len(date_range) - 1):
# 	# 		week_start = date_range[i]
# 	# 		week_end = date_range[i + 1]
			
# 	# 		week_df = filtered_df[(filtered_df['validated_date'] >= week_start) & (filtered_df['validated_date'] < week_end)]
			
# 	# 		# Filter the DataFrame for Approved and Rejected rows
# 	# 		approved_df = week_df[week_df['approval_status'] == 'Approved']
# 	# 		rejected_df = week_df[week_df['approval_status'] == 'Rejected']
			
# 	# 		# Calculate the unique counts for Customers and Buildings for each 'validated_by'
# 	# 		source_pivot = week_df.pivot_table(index="validated_by", values=['slrn', 'ac_no'], aggfunc={"slrn": "nunique", "ac_no": "nunique"}, margins=False, margins_name='Total')
# 	# 		source_pivot = source_pivot.rename(columns={"slrn": "Buildings", "ac_no": "Customers"})
			
# 	# 		# Calculate the unique counts for Approved and Rejected
# 	# 		source_pivot['Approved'] = approved_df.groupby('validated_by')['ac_no'].nunique()
# 	# 		source_pivot['Rejected'] = rejected_df.groupby('validated_by')['ac_no'].nunique()
			
# 	# 		# Fill NaN values with 0
# 	# 		source_pivot = source_pivot.fillna(0)
			
# 	# 		# Append the week's DataFrame to the list
# 	# 		weekly_dfs.append(source_pivot)

# 	# 	# Merge the weekly DataFrames based on 'validated_by'
# 	# 	weekly_results = pd.concat(weekly_dfs)

# 	# 	# Display the results in a Streamlit table
# 	# 	st.markdown("<div style='text-align:center; font-size:20px; font-weight:bold;'>Overall Customers and Buildings By Asset Status (Weekly)</div>", unsafe_allow_html=True)
# 	# 	st.dataframe(weekly_results, use_container_width=st.session_state.use_container_width)

# 	st.markdown("""---""")
