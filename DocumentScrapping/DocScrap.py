import enum
import os
import pandas as pd

class SUPPORTED_TYPES(enum.Enum):
    CSV = ".csv"
    XLSX = ".xlsx"
    XLS = ".xls"
    XLSM = ".xlsm"
    XLSB = ".xlsb"
    

class DocScrap:
    EXCEL_SET = [SUPPORTED_TYPES.XLSX, SUPPORTED_TYPES.XLS, SUPPORTED_TYPES.XLSB, SUPPORTED_TYPES.XLSM]
    default_file_type = SUPPORTED_TYPES.CSV
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename, self.file_type = os.path.splitext(file_path)
    
    def get_file_path(self):
        return self.file_path

    def get_file_type(self):
        return self.file_type

    def get_filename(self):
        return self.filename


    def isPresentExcel(self, value):
        EXCEL = self.EXCEL_SET
        for excel_iter in EXCEL:
            if value == excel_iter.value:
                return True
            else:
                return False
    
    def read(self):
        file_path = self.get_file_path()
        if self.isPresentExcel(self.get_file_type()):
            return pd.read_excel(file_path)
        else:
            return pd.read_csv(file_path)

