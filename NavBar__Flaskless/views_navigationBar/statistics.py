import streamlit as st 
from views_navigationBar.streamlit_radio_options import app_transform, app_viz, app_stats


def load_view():
    #st.title('Data Visualization')
    
    st.markdown("<h2 style='text-align: center; color: black;'>Data Statistics</h2>", unsafe_allow_html=True)

    

    PAGES = {
        "App1": app_transform,
        "App2": app_viz,
        "App3": app_stats
    }
    
    st.sidebar.title('Data Statistics')
    selection = "App3"
    #st.write(selection)
    page = PAGES[selection]
    #st.write(page) # views_navigationBar.streamlit_radio_options.app1 (.app2 if we choice app2)
    page.app()