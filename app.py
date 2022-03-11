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


# this slider allows the user to select a number of lines
# to display in the dataframe

#streamlit run app.py

'''
# IA -- BTP 
'''

xlsFilepath = 'Facilis___IA_BTP.xlsx'
# Add a selectbox to the sidebar:

NAME_SHEET = st.sidebar.selectbox(
    'NAME_SHEET',
    ('TOUT', 'Frs', 'Stat', 'Virement'))#Unaccompanied      Group of people        

uploaded_files = st.file_uploader("Choose a source file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)
        
    if NAME_SHEET == "TOUT":
        columns = "A:G"
        dic = {'n° facture':str, 'Montant':float,
               'n° sem': int, 'Date de facture' :str,
              "Date d'échéance": str, "Mis en paie.": str}
        skip = None
        
    elif NAME_SHEET == "Frs":
        columns = "I:J"
    elif NAME_SHEET == "Virement":
        columns = "A:R"
    elif NAME_SHEET == "Stat":
        columns = "C:E"
        dic = {'Montant':float, 'Nbre factures':str, 'Semaine':str}
        skip=[0,1,2,3]
        
    df = pd.read_excel(uploaded_file, sheet_name= NAME_SHEET, 
                       usecols= columns, dtype= dic,
                       skiprows=skip, header=0)
    st.dataframe(df)

checkbox_val = st.checkbox("Transform")
if checkbox_val:
    
    dataframe = pd.read_excel(uploaded_file, sheet_name= "Frs", 
                           usecols= "I:J", 
                           header=0)

    # Merge two tables (sheet 'TOUT' && { sheet 'FRS' --> table 'coord_dt' } )
    concat = pd.merge(df, dataframe, how= 'left', on = ['Fournisseurs']) 

    concat.rename(columns={"Fournisseurs": "Fournisseurs IA-BTP", 
                          "n° facture":  "N° facture"}, 
                 inplace=True)

    # change the columns order 
    order = [0,7] + list(np.arange(1, 7)) # setting column's order
    concat = concat[[concat.columns[i] for i in order]]

    st.dataframe(concat)
    
    next_step = st.selectbox('next_step',   ('Please select', 'Upload file', 'Fill missing values')) 
    if next_step == 'Fill missing values':       
        genre = st.radio(
             "Combien de fournisseurs vous voudriez saisir ?",
             ('1', '2', '3'))

        i = 0
        while i < int(genre):
            try:
            
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input(f'Nom du Fournisseur {i+1}', '')
                with col2:
                    email = st.text_input(f'Email du Fournisseur {i+1}', '')

                # Replace the missing value by the new one
                boolean_condition = concat["Fournisseurs IA-BTP"] == name
                column_name = "E-MAIL"
                new_value = email

                concat.loc[boolean_condition, column_name] = new_value
             
            except ValueError:
                print("Oops!  That was no valid number.  Try again...")
                break
            i = i+1            
        st.dataframe(concat)    
        #concat_n = concat.copy()
        
    elif next_step == "Upload file":
        pdf_file = st.file_uploader("Please Choose a file",  type = "pdf", accept_multiple_files=False) 
        
        if pdf_file is not None and pdf_file.name[-3:] == 'pdf':
            
            base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf">' 
                    
            #st.write(pdf_file.name[-3:])
            #st.write(pdf_file.type)

            raw_text = Transform().read_pdf(pdf_file)
            
            #split string
            liste = raw_text.split(", ")
            # Removig columns
            L = liste[2:]

            # automate data task with for loop
            column_name = "E-MAIL"
            for i in range(0,len(L),2):
                boolean_condition = concat["Fournisseurs IA-BTP"] == L[i] #val_fournisseur
                concat.loc[boolean_condition, column_name] = L[i+1] # val_email 

            checkbox_file = st.checkbox("Display file")
            if checkbox_file:
                st.markdown(pdf_display, unsafe_allow_html=True)

            checkbox_dataframe = st.checkbox("Display data")
            
            def highlight_max(s):
                is_max = s == s.max()
                return ['background: lightgreen' if cell else '' for cell in is_max]


            if checkbox_dataframe:          
                # Highlighting the maximum values of
                # last 2 columns
                concat.style.apply(highlight_max)
                st.dataframe(concat)
                
            checkbox_export_file = st.checkbox("Export data to Excel file")
            if checkbox_export_file:
               
                Utils(dataframe = concat, xlsFilepath=xlsFilepath).steps_grouped(apply = True, link=True)
                
                
        
                checkbox_stat = st.checkbox("Statistiques")
                if checkbox_stat:
                    Stat = st.selectbox('Stat',  
                                             ('Please select', 
                                              'Sum amounts by week number', 'Count bills number by provider')) 
                    # add id as the primary key.
                    concat['id'] = list(np.arange(1, len(concat)+1))
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

                    L = list(concat['Fournisseurs IA-BTP'].unique())

                    res = map_index(liste = L, start_id = 1, end_id=len(L)+1)
                    concat["id_fournisseurs"] = concat["Fournisseurs IA-BTP"].map(res)

                    if Stat == 'Sum amounts by week number':

                        # Sum amounts, maximal amount, and minimal amount by week number
                        res = concat[(concat[ "n° sem"]>9) & (concat[ "n° sem"]<25)] .groupby( "n° sem" ).agg( 
                        Montant_total = ('Montant','sum'),
                        min_montant = ('Montant', 'min'), 
                        max_montant = ('Montant', 'max'),
                        nbre_factures = ('id', 'count')
                        ).reset_index().rename(columns = {'n° sem':'Semaine',
                                                         'nbre_factures' : 'Nbre factures'}, inplace = False) #id refers to bills

                        list_cols = ['Semaine', 'Montant_total', 'Nbre factures']
                        st.dataframe(res[list_cols])

                        checkbox_viz = st.checkbox("Visualization")
                        if checkbox_viz:
                            
                            #The plot
                            figo = go.Figure(
                                go.Pie(
                                 labels= res["Semaine"].map(lambda x: 'Week {}'.format(x)),
                                 values = res["Montant_total"],
                                hoverinfo = "label+percent",
                                textinfo = "value",
                                    hole = 0.4
                            ))

                            st.header("Donut chart, Sum amounts by week number")
                            st.plotly_chart(figo)
                            
                            
                            #Axis to color
                            color="Montant_total"

                            fig = px.bar(        
                                    res[list_cols],
                                    x = "Semaine",
                                    y = "Montant_total",
                                    title = "Bar Graph",
                                    color="Montant_total",
                            )
                            st.header("Sum amounts by week number")
                            st.plotly_chart(fig)


                    if Stat == 'Count bills number by provider':
                        counts = concat[(concat[ "n° sem"]>7) & (concat[ "n° sem"]<25)].groupby(
                            ["id_fournisseurs", "Fournisseurs IA-BTP"] ).agg( 
                        nbre_factures = ('id', 'count')).reset_index().rename(
                            columns = {'nbre_factures' : 'Nbre factures'},
                                               inplace = False).sort_values(by='Nbre factures', ascending=False) #id refers to bills

                        list_cols = ['Fournisseurs IA-BTP','Nbre factures']
                        st.dataframe(counts[list_cols])

                        checkbox_viz = st.checkbox("Visualization")
                        if checkbox_viz:

                            #The plot
                            figo = go.Figure(
                                go.Pie(
                                labels = counts["Fournisseurs IA-BTP"],
                                values = counts["Nbre factures"],
                                hoverinfo = "label+percent",
                                textinfo = "value"
                            ))

                            st.header("Pie chart, Count bills number by provider")
                            st.plotly_chart(figo)

                            #Axis to color
                            color="Nbre factures"

                            fig = px.bar(        
                                    counts[list_cols],
                                    x = "Fournisseurs IA-BTP",
                                    y = "Nbre factures",
                                    title = "Bar Graph",
                                    color="Nbre factures",
                            )
                            st.header("Count bills number by provider")
                            st.plotly_chart(fig)
                                            
        elif pdf_file is None:
            st.markdown("####  ###")
            
        else:
            st.markdown("#### Please check the type of your uploaded file ###")
            
            
            
    
                
     


        
    
    



    
    #st.button('Fill missing values')

    


#url = 'http://127.0.0.1:8000/make_preds'
params = dict(
   NAME_SHEET=NAME_SHEET)

# enter here the address of your initial api deployed to heroku , flask api
#url = f'http://0.0.0.0:8000/make_preds?CODE_GENDER={CODE_GENDER}&FLAG_OWN_CAR={FLAG_OWN_CAR}&OCCUPATION_TYPE={OCCUPATION_TYPE}&NAME_INCOME_TYPE={NAME_INCOME_TYPE}&NAME_TYPE_SUITE={NAME_TYPE_SUITE}&EXT_SOURCE_3={EXT_SOURCE_3}&DAYS_EMPLOYED={DAYS_EMPLOYED}&FLOORSMAX_AVG={FLOORSMAX_AVG}&DAYS_BIRTH={DAYS_BIRTH}&REGION_RATING_CLIENT_W_CITY={REGION_RATING_CLIENT_W_CITY}'


st.write('')
st.write('')


#if st.button('Predicted target'):
 #   response = requests.get(url, params=params)
  #  prediction = response.json()
  #  col1, col2 = st.columns(2)
   # col2.metric("", f"{prediction['Prediction']}")
