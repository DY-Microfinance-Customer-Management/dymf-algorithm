import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class CustomersPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        
        self.title_label = ctk.CTkLabel(self, text="Customer Registration", font=("Arial", 24))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        self.name_label = ctk.CTkLabel(self, text="Name:")
        self.name_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.name_entry = ctk.CTkEntry(self, width=200)
        self.name_entry.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="w")
        
        self.gender_label = ctk.CTkLabel(self, text="Gender:")
        self.gender_label.grid(row=1, column=2, padx=10, pady=(10, 0), sticky="w")
        self.gender_var = tk.StringVar(value="Male")
        self.gender_male_radio = ctk.CTkRadioButton(self, text="Male", variable=self.gender_var, value="Male")
        self.gender_female_radio = ctk.CTkRadioButton(self, text="Female", variable=self.gender_var, value="Female")
        self.gender_male_radio.grid(row=1, column=3, padx=5, pady=(10, 0), sticky="w")
        self.gender_female_radio.grid(row=1, column=4, padx=5, pady=(10, 0), sticky="w")
        
        self.loan_label = ctk.CTkLabel(self, text="Loan Type:")
        self.loan_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        loan_types = ["Personal Loan", "Home Loan", "Car Loan", "Education Loan"]
        self.loan_type_var = tk.StringVar(value=loan_types[0])
        self.loan_type_menu = ctk.CTkOptionMenu(self, variable=self.loan_type_var, values=loan_types)
        self.loan_type_menu.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="w")
        
        self.guarantee_label = ctk.CTkLabel(self, text="Guarantor Name:")
        self.guarantee_label.grid(row=2, column=2, padx=10, pady=(10, 0), sticky="w")
        self.guarantee_entry = ctk.CTkEntry(self, width=200)
        self.guarantee_entry.grid(row=2, column=3, padx=10, pady=(10, 0), sticky="w")
        
        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_form)
        self.submit_button.grid(row=3, column=0, columnspan=5, pady=20)
    
    def submit_form(self):
        name = self.name_entry.get()
        gender = self.gender_var.get()
        loan_type = self.loan_type_var.get()
        guarantor = self.guarantee_entry.get()
        
        if not name or not guarantor:
            messagebox.showerror("Error", "All fields are required!")
        else:
            messagebox.showinfo("Success", f"Customer {name} registered successfully!")
            self.name_entry.delete(0, tk.END)
            self.gender_var.set("Male")
            self.loan_type_var.set("Personal Loan")
            self.guarantee_entry.delete(0, tk.END)
