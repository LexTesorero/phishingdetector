import streamlit as st

import model

# "baseline" or "enhanced"
MODEL = "enhanced"

st.set_page_config(page_title="URL DETECTOR Dashboard")
st.title("URL DETECTOR dashboard")


@st.cache_resource
def _load():
    model.load_models()
    return True


_load()

url = st.text_input("URL")

if st.button("Check link") and url.strip():
    st.metric("Phishing probability", f"{model.predict(url.strip(), MODEL):.2%}")
