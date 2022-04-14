import json
import os
import webbrowser
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from lxml import etree
from datetime import datetime
import shutil
from handle_upload import carica_foto

'''
Should also try Pillow instead of PIL
'''

def run_app():
    # main application window
    root = Tk()
    root.title("ICCU Digitalisation Cartography - images to xml")
    # frame widget
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.pack(fill=BOTH, expand=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # start event loop
    my_canvas = Canvas(mainframe)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
    my_scrollbar = ttk.Scrollbar(mainframe, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    # create another frame inside the canvas
    second_frame = Frame(my_canvas)
    my_canvas.create_window((0, 0), window=second_frame, anchor='nw')

    '''                     SEZIONE GEN         '''
    # input utente per Stprog: indicazione del progetto di digitalizzazione. Esempio: www.mioprogetto.it
    # oppure l'home page dell'istituzione responsabile oppure l'uri del progetto
    L1_tooltip = "Descrizione oppure Home page dell'istituzione responsabile. Obbligatorio.\n "
    L1 = Label(second_frame, text="Stprog -" + L1_tooltip).grid(column=1, row=1, sticky=W)
    L1B = Label(second_frame, text="Es. www.mioprogetto.it").grid(column=2, row=2, sticky=W)
    E1 = Entry(second_frame, bd=5)
    E1.grid(column=1, row=2, sticky=W)

    # input utente per agency = istituzione responsabile del processo.
    L2_tooltip = "Istituzione responsabile del processo. Obbligatorio."
    L2 = Label(second_frame, text="Agency - " + L2_tooltip).grid(column=1, row=3, sticky=W)
    L2B = Label(second_frame, text="Es. 'Comune di La Spezia' oppure 'IT:Regione Liguria ").grid(column=2, row=4,
                                                                                                 sticky=W)
    E2 = Entry(second_frame, bd=5)
    E2.grid(column=1, row=4, sticky=W)

    # input utente per diritti di accesso: (uso riservato all'interno dell'istituzione= 0, uso pubblico=1)
    L3 = Label(second_frame, text="Diritti di accesso").grid(column=1, row=5, sticky=SW)
    var = IntVar()
    R1 = Radiobutton(second_frame, text="0: Uso riservato all'interno dell'istituzione", variable=var, value=0)
    R2 = Radiobutton(second_frame, text="1: Uso pubblico", variable=var, value=1)
    R1.grid(column=1, row=6, sticky=W)
    R2.grid(column=1, row=8, sticky=W)
    # input utente per Completezza della digitalizzazione: (0=completa, 1=incompleta)
    L4 = Label(second_frame, text="Completezza della digitalizzazione").grid(column=1, row=9, sticky=W)
    option = IntVar()
    R1 = Radiobutton(second_frame, text="0: digitalizzazione completa", variable=option, value=0)
    R2 = Radiobutton(second_frame, text="1: digitalizzazione incompleta", variable=option, value=1)
    R1.grid(column=1, row=10, sticky=W)
    R2.grid(column=1, row=12, sticky=W)

    '''                     SEZIONE BIB         '''
    # livello cioè tipo di pubblicazione
    # a=analitico; c=raccolta; m=monografia; s=pubblicazione in serie
    L3A = Label(second_frame, text="Livello ovvero tipo di pubblicazione").grid(
        column=1, row=13, sticky=W)
    level = StringVar(second_frame)
    level.set("m=monografia")  # default value
    O1 = OptionMenu(second_frame, level, "a=analitico", "c=raccolta", "m=monografia", "s=pubblicazione in serie",
                    "f=unità archivistica", "d=unità documentaria")
    O1.grid(column=1, row=14, sticky=W)
    # identificatore univoco
    L3B = Label(second_frame, text="Identificatore univoco - identificatore SBN o simile. Obbligatorio. ").grid(
        column=1, row=15, sticky=W)
    E3 = Entry(second_frame, bd=5)
    E3.grid(column=1, row=16, sticky=W)
    # titolo
    L4 = Label(second_frame, text="Titolo dell'opera ").grid(column=1, row=17, sticky=W)
    E4 = Entry(second_frame, bd=5)
    E4.grid(column=1, row=18, sticky=W)
    # creatore o autore dell'opera
    L5 = Label(second_frame, text="Autore dell'opera ").grid(column=1, row=19, sticky=W)
    E5 = Entry(second_frame, bd=5)
    E5.grid(column=1, row=20, sticky=W)
    # editore
    L6 = Label(second_frame, text="Editore dell'opera ").grid(column=1, row=21, sticky=W)
    E6 = Entry(second_frame, bd=5)
    E6.grid(column=1, row=22, sticky=W)
    # anno di pubblicazione
    L7 = Label(second_frame, text="Data di pubblicazione nel formato YYYY-MM-DD").grid(column=1, row=23, sticky=W)
    E7 = Entry(second_frame, bd=5)
    E7.grid(column=1, row=24, sticky=W)
    # descrizione
    L8 = Label(second_frame, text="Descrizione generica dell'opera").grid(column=1, row=25, sticky=W)
    E8 = Entry(second_frame, bd=5)
    E8.grid(column=1, row=26, sticky=W)
    # luogo di pubblicazione
    L9 = Label(second_frame, text="Luogo di pubblicazione").grid(column=1, row=27, sticky=W)
    E9 = Entry(second_frame, bd=5)
    E9.grid(column=1, row=28, sticky=W)
    L10 = Label(second_frame, text="Linguaggio dell'opera").grid(
        column=1, row=29, sticky=W)
    E10 = Entry(second_frame, bd=5)
    E10.grid(column=1, row=30, sticky=W)

    def carica_dati():
        input_utente_gen = {"stprog": E1.get(), "agency": E2.get(), "access_rights": var.get(),
                            "completeness": option.get(),
                            }
        # controllo che i dati obbligatori per la sezione gen siano stati inseriti correttamente
        TITLE = "ERRORE UTENTE NELL'INSERIMENTO DATI"
        ERROR_MESSAGE = " è vuoto o non è stato inserito correttamente. \" " \
                        "Ricorda di premere Invio dopo aver inserito il valore nella casella di testo"
        if input_utente_gen["stprog"] is None:
            messagebox.showerror(title=TITLE, message='Stprog' + ERROR_MESSAGE)
        if input_utente_gen["agency"] is None:
            messagebox.showerror(title=TITLE, message='Agency' + ERROR_MESSAGE)

        # salvo tutti gli input come stringhe per poterli mettere nell'xml
        for input in input_utente_gen:
            if input_utente_gen[input] is not None:
                input_utente_gen[input] = str(input_utente_gen[input])

        input_utente_bib = {"level": level.get(), "identifier": E3.get(), "title": E4.get(), "creator": E5.get(), \
                            "publisher": E6.get(), "date": E7.get(), "description": E8.get(), "coverage": E9.get(),
                            "language": E10.get()}
        if input_utente_bib["identifier"] is None:
            messagebox.showerror(title=TITLE, message='Identificatore Univoco ' + ERROR_MESSAGE)
        for input in input_utente_bib:
            if input_utente_bib[input] is not None:
                input_utente_bib[input] = str(input_utente_bib[input])
        return {"gen": input_utente_gen, "bib": input_utente_bib}

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
        # leggi gli input utente per GEN
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
        elif input_bib["level"].startswith("a"):  # s
            level = 'a'
        elif input_bib["level"].startswith("c"):
            level = 'c'
        elif input_bib["level"].startswith("s"):
            level = 's'
        elif input_bib["level"].startswith("d"):
            level = 'd'
        elif input_bib["level"].startswith("f"):
            level = 'f'
        bib.set("level", level)
        root.append(bib)
        # crea i sottoelementi di bib usando il namespace Dublin Core come tag
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
        language = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'language'))
        language.text = input_bib["language"]

        # Read images metadata from the json file that was created when the user uploaded the images
        # check that the files exists, throw an error if it doesn't.
        base_path = Path.home() / 'AppData' / 'Local' / 'Temp' / 'temporary_iccu_folder'
        source_metadata_file = base_path / "data.json"
        if not source_metadata_file:
            messagebox.showerror("Errore: ",
                                 "Il file {0} non esiste. Questo significa che le immagini non sono ancora state caricate"
                                 "Per favore cliccare su 'Carica Foto' e riprovare.".format(
                                     source_metadata_file))
            exit()

        # open json file
        f = open(source_metadata_file)
        data = json.load(f)

        print("printing all data read from the json file containing the metadata from the images \n")
        print(data)

        for image_dict in data:
            for i in image_dict:
                meta_info = image_dict.get(i)
                # create an <img> tag for each image
                img = etree.Element("img")
                # create <img> subelements for each image
                sequence_number = etree.SubElement(img, 'sequence_number')
                sequence_number.text = str(meta_info.get('sequence_number'))
                nomenclature = etree.SubElement(img, 'nomenclature')
                nomenclature.text = str(meta_info.get('nomenclature'))
                # per file dobbiamo creare un attributo xlink
                attribute_name = etree.QName(XLINK_NS, "href")
                print("File_Filename: {}".format(meta_info.get('File:FileName')))
                print("attribute name: {}".format(attribute_name))
                print("nsmap: {}".format(NSMAP))
                file = etree.SubElement(img, 'file',
                                        {attribute_name: meta_info.get('File:FileName'), 'Location': 'URL'},
                                        nsmap=NSMAP)
                md5 = etree.SubElement(img, 'md5')
                md5.text = str(meta_info.get('md5'))
                md5 = etree.SubElement(img, 'filesize')
                filesize = str(meta_info.get('File:FileSize'))
                # for image dimensions we need to create the subelements with niso namespace
                image_length = etree.QName(NISO_NAMESPACE, "image_length")
                image_width = etree.QName(NISO_NAMESPACE, "image_width")
                image_dimensions_x = str(meta_info.get('size')[0])
                image_dimensions_y = str(meta_info.get('size')[1])
                image_dimension = etree.SubElement(img, 'image_dimensions')
                image_length = etree.SubElement(image_dimension, image_length, nsmap=NSMAP)
                image_width = etree.SubElement(image_dimension, image_width, nsmap=NSMAP)
                image_length.text = image_dimensions_y
                image_width.text = image_dimensions_x
                datetimecreated = etree.SubElement(img, 'datetimecreated')
                datetimecreated.text = str(meta_info.get('File:FileCreateDate'))
                # image metrics contains all mandatory metrics on the image
                image_metrics = etree.SubElement(img, 'image_metrics')
                samplingfrequencyunit = etree.SubElement(image_metrics,
                                                         etree.QName(NISO_NAMESPACE, "samplingfrequencyunit"),
                                                         nsmap=NSMAP)
                # I will use dpi to determine x and y sampling frequency, using always inches (frequency unit = 2)
                samplingfrequencyunit.text = '2'
                # sampling frequency plane will be always 1, assuming we are reproducing with a camera, and not a scanner. But we will check with exif data
                samplingfrequencyplane = etree.SubElement(image_metrics,
                                                          etree.QName(NISO_NAMESPACE, "samplingfrequencyplane"),
                                                          nsmap=NSMAP)
                samplingfrequencyplane.text = str(meta_info.get('EXIF:PlanarConfiguration'))
                # here we do not use xsamplingfrequency and ysamplingfrequency as advised by the Mag Manual
                # it will come in a later version of the app
                # photometric interpretation is given in exif tools documentation: https://exiftool.org/TagNames/EXIF.html
                photometric_interpretation = etree.SubElement(image_metrics,
                                                              etree.QName(NISO_NAMESPACE, "photometricinterpretation"),
                                                              nsmap=NSMAP)
                if meta_info.get('EXIF:PhotometricInterpretation') == 2:
                    photometric_interpretation.text = 'RGB'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 3:
                    photometric_interpretation.text = 'RGB Palette'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 0:
                    photometric_interpretation.text = 'WhiteIsZero'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 1:
                    photometric_interpretation.text = 'BlackIsZero'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 4:
                    photometric_interpretation.text = 'Transparency Mask'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 5:
                    photometric_interpretation.text = 'CMYK'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 6:
                    photometric_interpretation.text = 'YCbCr'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 8:
                    photometric_interpretation.text = 'CIELab'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 9:
                    photometric_interpretation.text = 'ICCLab'
                elif meta_info.get('EXIF:PhotometricInterpretation') == 10:
                    photometric_interpretation.text = 'ITULab'
                bitpersample = etree.SubElement(image_metrics,
                                                etree.QName(NISO_NAMESPACE, "bitpersample"),
                                                nsmap=NSMAP)
                bitpersample.text = str(meta_info.get('EXIF:BitsPerSample'))
                format = etree.SubElement(img, 'format')
                name = etree.SubElement(format, etree.QName(NISO_NAMESPACE, "name"), nsmap=NSMAP)
                name.text = str(meta_info.get('File:FileType'))
                # 'File:MIMEType'
                mime = etree.SubElement(format, etree.QName(NISO_NAMESPACE, "mime"), nsmap=NSMAP)
                mime.text = str(meta_info.get('File:MIMEType'))
                compression = etree.SubElement(format, etree.QName(NISO_NAMESPACE, "compression"), nsmap=NSMAP)
                if meta_info.get('EXIF:Compression') == 2:
                    compression.text = 'CCITT 1D'
                elif meta_info.get('EXIF:Compression') == 3:
                    compression.text = 'T4/Group 3 Fax'
                elif meta_info.get('EXIF:Compression') == 1:
                    compression.text = 'Uncompressed'
                elif meta_info.get('EXIF:Compression') == 4:
                    compression.text = 'T6/Group 4 Fax'
                elif meta_info.get('EXIF:Compression') == 5:
                    compression.text = 'LZW'
                elif meta_info.get('EXIF:Compression') == 6:
                    compression.text = 'JPEG (old-style)'
                elif meta_info.get('EXIF:Compression') == 7:
                    compression.text = 'JPEG'
                elif meta_info.get('EXIF:Compression') == 8:
                    compression.text = 'Adobe Deflate'
                elif meta_info.get('EXIF:Compression') == 9:
                    compression.text = 'JBIG B&W'
                elif meta_info.get('EXIF:Compression') == 10:
                    compression.text = 'JBIG Color'
                elif meta_info.get('EXIF:Compression') == 99:
                    compression.text = 'JPEG'
                root.append(img)

        # create list of <image> tag until the end of the document

        # write complete xml file
        # stampa del file con aggiunta della dichiarazione xml
        print(etree.tostring(root, pretty_print=True, encoding="utf8", xml_declaration=True))

        # creo file temporaneo se non esiste già, in modo che possa essere riscritto in seguito,
        # per esempio durante il caricamento foto, con un processo parallelo
        base_path_xml = Path.home() / 'AppData' / 'Local' / 'Temp' / 'temporary_iccu_folder_xml'
        p = Path(base_path_xml)
        if p.exists() and p.is_dir():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)
        # write xml file
        filename_xml = "metadata_archivio.xml"
        tree = etree.ElementTree(root)
        os.chdir(base_path_xml)
        tree.write(filename_xml)
        # validate xml document against given MAG schema
        '''
        xmlschema = etree.XMLSchema(file='C:/Users/nromeo/OneDrive - DXC Production/Desktop/ICCU Digitalizzazione/ICCU/OLD USEFUL STUFF/metatype.xsd')
        try:
            if not xmlschema.validate(tree):
                #this will print the exception
                print(xmlschema.validate(tree))
                messagebox.showerror("Errore di caricamento",
                                     "Il file {0} non è uno zip. Le immagini devono essere compresse in uno zip. Riprova.".format(
                                         str(xmlschema.validate(filename_xml))))
            else:
                messagebox.showinfo("Il documento xml e' valido.")
        except Exception as e: raise(e)
        '''
        path_xml = base_path_xml / filename_xml
        download_path = Path.home() / "Downloads"
        # if the file exists, copy the file in the download folder and open it
        # first delete anything we created in the download folder.
        if os.path.exists(download_path):
            os.remove(download_path / filename_xml)
        if os.path.exists(path_xml):
            shutil.move(path_xml, download_path)
            if os.path.exists(download_path / filename_xml):
                webbrowser.open(download_path / filename_xml)
            else:
                print("The xml file has not been moved and is still in the Appdata folder")
        else:
            print("The xml file does not exist")

        # validate this againts given existing schema XSD

    B1 = ttk.Button(second_frame, text="Carica Foto", command=carica_foto).grid(column=1, row=31, sticky=W)
    # B2 = ttk.Button(root, text="Carica Dati", command= carica_dati).grid(column=1, row=13, sticky=W)
    B3 = ttk.Button(second_frame, text="Genera XML", command=genera_xml).grid(column=1, row=32, sticky=W)

    # adding some polish
    # root.bind("<Return>", carica_foto())

    root.mainloop()


# Driver Code

# Decide the two file paths according to your
# computer system


# Call the make_json function


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_app()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
