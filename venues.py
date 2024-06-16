# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 15:59:05 2023

@author: Subramanya.Ganti
"""

import glob
import pandas as pd
from openpyxl import load_workbook

path = "C:/Users/Subramanya.Ganti/Downloads/cricket/summary"
input_file = 'C:/Users/Subramanya.Ganti/Downloads/cricket/venues.xlsx'
venues = pd.read_excel(input_file,'Sheet1')

def venue_aggregate(venue_list,venues,path):
    file_list = glob.glob(path + "/*summary.xlsx")
    for file in file_list:
        if(file[-17:] != "smat_summary.xlsx" or True):
            df_bat = pd.read_excel(file,'venue batting')
            comp_venues = df_bat['Venue'].tolist()
            #venue_list.append(comp_venues)
            venue_list = [*venue_list, *comp_venues]
    
    venue_list = list(dict.fromkeys(venue_list))
    for x in venue_list:
        existing = venues['venue'].tolist()
        if(x not in existing):
            venues.loc[len(venues.index)] = [x,'']
            
    return venues

def write_to_excel(venues,output_dump):
    try:
        book = load_workbook(output_dump)
        with pd.ExcelWriter(output_dump, engine = 'openpyxl',mode='a', if_sheet_exists = 'replace') as writer:
            writer.book = book
            writer.sheets = {ws.title:ws for ws in book.worksheets}
            venues.to_excel(writer, sheet_name='Sheet1',index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(output_dump) as writer:        
            venues.to_excel(writer, sheet_name='Sheet1',index=False)

venues = venue_aggregate([],venues,path)
write_to_excel(venues,input_file)
