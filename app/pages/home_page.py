from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class HomePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        
        self.df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'Los Angeles', 'Chicago']
        })
        
        self.data_label = tk.Label(self, text=self.df.to_string(), font=('Arial', 12))
        self.data_label.pack(padx=20, pady=20)
        
        self.download_button = ctk.CTkButton(self, text='Download as Excel', command=self.download_excel)
        self.download_button.pack(padx=20, pady=20)
    
    def download_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel files', '*.xlsx'), ('All files', '*.*')])
        if file_path:
            self.df.to_excel(file_path, index=False)
            CTkMessagebox(title='Download Complete', icon='check', message='File has been saved successfully.')
