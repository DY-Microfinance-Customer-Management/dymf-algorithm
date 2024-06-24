import customtkinter as ctk
import tkinter as tk

from pages import CustomersPage, HomePage, LoanPage, LoginPage, ReceivesPage, SettingsPage

root = ctk.CTk()
root.geometry('800x600')
root.title('CustomTkinter Sidebar Example')

sidebar = ctk.CTkFrame(root, width=150, corner_radius=0)
sidebar.grid(row=0, column=0, rowspan=4, sticky='nswe')

main_content = ctk.CTkFrame(root, corner_radius=0)
main_content.grid(row=0, column=1, sticky='nswe')

pages = {
    'Customers': CustomersPage(main_content),
    'Home': HomePage(main_content),
    'Loan': LoanPage(main_content),
    'Login': LoginPage(main_content),
    'Receives': ReceivesPage(main_content),
    'Settings': SettingsPage(main_content)
}

menu_buttons = []
menu_names = ['Home', 'Customers', 'Loan', 'Login', 'Receives', 'Settings']

def select_menu(name):
    for page in pages.values():
        page.grid_remove()
    pages[name].grid(row=0, column=0, sticky='nswe')

for i, name in enumerate(menu_names):
    button = ctk.CTkButton(sidebar, text=name, width=150, height=50, fg_color='transparent', command=lambda name=name: select_menu(name))
    button.grid(row=i, column=0, padx=0, pady=0, sticky='we')
    menu_buttons.append(button)

select_menu('Home')

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
sidebar.grid_rowconfigure(len(menu_names), weight=1)
main_content.grid_rowconfigure(0, weight=1)
main_content.grid_columnconfigure(0, weight=1)

root.mainloop()
