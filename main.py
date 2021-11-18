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

    '''                     SEZIONE GEN         '''
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
    '''                     SEZIONE BIB         '''
    #livello cioè tipo di pubblicazione
    #a=analitico; c=raccolta; m=monografia; s=pubblicazione in serie
    L3A = Label(root, text="Livello ovvero tipo di pubblicazione (premi invio nella casella di testo per inserire i dati) ").grid(
        column=1, row=9, sticky=W)
    level = StringVar(root)
    level.set("m=monografia")  # default value
    O1 = OptionMenu(root, level, "a=analitico", "c=raccolta", "m=monografia", "s=pubblicazione in serie")
    O1.grid(column=1, row=10, sticky=W)
    #identificatore univoco
    L3B = Label(root, text="Identificatore univoco (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=11, sticky=W)
    E3 = Entry(root, bd=5)
    E3.grid(column=1, row=12, sticky=W)
    #titolo
    L4 = Label(root, text="Titolo dell'opera (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=13, sticky=W)
    E4 = Entry(root, bd=5)
    E4.grid(column=1, row=14, sticky=W)
    #creatore o autore dell'opera
    L5 = Label(root, text="Autore dell'opera (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=15, sticky=W)
    E5 = Entry(root, bd=5)
    E5.grid(column=1, row=16, sticky=W)
    #editore
    L6 = Label(root, text="Editore dell'opera (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=17, sticky=W)
    E6 = Entry(root, bd=5)
    E6.grid(column=1, row=18, sticky=W)
    #anno di pubblicazione
    L7 = Label(root, text="Data di pubblicazione nel formato YYYY-MM-DD (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=19, sticky=W)
    E7 = Entry(root, bd=5)
    E7.grid(column=1, row=20, sticky=W)
    # descrizione
    L8 = Label(root, text="Descrizione (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=21, sticky=W)
    E8 = Entry(root, bd=5)
    E8.grid(column=1, row=22, sticky=W)
    # luogo di pubblicazione
    L9 = Label(root, text="Luogo di pubblicazione (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=23, sticky=W)
    E9 = Entry(root, bd=5)
    E9.grid(column=1, row=24, sticky=W)


    def carica_dati():
        print('sono dentro la funzione carica_dati')
        input_utente_gen = {"stprog": E1.get(), "agency": E2.get(), "access_rights": var.get(), "completeness": option.get()}
        #controllo che i dati obbligatori per la sezione gen siano stati inseriti correttamente
        if input_utente_gen["stprog"] is None:
            raise Exception('Stprog è vuoto o non è stato inserito correttamente.')
        if input_utente_gen["agency"] is None:
            raise Exception('agency è vuoto o non è stato inserito correttamente.')
        #salvo tutti gli input come stringhe per poterli mettere nell'xml
        for input in input_utente_gen:
            if input_utente_gen[input] is not None:
                input_utente_gen[input] = str(input_utente_gen[input])

        input_utente_bib = {"level": level.get(), "identifier": E3.get(),"title":E4.get(),"creator": E5.get(), \
                            "publisher": E6.get(), "date": E7.get(),"description":E8.get(), "coverage":E9.get() }
        if input_utente_bib["identifier"] is None:
            raise Exception("l'identificatore univoco è vuoto o non è stato inserito correttamente.")
        for input in input_utente_bib:
            if input_utente_bib[input] is not None:
                input_utente_bib[input] = str(input_utente_bib[input])
        return {"gen": input_utente_gen,"bib":input_utente_bib}

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
        input_gen = carica_dati()["gen"]
        stprog = etree.SubElement(gen, "stprog")
        stprog.text = input_gen["stprog"]
        agency = etree.SubElement(gen, "agency")
        agency.text = input_gen["agency"]
        access_rights = etree.SubElement(gen, "access_rights")
        access_rights.text = input_gen["access_rights"]
        completeness = etree.SubElement(gen, "completeness")
        completeness.text = input_gen["completeness"]
        # leggi gli input utente per BIB
        input_bib = carica_dati()["bib"]
        bib = etree.Element("bib")
        if input_bib["level"].startswith("m"):
            level = 'm'
        elif input_bib["level"].startswith("a"): #s
            level = 'a'
        elif input_bib["level"].startswith("c"):
            level = 'c'
        elif input_bib["level"].startswith("s"):
            level = 's'
        bib.set("level", level)
        root.append(bib)
        #crea i sottoelementi di bib usando il namespace Dublin Core come tag
        identifier = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'identifier'))
        identifier.text = input_bib["identifier"]
        title = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'title'))
        title.text = input_bib["title"]
        creator = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'creator'))
        creator.text = input_bib["creator"]
        publisher = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'publisher'))
        publisher.text = input_bib["publisher"]
        date = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'date'))
        date.text = input_bib["date"]
        coverage = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'coverage'))
        coverage.text = input_bib["coverage"]

        #stampa del file con aggiunta della dichiarazione xml
        print(etree.tostring(root, pretty_print=True, encoding="utf8", xml_declaration=True))
        exit()

    B1 = ttk.Button(root, text="Carica Foto", command=carica_foto).grid(column=1, row=26, sticky=W)
    #B2 = ttk.Button(root, text="Carica Dati", command= carica_dati).grid(column=1, row=13, sticky=W)
    B3 = ttk.Button(root, text="Genera XML", command=genera_xml).grid(column=1, row=28, sticky=W)

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
