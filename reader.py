import pandas as pd
from pathlib import Path

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
