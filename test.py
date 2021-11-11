import csv
import json
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from lxml import etree
from datetime import datetime




def carica_foto(*args):
    print('sono dentro la funzione carica_foto')
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    print(filename)
    if filename.split('.')[-1] != 'zip':
        messagebox.showerror("Errore di caricamento", "Il file non è uno zip. Le immagini devono essere compresse in uno zip. Riprova.")
        #raise Exception("Il file non è uno zip. Le immagini devono compresse in uno zip. Riprova.")

def run_app():

    #main application window
    root = Tk()
    root.title("ICCU Digitalisation Cartography - images to xml")
    #frame widget
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=5, row=5, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    #start event loop



    #input utente per Stprog: indicazione del progetto di digitalizzazione. Esempio: www.mioprogetto.it
    # oppure l'home page dell'istituzione responsabile oppure l'uri del progetto
    L1 = Label(root, text="Stprog (premi invio nella casella di testo per inserire i dati)").grid(column=1, row=1, sticky=W)
    E1 = Entry(root, bd=5)
    E1.grid(column=1, row=2, sticky=W)

    #input utente per agency = istituzione responsabile del processo.
    L2 = Label(root, text="Agency (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=3, sticky=W)
    E2 = Entry(root, bd=5)
    E2.grid(column=1, row=4, sticky=W)

    #input utente per diritti di accesso: (uso riservato all'interno dell'istituzione= 0, uso pubblico=1)
    L3 = Label(root, text="Diritti di accesso").grid(column=1, row=5, sticky=SW)
    var = IntVar()
    R1 = Radiobutton(root, text="0: Uso riservato all'interno dell'istituzione", variable=var, value=0)
    R2 = Radiobutton(root, text="1: Uso pubblico", variable=var, value=1)
    R1.grid(column=1, row=6, sticky=W)
    R2.grid(column=2, row=6, sticky=W)
    #input utente per Completezza della digitalizzazione: (0=completa, 1=incompleta)
    L4 = Label(root, text="Completezza della digitalizzazione").grid(column=1, row=7, sticky=W)
    option = IntVar()
    R1 = Radiobutton(root, text="0: digitalizzazione completa", variable=option, value=0)
    R2 = Radiobutton(root, text="1: digitalizzazione incompleta", variable=option, value=1)
    R1.grid(column=1, row=8, sticky=W)
    R2.grid(column=2, row=8, sticky=W)

    def carica_dati():
        print('sono dentro la funzione carica_dati')
        input_utente = {"stprog": E1.get(), "agency": E2.get(), "access_rights": var.get(), "completeness": option.get()}
        for input in input_utente:
            if input_utente[input] is not None:
                input_utente[input] = str(input_utente[input])
        return input_utente

    def genera_xml():
        DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
        NISO_NAMESPACE = "http://www.niso.org/pdfs/DataDict.pdf"
        XLINK_NS = "http://www.w3.org/TR/xlink"
        XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
        DEF_NS = "http://www.iccu.sbn.it/metaAG1.pdf"

        attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

        NSMAP = {'dc': DC_NAMESPACE, "niso": NISO_NAMESPACE, "xlink": XLINK_NS, "xsi": XSI_NS,
                 None: DEF_NS}  # the default namespace (no prefix)
        # creazione elemento root con tutti i namespace
        root = etree.Element("metadigit",
                             {attr_qname: "http://www.iccu.sbn.it/metaAG1.pdf metadigit.xsd", "version": "2.0.1"},
                             nsmap=NSMAP)  # lxml only!

        # creazione elemento GEN con input utente
        # creazione dell'elemento gen con la data di creazione e di ultimo aggiornamento
        # qui servirà una classe o una funzione che deve essere attivata al momento dell'inserimento degli input utente
        # perché questi tag contengono valori che non possono essere noti a priori.
        gen = etree.Element("gen")
        gen.set("creation", str(datetime.now()))
        root.append(gen)
        #leggi gli input utente per GEN
        input_gen = carica_dati()
        stprog = etree.SubElement(gen, "stprog")
        stprog.text = input_gen["stprog"]
        agency = etree.SubElement(gen, "agency")
        agency.text = input_gen["agency"]
        access_rights = etree.SubElement(gen, "access_rights")
        access_rights.text = input_gen["access_rights"]
        completeness = etree.SubElement(gen, "completeness")
        completeness.text = input_gen["completeness"]

        #stampa del file con aggiunta della dichiarazione xml
        print(etree.tostring(root, pretty_print=True, encoding="utf8", xml_declaration=True))

    B1 = ttk.Button(root, text="Carica Foto", command=carica_foto).grid(column=1, row=11, sticky=W)
    B2 = ttk.Button(root, text="Carica Dati", command= carica_dati).grid(column=1, row=13, sticky=W)
    B3 = ttk.Button(root, text="Genera XML", command=genera_xml).grid(column=1, row=15, sticky=W)

    #adding some polish
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    #root.bind("<Return>", carica_foto())

    root.mainloop()


# Driver Code

# Decide the two file paths according to your
# computer system


# Call the make_json function


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    run_app()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
