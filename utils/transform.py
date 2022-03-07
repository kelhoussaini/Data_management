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
class Transform():
    
    def __init__(self, 
                     dataframe = pd.DataFrame, 
                     xlsFilepath = 'Facilis___IA_BTP.xlsx'): # xlsFilepath where we insert data after transformations
        self.xlsFilepath = xlsFilepath    
        self.dataframe = dataframe

    def read_pdf(self, file): # pdf file to upload
        pdfReader = PdfFileReader(file)
        count = pdfReader.numPages
        all_page_text = ""
        for i in range(count):
            page = pdfReader.getPage(i)
            all_page_text += page.extractText()

            all_page_text = all_page_text.replace('\n \n \n','')
            # insert commas to separate variables and then remove excess strings
            all_page_text = all_page_text.replace('\n \n',', ').replace('\n','')

            #remove excess strings
            all_page_text = all_page_text.strip()


        return all_page_text
    
    
    def get_writer(self): # dataframe
        
        writer_save = pd.ExcelWriter(os.getcwd()+self.xlsFilepath, engine='xlsxwriter')
        # Convert the dataframe to an XlsxWriter Excel object.
        self.dataframe.to_excel(writer_save, sheet_name='Summary__IA_BTP',
                                encoding='utf-8',index=False)
    
        writer_save.save()
        
        towrite = io.BytesIO()
        
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer_load:
            self.dataframe.to_excel(writer_load, sheet_name='Summary__IA_BTP',
                                index=False)
                   
        #towrite.seek(0)  # reset pointer
        #b64 = base64.b64encode(towrite.read()).decode()  # some strings

       # linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{self.xlsFilepath}">Download excel file</a>'
        #st.markdown(linko, unsafe_allow_html=True)
           
        #workbook  = writer.book
        #worksheet = writer.sheets['Summary__IA_BTP']
                  
        #writer_load.save() # Close the Pandas Excel writer and output the Excel file.
        
        #towrite.seek(0)
        return (writer_save, towrite)
          
    
