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
class Utils():
    
    
    def __init__(self, dataframe, xlsFilepath):
        
        self.transf = Transform(dataframe, xlsFilepath)
        self.forma = Formats()
        print(self.transf)


     
    def highlight_maxi(self, s):
        is_max = s == s.max()
        return ['background: lightgreen' if cell else '' for cell in is_max]
  
        
    def steps(self, apply = True, link=True):
        
        if link:
            a = self.transf.get_writer()[1]
            a.seek(0)  # reset pointer
            b64 = base64.b64encode(a.read()).decode()  # some strings

            linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{self.transf.xlsFilepath}">Download excel file</a>'
            st.markdown(linko, unsafe_allow_html=True)       
        else:
            existing_file = self.transf.get_writer()[0]
                                                   
        # read existing file
        reader = pd.read_excel(existing_file)
        #print("reader   ", reader)
        # write out the new sheet
        df = pd.DataFrame(reader)


        book = load_workbook(existing_file)
        print("book   ", book)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer_new = pd.ExcelWriter(existing_file, engine='openpyxl')

        writer_new.book = book
        workbook = writer_new.book

        writer_new.sheets = dict((ws.title, ws) for ws in book.worksheets)
        worksheet = writer_new.sheets

        # write out the new sheet
        df.to_excel(writer_new, sheet_name='Summary__IA_BTP', 
                     startrow=len(df.index) )
       
        print("writer_new.book   ", writer_new.book)

        
       # We need the number of rows in order to place the totals
        number_rows = len(df.index)
        # Define our range for the color formatting
        color_range = "L2:L{}".format(number_rows+1)


        # Highlight the top 5 values in Green
        #worksheet.conditional_format(color_range, {'type': 'top',
                                              # 'value': '5',
                                             #  'format': format2})

        # Note: It isn't possible to format any cells that already have a format such
        # as the index or headers or any cells that contain dates or datetimes.

        # Set the column width and format.
        #worksheet.set_column(1, 1, 18, format1)
        
        

        self.forma.appply_formats_openpyxl(worksheet = worksheet, workbook = workbook)

        writer_new.save() # Close the Pandas Excel writer and output the Excel file.
        return writer_new
    
    
    def steps_grouped(self, apply = True, link=True):
        
        file_load = io.BytesIO()
        (file_save, file_load) = self.transf.get_writer()
        file_load.seek(0)  # reset pointer
        b64 = base64.b64encode(file_load.read()).decode()  # some strings

        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{self.transf.xlsFilepath}">Download excel file</a>'
        st.markdown(linko, unsafe_allow_html=True)       

        # read existing file
        reader_save = pd.read_excel(file_save)
        reader_load = pd.read_excel(file_load)
        #print("reader   ", reader)
        # write out the new sheet
        df_save = pd.DataFrame(reader_save)
        df_load = pd.DataFrame(reader_load)


        book_save = load_workbook(file_save)
        book_load = load_workbook(file_load)
        print("book   ", book_save)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer_new_save = pd.ExcelWriter(file_save, engine='openpyxl')
        writer_new_load = pd.ExcelWriter(file_load, engine='openpyxl')

        writer_new_save.book = book_save
        workbook_save = writer_new_save.book
        
        writer_new_load.book = book_load
        workbook_load = writer_new_load.book

        writer_new_save.sheets = dict((ws.title, ws) for ws in book_save.worksheets)
        worksheet_save = writer_new_save.sheets
        
        writer_new_load.sheets = dict((ws.title, ws) for ws in book_load.worksheets)
        worksheet_load = writer_new_load.sheets


        # write out the new sheet
        df_save.to_excel(writer_new_save, sheet_name='Sheet1', 
                     startrow=len(df_save.index) )
        
        df_load.to_excel(writer_new_load, sheet_name='Sheet1', 
                     startrow=len(df_load.index) )
       
        print("writer_new_save.book   ", writer_new_save.book)

        
       # We need the number of rows in order to place the totals
        number_rows = len(df_load.index)
        # Define our range for the color formatting
        color_range = "L2:L{}".format(number_rows+1)


        # Highlight the top 5 values in Green
        #worksheet.conditional_format(color_range, {'type': 'top',
                                              # 'value': '5',
                                             #  'format': format2})

        # Note: It isn't possible to format any cells that already have a format such
        # as the index or headers or any cells that contain dates or datetimes.

        # Set the column width and format.
        #worksheet.set_column(1, 1, 18, format1)
        

        
        print("worksheet_load   ", worksheet_load)

            
        self.forma.appply_formats_openpyxl(worksheet = worksheet_save)#, workbook = workbook_save)       
        self.forma.appply_formats_openpyxl(worksheet = worksheet_load)#, workbook = workbook_load)


        #writer_new_save.save() # Close the Pandas Excel writer and output the Excel file.
        #writer_new_load.save()
        
        writer_new_save.save() # Close the Pandas Excel writer and output the Excel file.
        writer_new_load.save()
        
        writer_new_save.close() # Close the Pandas Excel writer and output the Excel file.
        writer_new_load.close()
        
        return 1 #(writer_new_save, writer_new_load)
            
        