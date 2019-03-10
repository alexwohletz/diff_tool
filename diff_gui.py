import PySimpleGUI as sg
import pandas as pd
from pathlib import Path
from diff import Diff

class Reader:

    def __init__(self,file_path):
        self.file_path = file_path
        self.columns = ''
    
    def read_files(self):

        file_dict = {'.csv':pd.read_csv,'.xlsx': pd.read_excel,'.txt':pd.read_csv}
        
        p = Path(self.file_path)
        print(f"Reading from {p.suffix} file.")

        if p.is_file():
            try:
                df = file_dict[p.suffix](p)
                self.columns = list(df.columns)
                return df
            except KeyError as err:
                print("Invalid file type selected,",p.suffix)

            except IOError as err:
                print('File could not be read.',err)
        else:
            print("Not a file")


layout = [[sg.Text('File New:'), sg.InputText('',size=(10,1)),sg.FileBrowse(button_text='Browse',key = 'file_new')],
          [sg.Text('File Old:'), sg.InputText('',size=(10,1)),sg.FileBrowse(button_text='Browse',key = 'file_old')],
          [sg.Text('Shared Columns \n to Compare:',auto_size_text=True),sg.Listbox(values = ['columns'],key='ucols',size = (10,5), select_mode='multiple')],
          [sg.Text('Index:'), sg.InputCombo(values = ['columns'],key='index')], 
          [sg.Button('Update'),sg.Submit(), sg.Button('Exit')]]  

window = sg.Window('File Comparison Tool').Layout(layout)  

while True:                 # Event Loop  
  event, values = window.Read()  
  print(event, values)
  if event is None or event == 'Exit':  
      break  
  if event == 'Update':
      
      old = Reader(values['file_old']).read_files() 
      new = Reader(values['file_new']).read_files()
      shared = set(old.columns).intersection(new.columns)

      if shared is None:
          print("No shared columns, this may produce spurious results")
      else:
        window.FindElement('ucols').Update(values = shared)
        window.FindElement('index').Update(values = list(shared))

  if event == 'Submit':

    diff_rept =  Diff(new,old,values['index'],'diff_report',values['ucols'])

    try:
        diff_rept.dataframe_diff()
    except Exception as err:
        print("something went wrong", err)

window.Close()


    


        
        
