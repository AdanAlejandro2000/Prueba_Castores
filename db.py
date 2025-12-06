import pyodbc

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-9MNKC98;"
        "DATABASE=prueba_Castores;"
        "UID=sa;"
        "PWD=adan1234;"
    )
