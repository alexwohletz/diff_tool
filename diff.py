# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 13:22:07 2019

@author: wohletza
"""
import pandas as pd
import numpy as np
import xlsxwriter

class Diff:

    def __init__(self,df_NEW,df_OLD,index_col,file_name,useful_cols = None):
        self.df_NEW = df_NEW
        self.df_OLD = df_OLD
        self.index_col = index_col
        self.file_name = file_name
        self.useful_cols = useful_cols
        
    @property
    def cols_to_keep(self):
        return self.useful_cols

    @cols_to_keep.setter
    def cols_to_keep(self,cols):
        self.useful_cols = cols

    def dataframe_diff(self, df_OLD=None,df_NEW=None,index_col=None,file_name=None,useful_cols = None):
        
        '''Function to find the differences between two dataframes and export the report into a multi-tabbed excel report.
        Inputs:
            df_OLD(dataframe): Dataframe to be compared with new.
            df_NEW(dataframe): Dataframe to be compared with old.
            index_col(str): Key to perform comparison against.
            file_name(str): Filename to save diff report under.
        Returns:
            None: Creates tabbed excel spreadsheet.
        '''
        #Check for call or use class attributes to keep function generalizable

        df_OLD = df_OLD if df_OLD is not None else self.df_OLD
        df_NEW = df_NEW if df_NEW is not None else self.df_NEW
        ind = index_col if index_col is not None else self.index_col 
        file_name = file_name if file_name is not None else self.file_name
        useful_cols = useful_cols if useful_cols is not None else self.useful_cols

        if useful_cols is not None and isinstance(useful_cols,list):
            try:
                df_OLD = df_OLD[useful_cols].copy()
                df_NEW = df_NEW[useful_cols].copy()
            except KeyError as err:
                print(err)

        #Index column needs to perform like a string to prevent sorting errors.
        df_OLD[ind] = df_OLD[ind].astype(str)
        df_NEW[ind] = df_NEW[ind].astype(str)

        # Set the index
        df_OLD = df_OLD.set_index(ind).fillna(0).sort_index()
        df_NEW = df_NEW.set_index(ind).fillna(0).sort_index()
        
        # Perform Diff
        dfDiff = df_NEW.copy()
        droppedRows = []
        newRows = []
        diffRows = []

        cols_OLD = df_OLD.columns
        cols_NEW = df_NEW.columns
        sharedCols = list(set(cols_OLD).intersection(cols_NEW))
        
        for row in dfDiff.index:
            if (row in df_OLD.index) and (row in df_NEW.index):
                for col in sharedCols:
                    value_OLD = df_OLD.loc[row,col]
                    value_NEW = df_NEW.loc[row,col]
                    if value_OLD==value_NEW: 
                        dfDiff.loc[row,col] = df_NEW.loc[row,col]
                    else:
                        dfDiff.loc[row,col] = ('{}→{}').format(value_OLD,value_NEW)
                        diffRows.append(row)
            else:
                newRows.append(row)

        for row in df_OLD.index:
            if row not in df_NEW.index:
                droppedRows.append(row)
                dfDiff = dfDiff.append(df_OLD.loc[row,:])

        dfDiff = dfDiff.sort_index().fillna('')
        print(dfDiff)
        print('\nNew Rows:     {}'.format(newRows))
        print('Dropped Rows: {}'.format(droppedRows))
        
        new_S = pd.Series(newRows)
        dropped_S = pd.Series(droppedRows)
        df_rows = pd.concat([new_S,dropped_S],keys = ['new','dropped'])
        

        # Save output and format
        fname = self.file_name + '.xlsx'
        writer = pd.ExcelWriter(fname, engine='xlsxwriter')

        dfDiff.to_excel(writer, sheet_name='DIFF', index=True)
        df_NEW.to_excel(writer, sheet_name='NEW', index=True)
        df_OLD.to_excel(writer, sheet_name='OLD', index=True)
        #Check if delta exists
        if df_rows.empty:
            pass
        else:
            df_rows.to_excel(writer,sheet_name='Row Delta',index = True)

        
        diffRows = list(set(diffRows+newRows+droppedRows))
        df_Changes = dfDiff.loc[diffRows,:]
        print('\nChanges:\n{}'.format(df_Changes))

        # get xlsxwriter objects
        workbook  = writer.book
        worksheet = writer.sheets['DIFF']
        worksheet.hide_gridlines(2)
        worksheet.set_default_row(15)

        # define formats
        date_fmt = workbook.add_format({'align': 'center', 'num_format': 'yyyy-mm-dd'})
        center_fmt = workbook.add_format({'align': 'center'})
        number_fmt = workbook.add_format({'align': 'center', 'num_format': '#,##0.00'})
        cur_fmt = workbook.add_format({'align': 'center', 'num_format': '$#,##0.00'})
        perc_fmt = workbook.add_format({'align': 'center', 'num_format': '0%'})
        grey_fmt = workbook.add_format({'font_color': '#E0E0E0'})
        highlight_fmt = workbook.add_format({'font_color': '#FF0000', 'bg_color':'#B1B3B3'})
        new_fmt = workbook.add_format({'font_color': '#32CD32','bold':True})

        # set format over range
        ## highlight changed cells
        worksheet.conditional_format('A1:ZZ1000', {'type': 'text',
                                                'criteria': 'containing',
                                                'value':'→',
                                                'format': highlight_fmt})

        # highlight new/changed rows
        for row in range(dfDiff.shape[0]):
            if row+1 in newRows:
                worksheet.set_row(row+1, 15, new_fmt)
            if row+1 in droppedRows:
                worksheet.set_row(row+1, 15, grey_fmt)

        # save
        writer.save()
        print('\nDone.\n')
