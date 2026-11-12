import streamlit as st

import model

st.set_page_config(page_title="URL DETECTOR Dashboard")

st.title("URL DETECTOR dashboard")

url = st.text_input("URL")

if st.button("Check link"):
    try:
        probability = model.predict(url)
        st.write(probability)
    except NotImplementedError:
        st.warning("Model not implemented yet.")