import tkinter as tk
from tkinter import ttk
"""
--- Arguments ---
ordo,++terra,+aer,-metallum|ratio /R|count
--- Meaning ---
Selected Aspects: Ordo, Terra
Soft Whitelist: Aer
Blacklist: Metallum
Sorts first by Reverse Ratio ()
Sorts second by count of selected aspects
"""


class App(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.tree = ttk.Treeview()
        self.tree.grid(column=0, row=1, columnspan=1, rowspan=1, sticky='NEWS')

if __name__ == "__main__":
    root = tk.Tk()
    screen = App(root)
    root.mainloop()