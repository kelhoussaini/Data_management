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

from views_navigationBar import utils

from views_navigationBar.utils.params import Utils
from views_navigationBar.utils.formats_excel import Formats
from views_navigationBar.utils.transform import Transform #  get worksheet

import os

# Data visualization
import plotly.graph_objects as go
import plotly.express as px



# Initialization
def Initialize_session_state(dict_session= {}):

    if 'dataframe' not in dict_session:
        dict_session["dataframe"] = pd.DataFrame()

    if 'back_dataframe' not in dict_session:
        dict_session["back_dataframe"] = pd.DataFrame()
        
    if 'filled_dataframe' not in dict_session:
        dict_session["filled_dataframe"] = pd.DataFrame()        
        
    if 'next_step' not in dict_session:
        dict_session["next_step"] = 0
        
    if 'Statistics' not in dict_session:
        dict_session["Statistics"] = False
        
    return dict_session
       
    
    
def Fill_session_state(dataframe):
    
    st.session_state["dataframe"] = dataframe
    st.session_state["filled_dataframe"] = dataframe
    st.session_state["back_dataframe"] = dataframe
    
    return st.session_state


def Initialize_uploaded_session_state(dict_session):
    if dict_session["filled_dataframe"].empty:

        if dict_session["back_dataframe"].empty:
            dataframe = dict_session["dataframe"]
        else:
            dataframe = dict_session["back_dataframe"]
    else:
        dataframe = dict_session["filled_dataframe"]
        
    return dataframe

                
                
        
def Fill_missing_values(dataframe):
    
    if st.session_state["back_dataframe"].empty:            
        dataframe = st.session_state["dataframe"]
    else:
        dataframe = st.session_state["back_dataframe"]

            
    genre = st.radio(
         "How many companies do you need to add ?",
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
            boolean_condition = dataframe["Fournisseurs IA-BTP"] == name
            column_name = "E-MAIL"
            new_value = email

            dataframe.loc[boolean_condition, column_name] = new_value

        except ValueError:
            print("Oops!  That was no valid number.  Try again...")
            break
        i = i+1            

    st.session_state["filled_dataframe"] = dataframe
    
    return st.session_state

    #st.session_state

    #st.dataframe(st.session_state["filled_dataframe"]) #concat)
    
    
    
    
def get_uploaded_files(Uploaded_Files, NAME_SHEET):
    
    df = pd.DataFrame()
        
    for uploaded_file in Uploaded_Files:
        bytes_data = uploaded_file.read()
        #st.write("filename:", uploaded_file.name)

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

        dataf = pd.read_excel(uploaded_file, sheet_name= NAME_SHEET, 
                           usecols= columns, dtype= dic,
                           skiprows=skip, header=0)

        df = df.append(dataf, ignore_index=True)
        
    return df
    
    

        
def Transform_columns(Uploaded_File, original_df):
    
    
    
    dataframe = pd.read_excel(Uploaded_File, sheet_name= "Frs", 
                           usecols= "I:J", 
                           header=0)

    # Merge two tables (sheet 'TOUT' && { sheet 'FRS' --> table 'coord_dt' } )
    concat = pd.merge(original_df, dataframe, how= 'left', on = ['Fournisseurs']) 

    concat.rename(columns={"Fournisseurs": "Fournisseurs IA-BTP", 
                          "n° facture":  "N° facture"}, 
                 inplace=True)

    # change the columns order 
    order = [0,7] + list(np.arange(1, 7)) # setting column's order
    concat = concat[[concat.columns[i] for i in order]]
    
    
    return concat
    
      
    
def sql_queries(dataframe, type_query = "sum"):
    
    if type_query == "sum": 
        # Sum amounts, maximal amount, and minimal amount by week number
        result = dataframe[(dataframe[ "n° sem"]>7) & (dataframe[ "n° sem"]<23)] .groupby( "n° sem" ).agg( 
        Montant_total = ('Montant','sum'),
        min_montant = ('Montant', 'min'), 
        max_montant = ('Montant', 'max'),
        nbre_factures = ('id', 'count')
        ).reset_index().rename(columns = {'n° sem':'Semaine',
                                         'nbre_factures' : 'Nbre factures'}, inplace = False) #id refers to bills

    if type_query == "counts":
        
        result = dataframe[(dataframe[ "n° sem"]>7) & (dataframe[ "n° sem"]<23)].groupby(
            ["id_fournisseurs", "Fournisseurs IA-BTP"] ).agg( 
        nbre_factures = ('id', 'count')).reset_index().rename(
            columns = {'nbre_factures' : 'Nbre factures'},
                               inplace = False).sort_values(by='Nbre factures', ascending=False) #id refers to bills

        
    return result
    
    
    
def graphics_sum(dataframe, list_cols):
    
    #The plot : pie
    figo = go.Figure(
        go.Pie(
         labels= dataframe["Semaine"].map(lambda x: 'Week {}'.format(x)),
         values = dataframe["Montant_total"],
        hoverinfo = "label+percent",
        textinfo = "value",
            hole = 0.4
    ))


    # bar chart
    color="Montant_total"

    fig = px.bar(        
            dataframe[list_cols],
            x = "Semaine",
            y = "Montant_total",
            title = "Bar Graph",
            color="Montant_total",
    )


    
    option = st.sidebar.radio(
                 'Which plot would you like to see ?',
                 ('Donut chart', 'Bar Graph'))

    if option == 'Donut chart':
        st.header("Donut chart, Sum amounts by week number")
        st.plotly_chart(figo)

    if option == 'Bar Graph':
        st.header("Sum amounts by week number")
        st.plotly_chart(fig)

    
    
    
    
    
def graphics_count(dataframe, list_cols):    
    
    #The plot
    figo = go.Figure(
        go.Pie(
        labels = dataframe["Fournisseurs IA-BTP"],
        values = dataframe["Nbre factures"],
        hoverinfo = "label+percent",
        textinfo = "value"
    ))

    #Axis to color
    color="Nbre factures"

    fig = px.bar(        
            dataframe[list_cols],
            x = "Fournisseurs IA-BTP",
            y = "Nbre factures",
            title = "Bar Graph",
            color="Nbre factures",
    )

    option = st.sidebar.radio(
         'Which plot would you like to see ?',
         ('Pie', 'Bar Graph'))

    if option == 'Pie':
        st.header("Pie, Count bills number by company")
        st.plotly_chart(figo)

    if option == 'Bar Graph':
        st.header("Count bills number by company")
        st.plotly_chart(fig)


def read_file(file, data):
    if file is not None and file.name[-3:] == 'pdf':

        base64_pdf = base64.b64encode(file.read()).decode('utf-8')
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf">' 

        #st.write(file.name[-3:])
        #st.write(file.type)

        raw_text = Transform().read_pdf(file)

        #split string
        liste = raw_text.split(", ")
        # Removig columns
        L = liste[2:]
        #st.write(L)

        # automate data task with for loop
        column_name = "E-MAIL"
        for i in range(0,len(L),2):
            boolean_condition = data["Fournisseurs IA-BTP"] == L[i] #val_fournisseur
            data.loc[boolean_condition, column_name] = L[i+1] # val_email 

        Fill_session_state(dataframe = data)

        checkbox_file = st.checkbox("Display file")
        if checkbox_file:
            st.markdown(pdf_display, unsafe_allow_html=True)

        st.session_state["next_step"] = 1

    elif file is None:
        st.markdown("####  ###")

    else:
        st.markdown("#### Please check the type of your uploaded file ###")

