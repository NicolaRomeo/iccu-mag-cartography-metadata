import csv
import json
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

def run_app():
    def calculate(*args):
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
        print(filename)

    #main application window
    root = Tk()
    root.title("ICCU Digitalisation Cartography - images to xml")
    #frame widget
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    #entry widget (feet textbox)
    #other widgets

    ttk.Button(mainframe, text="Upload", command=calculate).grid(column=3, row=3, sticky=W)

    #adding some polish
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    root.bind("<Return>", calculate)

    #start event loop
    root.mainloop()


# Driver Code

# Decide the two file paths according to your
# computer system


# Call the make_json function

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    run_app()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
