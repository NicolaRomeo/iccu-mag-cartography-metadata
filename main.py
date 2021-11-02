import csv
import json
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from lxml import etree
def generate_xml():
    DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
    NISO_NAMESPACE = "http://www.niso.org/pdfs/DataDict.pdf"
    XLINK_NS = "http://www.w3.org/TR/xlink"
    XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
    DEF_NS =  "http://www.iccu.sbn.it/metaAG1.pdf"

    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

    NSMAP = {'dc': DC_NAMESPACE, "niso": NISO_NAMESPACE, "xlink": XLINK_NS, "xsi": XSI_NS, None: DEF_NS}  # the default namespace (no prefix)

    root = etree.Element("metadigit", {attr_qname:"http://www.iccu.sbn.it/metaAG1.pdf metadigit.xsd", "version": "2.0.1"}, nsmap=NSMAP)  # lxml only!

    print(etree.tostring(root, pretty_print=True))

def run_app():
    def calculate(*args):
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
        print(filename)
        if filename.split('.')[-1] != 'zip':
            messagebox.showerror("Errore di caricamento", "Il file non è uno zip. Le immagini devono essere compresse in uno zip. Riprova.")
            #raise Exception("Il file non è uno zip. Le immagini devono compresse in uno zip. Riprova.")
        generate_xml()


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
