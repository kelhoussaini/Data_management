# app2.py
import streamlit as st

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


import os

# Data visualization
import plotly.graph_objects as go
import plotly.express as px


from views_navigationBar import functions
#from views_navigationBar.streamlit_radio_options import functions


from views_navigationBar.utils.params import Utils
from views_navigationBar.utils.formats_excel import Formats
from views_navigationBar.utils.transform import Transform #  get worksheet



# this slider allows the user to select a number of lines
# to display in the dataframe

#streamlit run app.py

def app():
    
    # Initialization
    st.session_state = functions.Initialize_session_state()

    text_input = "Choose a source (Excel) file"
    uploaded_file = st.sidebar.file_uploader(text_input, accept_multiple_files=False)
    
    xlsFilepath = 'Facilis___IA_BTP.xlsx'
    # Add a selectbox to the sidebar:

    
    if uploaded_file is not None:    
        
        ALL_SHEETS = pd.read_excel(uploaded_file,  sheet_name = None)
        
        NAME_SHEET = st.sidebar.selectbox(
            'Name_sheet',
            list(ALL_SHEETS.keys())
            )#Unaccompanied      Group of people        

        
        if NAME_SHEET == 'Summary__IA_BTP' :
            columns = "A:H"

            dic = {'Fournisseurs IA-BTP' : str,
                              'E-MAIL' : str, 'N° facture':str, 'Montant':float,
                              'Date de facture' :str, "Date d'échéance": str, 
                              'n° sem': int, "Mis en paie.": str}
            skip = None


            df = pd.read_excel(uploaded_file, sheet_name= NAME_SHEET, 
                                   usecols= columns, dtype= dic,
                                   skiprows=skip, header=0) 
            st.sidebar.write('Data -- 5 Firsts rows')
            st.sidebar.dataframe(df.head())

            L = list(df['Fournisseurs IA-BTP'].unique())

            def map_index(liste=[], start_id=1, end_id=11): #end_id=len(liste)+1
                list2 = list(np.arange(start_id, end_id))

                dic = {}
                for i,j in enumerate(liste):
                    dic[j] = i+1
                return dic


            func = map_index(liste = L, start_id = 1, end_id=len(L)+1)
            df["id_fournisseurs"] = df["Fournisseurs IA-BTP"].map(func)

            # add id as the primary key.
            df['id'] = list(np.arange(1, len(df)+1))            
        
            Stat = st.sidebar.selectbox('',  
                                 ('Please select', 
                                  'Sum amounts by week number', 'Count bills number by company')) 

            #st.dataframe(concat)

            #Multiple rows are with the same company
            # We make a new column to represent companies by their id.
            #Using for loop,dictionary and map functions 




            if Stat == 'Sum amounts by week number':

                #st.subheader('Sum amounts by week number')

                res = functions.sql_queries(dataframe = df, type_query = "sum")
                list_cols = ['Semaine', 'Montant_total', 'Nbre factures']
                #st.dataframe(res[list_cols])

                checkbox_viz = True # st.checkbox("Visualization")
                if checkbox_viz:
                    functions.graphics_sum(dataframe = res, list_cols = list_cols)    

            if Stat == 'Count bills number by company':

                #st.subheader('Count bills number by company')

                counts = functions.sql_queries(dataframe = df, type_query = "counts")       
                list_cols = ['Fournisseurs IA-BTP','Nbre factures']
                #st.dataframe(counts[list_cols])

                checkbox_viz = True #st.checkbox("Visualization")
                if checkbox_viz:
                    functions.graphics_count(dataframe = counts, list_cols = list_cols)   
                    
        else:
            st.markdown(" Oops ! Make sure you uploaded the right file !")







    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
