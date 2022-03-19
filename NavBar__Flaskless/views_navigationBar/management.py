import streamlit as st 
from views_navigationBar.streamlit_radio_options import app_transform, app_viz, app_stats


def load_view():
    st.title('Data Management')
    

    PAGES = {
        "App1": app_transform,
        "App2": app_viz,
        "App3": app_stats
    }
    
    st.sidebar.title('Data Management')
    selection = "App1"
    #st.write(selection)
    page = PAGES[selection]
    #st.write(page) # views_navigationBar.streamlit_radio_options.app1 (.app2 if we choice app2)
    page.app()