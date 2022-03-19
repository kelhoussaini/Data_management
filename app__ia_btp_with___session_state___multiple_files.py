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

import utils
from utils.params import Utils
from utils.formats_excel import Formats
from utils.transform import Transform #  get worksheet

import os

# Data visualization
import plotly.graph_objects as go
import plotly.express as px


import functions

# this slider allows the user to select a number of lines
# to display in the dataframe

#streamlit run app.py

'''
# IA -- BTP 
'''
 
# Initialization
st.session_state = functions.Initialize_session_state()

xlsFilepath = 'Facilis___IA_BTP.xlsx'
# Add a selectbox to the sidebar:

name_sheet = st.sidebar.selectbox(
    'name_sheet',
    ('TOUT', 'Frs', 'Stat', 'Virement'))#Unaccompanied      Group of people        


text_input = "Choose a source (Excel) file"
uploaded_files = st.file_uploader(text_input, accept_multiple_files=True)

if uploaded_files:

    df = functions.get_uploaded_files(Uploaded_Files = uploaded_files, NAME_SHEET  = name_sheet)
    st.dataframe(df)   
    st.session_state["dataframe"] = df    

    checkbox_val = st.checkbox("Transform")
    if checkbox_val:
        
        # transform, concatenate , organize and rename columns
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
            
#st.session_state
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
    
        
        
if st.session_state["Statistics"]:
    Stat = st.selectbox('',  
                             ('Please select', 
                              'Sum amounts by week number', 'Count bills number by provider')) 
    # add id as the primary key.
    reso['id'] = list(np.arange(1, len(reso)+1))
    #st.dataframe(concat)

    #Multiple rows are with the same provider
    # We make a new column to represent providers by their id.
    #Using for loop,dictionary and map functions 

    def map_index(liste=[], start_id=1, end_id=11): #end_id=len(liste)+1
        list2 = list(np.arange(start_id, end_id))

        dic = {}
        for i,j in enumerate(liste):
            dic[j] = i+1
        return dic

    L = list(reso['Fournisseurs IA-BTP'].unique())

    func = map_index(liste = L, start_id = 1, end_id=len(L)+1)
    reso["id_fournisseurs"] = reso["Fournisseurs IA-BTP"].map(func)

    if Stat == 'Sum amounts by week number':

        res = functions.sql_queries(dataframe = reso, type_query = "sum")
        list_cols = ['Semaine', 'Montant_total', 'Nbre factures']
        st.dataframe(res[list_cols])

        checkbox_viz = st.checkbox("Visualization")
        if checkbox_viz:
            functions.graphics_sum(dataframe = res, list_cols = list_cols)    

    if Stat == 'Count bills number by provider':
        
        counts = functions.sql_queries(dataframe = reso, type_query = "counts")       
        list_cols = ['Fournisseurs IA-BTP','Nbre factures']
        st.dataframe(counts[list_cols])

        checkbox_viz = st.checkbox("Visualization")
        if checkbox_viz:
            functions.graphics_count(dataframe = counts, list_cols = list_cols)    


#url = 'http://127.0.0.1:8000/make_preds'
params = dict(
   name_sheet=name_sheet)

# enter here the address of your initial api deployed to heroku , flask api
#url = f'http://0.0.0.0:8000/make_preds?CODE_GENDER={CODE_GENDER}&FLAG_OWN_CAR={FLAG_OWN_CAR}&OCCUPATION_TYPE={OCCUPATION_TYPE}&NAME_INCOME_TYPE={NAME_INCOME_TYPE}&NAME_TYPE_SUITE={NAME_TYPE_SUITE}&EXT_SOURCE_3={EXT_SOURCE_3}&DAYS_EMPLOYED={DAYS_EMPLOYED}&FLOORSMAX_AVG={FLOORSMAX_AVG}&DAYS_BIRTH={DAYS_BIRTH}&REGION_RATING_CLIENT_W_CITY={REGION_RATING_CLIENT_W_CITY}'


st.write('')
st.write('')


#if st.button('Predicted target'):
 #   response = requests.get(url, params=params)
  #  prediction = response.json()
  #  col1, col2 = st.columns(2)
   # col2.metric("", f"{prediction['Prediction']}")
