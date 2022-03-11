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

from utils.formats_excel import Formats
from utils.transform import Transform #  get worksheet
from openpyxl import load_workbook
import xlsxwriter
import openpyxl

import xlrd
import os

class Utils():
    
    
    def __init__(self, dataframe, xlsFilepath):
        
        self.transf = Transform(dataframe, xlsFilepath)
        self.forma = Formats(dataframe, xlsFilepath)
        print(self.transf)

    
    def highlight_maxi(self, s):
        is_max = s == s.max()
        return ['background: lightgreen' if cell else '' for cell in is_max]
    
    def steps_grouped(self, apply = True, link=True):
        
        #file_load = io.BytesIO()
        (file_save, file_load) = self.transf.get_writer()
        #file_load.seek(0)  # reset pointer
        
        # read existing file
        reader_save = pd.read_excel(file_save)
      
        # write out the new sheet
        df_save = pd.DataFrame(reader_save)
        book_save = load_workbook(file_save)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer_new_save = pd.ExcelWriter(file_save, engine='openpyxl')

        writer_new_save.book = book_save
        workbook_save = writer_new_save.book
        
        writer_new_save.sheets = dict((ws.title, ws) for ws in book_save.worksheets)
        worksheet_save = writer_new_save.sheets     

        # write out the new sheet
        df_save.to_excel(writer_new_save, sheet_name='Sheet1', 
                     startrow=len(df_save.index) )
        
         
       # We need the number of rows in order to place the totals
        number_rows = len(df_save.index)
        # Define our range for the color formatting
        color_range = "L2:L{}".format(number_rows+1)
            
        worksheet_save = self.forma.appply_formats_openpyxl(worksheet = worksheet_save)#, workbook = workbook_save)       
        
        workbook_save.save(self.transf.xlsFilepath) #(writer_new_save, writer_new_load)
        data = open(self.transf.xlsFilepath, 'rb').read()
        b64 = base64.b64encode(data).decode('UTF-8')
        
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{self.transf.xlsFilepath}">Download excel file</a>'
        st.markdown(linko, unsafe_allow_html=True)       
        
        #with open(os.path.join("tempDir", self.transf.xlsFilepath), "wb") as f:
                 # f.write(data)
               #   st.success("Saved File:{} to tempDir".format(self.transf.xlsFilepath))
                  
        
        workbook_save.close()
        
 
            
        
