import streamlit as st
import base64

def show_raw_data(df_selection):
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(df_selection)
        csv = df_selection.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="raw_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown("---")