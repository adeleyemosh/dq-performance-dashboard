import streamlit as st
import base64
import pandas as pd

def show_raw_data(df_selection):
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(df_selection)
        csv = df_selection.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="raw_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown("---")

def load_and_preprocess_data(new_customer_data, existing_customer_data, v2_cus_data=None):
    data = pd.concat([new_customer_data, existing_customer_data, v2_cus_data])

    data = data.drop_duplicates(subset=['meter_no'])
    
    invalid_validators = [
        'DevAdmin', 
        'Christianbackend'
    ]

    data = data[
        (data['validated_by'].notnull()) &
        (~data['validated_by'].isin(invalid_validators))
    ]

    data["validated_date"] = pd.to_datetime(data["validated_date"])
    data["val_date"] = data["validated_date"].dt.strftime('%Y-%m-%d')
    data['year'] = pd.DatetimeIndex(data['validated_date']).year
    data['month'] = pd.DatetimeIndex(data['validated_date']).month

    return data