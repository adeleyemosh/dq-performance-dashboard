import streamlit as st
from modules.menu import streamlit_menu

# 1=sidebar menu, 2=horizontal menu, 3=horizontal menu w/ custom menu
DESIGN_NO = 2
selected = streamlit_menu(design=DESIGN_NO)

def dashboard_header(image1, image2, title):
	hd1, hd2, hd3, hd4, hd5 = st.columns(5)

	with hd1:
		if selected == "ECG":
			st.image(image2, width=125)
		if selected == "AEDC":
			st.image(image2, width=250)

	with hd3:
		st.markdown(f"<div style='text-align:center; font-size:40px; font-weight:bold;'>{title}</div>", unsafe_allow_html=True)

	with hd5:
		if selected == "ECG":
			st.image(image1, width=300)
		if selected == "AEDC":
			st.image(image1, width=300)
	
	st.markdown("---")