import streamlit as st
import base64
from streamlit.components.v1 import html

from PATHS_navigationBar import NAVBAR_PATHS, SETTINGS, ANALYSIS_DROPDOWN


def inject_custom_css():
    with open('assets_navigationBar/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def get_current_route():
    try:
        #st.write(st.experimental_get_query_params()) ############ moi  ############
        return st.experimental_get_query_params()['nav'][0]
    except:
        return None


def navbar_component():
    with open("assets_navigationBar/images/settings.png", "rb") as image_file:
        image_as_base64 = base64.b64encode(image_file.read())

    navbar_items = ''
    #st.write(NAVBAR_PATHS.items())  ############ moi  ############
    for key, value in NAVBAR_PATHS.items():
        navbar_items += (f'<a class="navitem" href="/?nav={value}">{key}</a>')
    #st.write(navbar_items)  ############ moi  ############

    settings_items = ''
    for key, value in SETTINGS.items():
        settings_items += (
            f'<a href="/?nav={value}" class="settingsNav">{key}</a>')
        
    analysis_items = ''
    for key, value in ANALYSIS_DROPDOWN.items():
        analysis_items += (
            f'<a href="/?nav={value}" class="analysissNav">{key}</a>')

    component = rf'''
            <nav class="container navbar" id="navbar">
                <ul class="navlist">
                {navbar_items}
                </ul>
                <div class="dropdown" id="settingsDropDown">
                    <img class="dropbtn" src="data:image/png;base64, {image_as_base64.decode("utf-8")}"/>
                    <div id="myDropdown" class="dropdown-content">
                        {settings_items}
                    </div>
                </div>
                 <div class="dropdown_anal" id="settingsDropDown111">
                    <div id="myDropdown" class="dropdown-content">
                        {analysis_items}
                    </div>
                </div>
                
            </nav>
            '''
    st.markdown(component, unsafe_allow_html=True)
    js = '''
    <script>
        // navbar elements
        var navigationTabs = window.parent.document.getElementsByClassName("navitem");
        var cleanNavbar = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < navigationTabs.length; i++) {
            cleanNavbar(navigationTabs[i]);
        }
        
        // Dropdown hide / show
        var dropdown = window.parent.document.getElementById("settingsDropDown");
        dropdown.onclick = function() {
            var dropWindow = window.parent.document.getElementById("myDropdown");
            if (dropWindow.style.visibility == "hidden"){
                dropWindow.style.visibility = "visible";
            }else{
                dropWindow.style.visibility = "hidden";
            }
        };
        
        var settingsNavs = window.parent.document.getElementsByClassName("settingsNav");
        var cleanSettings = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < settingsNavs.length; i++) {
            cleanSettings(settingsNavs[i]);
        }
    </script>
    '''
    html(js)