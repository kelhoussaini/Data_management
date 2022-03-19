import streamlit as st 
from views_navigationBar.streamlit_radio_options import app_transform, app_viz


def load_view():
    st.title('Options Page')
    

    PAGES = {
        "App1": app_transform,
        "App2": app_viz
    }
    
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    st.write(selection)
    page = PAGES[selection]
    #st.write(page) # views_navigationBar.streamlit_radio_options.app1 (.app2 if we choice app2)
    page.app()