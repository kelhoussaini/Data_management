import streamlit as st
import utils_navigationBar as utl
from views_navigationBar import home,about,analysis,options,configuration,visualization,management,statistics


from views_navigationBar import functions
from views_navigationBar.streamlit_radio_options import functions


# Page Configuration
st.set_page_config(layout="wide", page_title='Navbar sample')
st.set_option('deprecation.showPyplotGlobalUse', False)


utl.inject_custom_css()
utl.navbar_component()

def navigation():
    route = utl.get_current_route()
    #st.write(route)  ############ moi  ############

    if route == "home":
        home.load_view()
    elif route == "about":
        about.load_view()
    elif route == "management":
        management.load_view() 
    elif route == "statistics":
        statistics.load_view()
    elif route == "analysis":
        analysis.load_view()
    elif route == "options":
        options.load_view()
    elif route == "configuration":
        configuration.load_view()
    elif route == "visualization":
        visualization.load_view()
    elif route == None:
        home.load_view()
        
navigation()
