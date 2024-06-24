import customtkinter as ctk

class ReceivesPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        label = ctk.CTkLabel(self, text='Welcome to Settings page', font=('Arial', 24))
        label.pack(padx=20, pady=20)
