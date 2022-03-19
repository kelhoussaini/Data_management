# app_transform.py

import streamlit as st
import requests

import xlsxwriter

import numpy as np
import pandas as pd
import PyPDF2
from PyPDF2 import PdfFileReader

import base64
import io
import datetime
from styleframe import StyleFrame

from UliPlot.XLSX import auto_adjust_xlsx_column_width

from views_navigationBar.utils.params import Utils
from views_navigationBar.utils.formats_excel import Formats
from views_navigationBar.utils.transform import Transform #  get worksheet

import os

# Data visualization
import plotly.graph_objects as go
import plotly.express as px


from views_navigationBar import functions

from streamlit.components.v1 import html


def app():
    
    
    # Initialization
    st.session_state = functions.Initialize_session_state()

    xlsFilepath = 'Facilis___IA_BTP.xlsx'
    # Add a selectbox to the sidebar:

    name_sheet = st.sidebar.selectbox(
        'Name_sheet',
        ('TOUT', 'Frs', 'Stat', 'Virement'))#Unaccompanied      Group of people        


    text_input = "Choose a source (Excel) file"
    st.markdown(f'<h4 style="text-align: center; color: black;">{text_input}</h4>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader('', accept_multiple_files=True)

    if uploaded_files:

        df = functions.get_uploaded_files(Uploaded_Files = uploaded_files, NAME_SHEET  = name_sheet)
        st.dataframe(df)   
        st.session_state["dataframe"] = df    

        checkbox_val = st.checkbox("Transform")
        if checkbox_val:

            # transform, concatenate , organize and rename columns
            text_input = "Transformed Data"
            st.markdown(f'<h4 style="text-align: center; color: black;">{text_input}</h4>', unsafe_allow_html=True)
            concat = functions.Transform_columns(Uploaded_File = uploaded_files[0], original_df=df)
            st.dataframe(concat)    
            st.session_state["dataframe"] = concat  
            res = st.session_state["dataframe"]    
            #st.session_state["dataframe"]

            next_step = st.selectbox('Next_step',   ('Please select', 'Upload file',
                                                     'Fill missing values', 'Display and Export Data to Excel')) 

            #st.session_state
            if next_step == 'Fill missing values':  

                st.session_state = functions.Fill_missing_values(dataframe = res)
                st.session_state["next_step"] = 1

            elif next_step == "Upload file":

                reso = functions.Initialize_uploaded_session_state(dict_session = st.session_state)

                pdf_file = st.file_uploader("Please Choose a file",  type = "pdf", accept_multiple_files=False) 

                functions.read_file(file = pdf_file, data=reso)

            elif next_step == 'Display and Export Data to Excel': 
                st.session_state["next_step"] = 2
            else:
                st.session_state["next_step"] = 0

    if st.session_state["next_step"] != 0:

        if st.session_state["next_step"] == 1 :
            reso = st.session_state["filled_dataframe"]  # the 3 keys have been filled by the same dataframe after transformtion
        else:
            reso = st.session_state["dataframe"] 

        checkbox_dataframe = st.checkbox("Display data")

        def highlight_max(s):
            is_max = s == s.max()
            return ['background: lightgreen' if cell else '' for cell in is_max]


        if checkbox_dataframe:          
            # Highlighting the maximum values of
            # last 2 columns
            reso.style.apply(highlight_max)
            st.dataframe(reso)


        checkbox_export_file = st.checkbox("Export data to Excel file")
        if checkbox_export_file:
            Utils(dataframe = reso, xlsFilepath=xlsFilepath).steps_grouped(apply = True, link=True)

            checkbox_stat = st.checkbox("Statistics")
            if checkbox_stat:
                st.session_state["Statistics"] = True

    else:
        st.markdown("####  ###")