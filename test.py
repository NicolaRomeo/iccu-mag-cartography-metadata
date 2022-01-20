import csv
import json
import os
import sys
import webbrowser
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from lxml import etree
from datetime import datetime
import zipfile
import subprocess
import filetype
import shutil
from PIL import Image as Image_PIL
import hashlib
import requests
from requests_file import FileAdapter
from exif import Image as IMAGE_exif

'''
Should also try Pillow instead of PIL
'''

class ExifTool(object):

    sentinel = "{ready}\r\n"

    def __init__(self, executable="C:\Program Files\exiftool(-k).exe"):
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            [self.executable, "-stay_open", "True", "-@", "-"],
            universal_newlines=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def  __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.endswith(self.sentinel):
            output += os.read(fd, 4096).decode('utf-8')
        return output[:-len(self.sentinel)]

    def get_metadata(self, *filenames):
        return json.loads(self.execute("-G", "-j", "-n", "-f", *filenames))

def carica_foto(*args):
    def extract_zip(input_zip):
        input_zip = zipfile.ZipFile(input_zip)
        return {name: input_zip.read(name) for name in input_zip.namelist()}
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    print(filename)
    #controlla che il file passato sia uno zip
    if filename.split('.')[-1] != 'zip':
        messagebox.showerror("Errore di caricamento", "Il file {0} non è uno zip. Le immagini devono essere compresse in uno zip. Riprova.".format(filename))
    #estrai il zip in una cartella temporanea
    '''
    #estrai nella stessa cartella dove si trova il file
    try:
        lista = filename.split('/')
        base_path = ''
        for i in lista:
            base_path = base_path + '/' + i
    '''
    base_path = Path.home() / 'AppData' / 'Local' / 'Temp' / 'temporary_iccu_folder'
    p = Path(base_path)
    if p.exists() and p.is_dir():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(p.resolve())
    dest_folder = filename.split('/')[-1].removesuffix('.zip')
    full_path_to_images = Path(base_path / dest_folder)
    filenames = []
    for imagename in os.listdir(full_path_to_images):
        image_path = full_path_to_images / imagename
        full_path = image_path.absolute()
        my_path = full_path.as_posix()
        if filetype.is_image(my_path):
            filenames.append(my_path)
        else:
            continue
    print('elenco delle immagini recuperate: {}'.format(filenames))


    #EXTRACT METADATA USING EXIFTOOLS (Working as of 2021-12-29)
    with ExifTool() as e:
        exiftools_metadata = e.get_metadata(*filenames)
        '''
        print('metadata is a {}'.format(type(metadata)))
        print(metadata)
        '''
        e.__exit__('i','j','k')

    #starts writing the xml file in append mode, because img is the last of the tags.

    #first we have to check that the file is actually there, otherwise the user will have to go through the
    #process of generating the rest of the input


    # USE PILLOW (PIL) TO GET IMAGE METADATA
    Pillow_img_metadata = {}
    for im in filenames:
        image = Image_PIL.open(im)
        md5hash = hashlib.md5(Image_PIL.open(im).tobytes())
        '''
        print(
            "filename: {} \n".format(image.filename),
            "mode: {} \n".format(image.mode), "size: {} \n".format(image.size), "format: {} \n".format(image.format),
            "info: {} \n".format(image.info),
            "md5: {} \n".format(md5hash)
            "********************************\n"
        )
        '''
        Pillow_img_metadata[image.filename]= {"name":image.filename,"mode":image.mode,"size":image.size,"format":image.format,"md5":md5hash.hexdigest(),"info":image.info}

    #we create all the xml tags with immutable general information that are required in the <img> tag before adding actual metadata
    #this information contains: sequence_number,nomenclature, usage, side, file location
    counter = 1
    immutable_metadata= {}
    for im in filenames:
        sequence_number = counter
        nomenclature = "Pagina {}".format(counter)
        #we will not implement the usage and side tags in this version of the application
        file_location = im.split('/')[-1]
        '''
        print('image: {} \n'
              'sequence_number: {} \n'
              'nomenclature: {} \n'
              'file_location: {} \n'.format(im,sequence_number,nomenclature,file_location))
        '''
        counter = counter + 1
        immutable_metadata[im]= {'image':im}
        immutable_metadata[im].update({'sequence_number':sequence_number})
        immutable_metadata[im].update({'nomenclature': nomenclature})
    #print("immutable_metadata {}".format(immutable_metadata))
    #USE EXAMPLE OF EXIFTOOL to get complete exif metadata of the image
    '''
    for file in metadata:
        print(file.keys())
        print("getting file name from exiftool metadata: {}".format(file["File:FileName"]))
    '''
    #create a dictionary with all available metadata and save to a json file
    complete_metadata = []
    #add immutable metadata
    for image in filenames:
        for im in immutable_metadata:
            if image == im:
                complete_metadata.append({im:immutable_metadata.get(im)})
    #add Pillow metadata
    for full_meta_image in complete_metadata:
        for i in Pillow_img_metadata:
            if full_meta_image.get(i):
                full_meta_image[i].update(Pillow_img_metadata.get(i))
            else:
                continue
    #add exif tools metadata
    #here we need to update the data structure because otherwise it's really complicated to deal with
    #the structure will be similar to the other metadata dictionaries, with the filenames as keys
    exiftools_metadata_dict = {}
    for j in exiftools_metadata:
        exiftools_metadata_dict[j['SourceFile']] = j
    for full_meta_image in complete_metadata:
        for i in exiftools_metadata_dict:
            if full_meta_image.get(i):
                full_meta_image[i].update(exiftools_metadata_dict.get(i))
            else:
                continue
    metadata_json_file = json.dumps(complete_metadata)
    print("printing complete metadata before saving to json file")
    print(metadata_json_file)
    destination = base_path / "data.json"
    with open(destination, "w") as jsonFile:
        jsonFile.write(metadata_json_file)




def run_app():

    #main application window
    root = Tk()
    root.title("ICCU Digitalisation Cartography - images to xml")
    #frame widget
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.pack(fill=BOTH,expand=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    #start event loop
    my_canvas= Canvas(mainframe)
    my_canvas.pack(side=LEFT,fill=BOTH,expand=1)
    my_scrollbar = ttk.Scrollbar(mainframe, orient=VERTICAL,command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT,fill=Y)
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>',lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    #create another frame inside the canvas
    second_frame = Frame(my_canvas)
    my_canvas.create_window((0,0),window=second_frame, anchor='nw')

    '''                     SEZIONE GEN         '''
    #input utente per Stprog: indicazione del progetto di digitalizzazione. Esempio: www.mioprogetto.it
    # oppure l'home page dell'istituzione responsabile oppure l'uri del progetto
    L1 = Label(second_frame, text="Stprog (premi invio nella casella di testo per inserire i dati)").grid(column=1, row=1, sticky=W)
    E1 = Entry(second_frame, bd=5)
    E1.grid(column=1, row=2, sticky=W)

    #input utente per agency = istituzione responsabile del processo.
    L2 = Label(second_frame, text="Agency (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=3, sticky=W)
    E2 = Entry(second_frame, bd=5)
    E2.grid(column=1, row=4, sticky=W)

    #input utente per diritti di accesso: (uso riservato all'interno dell'istituzione= 0, uso pubblico=1)
    L3 = Label(second_frame, text="Diritti di accesso").grid(column=1, row=5, sticky=SW)
    var = IntVar()
    R1 = Radiobutton(second_frame, text="0: Uso riservato all'interno dell'istituzione", variable=var, value=0)
    R2 = Radiobutton(second_frame, text="1: Uso pubblico", variable=var, value=1)
    R1.grid(column=1, row=6, sticky=W)
    R2.grid(column=2, row=6, sticky=W)
    #input utente per Completezza della digitalizzazione: (0=completa, 1=incompleta)
    L4 = Label(second_frame, text="Completezza della digitalizzazione").grid(column=1, row=7, sticky=W)
    option = IntVar()
    R1 = Radiobutton(second_frame, text="0: digitalizzazione completa", variable=option, value=0)
    R2 = Radiobutton(second_frame, text="1: digitalizzazione incompleta", variable=option, value=1)
    R1.grid(column=1, row=8, sticky=W)
    R2.grid(column=2, row=8, sticky=W)

    '''                     SEZIONE BIB         '''
    #livello cioè tipo di pubblicazione
    #a=analitico; c=raccolta; m=monografia; s=pubblicazione in serie
    L3A = Label(second_frame, text="Livello ovvero tipo di pubblicazione (premi invio nella casella di testo per inserire i dati) ").grid(
        column=1, row=9, sticky=W)
    level = StringVar(second_frame)
    level.set("m=monografia")  # default value
    O1 = OptionMenu(second_frame, level, "a=analitico", "c=raccolta", "m=monografia", "s=pubblicazione in serie")
    O1.grid(column=1, row=10, sticky=W)
    #identificatore univoco
    L3B = Label(second_frame, text="Identificatore univoco (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=11, sticky=W)
    E3 = Entry(second_frame, bd=5)
    E3.grid(column=1, row=12, sticky=W)
    #titolo
    L4 = Label(second_frame, text="Titolo dell'opera (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=13, sticky=W)
    E4 = Entry(second_frame, bd=5)
    E4.grid(column=1, row=14, sticky=W)
    #creatore o autore dell'opera
    L5 = Label(second_frame, text="Autore dell'opera (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=15, sticky=W)
    E5 = Entry(second_frame, bd=5)
    E5.grid(column=1, row=16, sticky=W)
    #editore
    L6 = Label(second_frame, text="Editore dell'opera (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=17, sticky=W)
    E6 = Entry(second_frame, bd=5)
    E6.grid(column=1, row=18, sticky=W)
    #anno di pubblicazione
    L7 = Label(second_frame, text="Data di pubblicazione nel formato YYYY-MM-DD (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=19, sticky=W)
    E7 = Entry(second_frame, bd=5)
    E7.grid(column=1, row=20, sticky=W)
    # descrizione
    L8 = Label(second_frame, text="Descrizione (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=21, sticky=W)
    E8 = Entry(second_frame, bd=5)
    E8.grid(column=1, row=22, sticky=W)
    # luogo di pubblicazione
    L9 = Label(second_frame, text="Luogo di pubblicazione (premi invio nella casella di testo per inserire i dati) ").grid(column=1, row=23, sticky=W)
    E9 = Entry(second_frame, bd=5)
    E9.grid(column=1, row=24, sticky=W)
    L10 = Label(second_frame, text="Luogo di pubblicazione (premi invio nella casella di testo per inserire i dati) ").grid(
        column=1, row=25, sticky=W)
    E10 = Entry(second_frame, bd=5)
    E10.grid(column=1, row=26, sticky=W)

    def carica_dati():
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
                            "publisher": E6.get(), "date": E7.get(),"description":E8.get(), "coverage":E9.get(), "language": E10.get() }
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
        language = etree.SubElement(bib, etree.QName(DC_NAMESPACE, 'language'))
        language.text = input_bib["language"]

        #Read images metadata from the json file that was created when the user uploaded the images
        #check that the files exists, throw an error if it doesn't.
        base_path = Path.home() / 'AppData' / 'Local' / 'Temp' / 'temporary_iccu_folder'
        source_metadata_file = base_path / "data.json"
        if not source_metadata_file:
            messagebox.showerror("Errore: ",
                                 "Il file {0} non esiste. Questo significa che le immagini non sono ancora state caricate"
                                 "Per favore cliccare su 'Carica Foto' e riprovare.".format(
                                     source_metadata_file))
            exit()

        #open json file
        f = open(source_metadata_file)
        data = json.load(f)

        print("printing all data read from the json file containing the metadata from the images \n")
        print(data)

        for image_dict in data:
            for i in image_dict:
                meta_info = image_dict.get(i)
                #create an <img> tag for each image
                img = etree.Element("img")
                #create <img> subelements for each image
                sequence_number = etree.SubElement(img,'sequence_number')
                sequence_number.text = str(meta_info.get('sequence_number'))
                nomenclature = etree.SubElement(img,'nomenclature')
                nomenclature.text = str(meta_info.get('nomenclature'))
                #per file dobbiamo creare un attributo xlink
                attribute_name = etree.QName(XLINK_NS, "href")
                file = etree.SubElement(img,'file', {attribute_name: meta_info.get('File:FileName'),'Location':'URL'}, nsmap=NSMAP)
                md5 = etree.SubElement(img,'md5')
                md5.text = str(meta_info.get('md5'))
                md5 = etree.SubElement(img, 'filesize')
                filesize = str(meta_info.get('File:FileSize'))
                #for image dimensions we need to create the subelements with niso namespace
                image_length = etree.QName(NISO_NAMESPACE, "image_length")
                image_width = etree.QName(NISO_NAMESPACE, "image_width")
                image_dimensions_x= str(meta_info.get('size')[0])
                image_dimensions_y = str(meta_info.get('size')[1])
                image_dimension = etree.SubElement(img,'image_dimensions')
                image_length = etree.SubElement(image_dimension, image_length,nsmap=NSMAP)
                image_width = etree.SubElement(image_dimension, image_width, nsmap=NSMAP)
                image_length.text = image_dimensions_y
                image_width.text = image_dimensions_x
                datetimecreated = etree.SubElement(img, 'datetimecreated')
                datetimecreated.text = str(meta_info.get('File:FileCreateDate'))
                #image metrics contains all mandatory metrics on the image
                image_metrics = etree.SubElement(img, 'image_metrics')
                samplingfrequencyunit = etree.SubElement(image_metrics, etree.QName(NISO_NAMESPACE, "samplingfrequencyunit"),nsmap=NSMAP)
                #I will use dpi to determine x and y sampling frequency, using always inches (frequency unit = 2)
                samplingfrequencyunit.text = '2'
                #sampling frequency plane will be always 1, assuming we are reproducing with a camera, and not a scanner. But we will check with exif data
                samplingfrequencyplane = etree.SubElement(image_metrics, etree.QName(NISO_NAMESPACE, "samplingfrequencyplane"),nsmap=NSMAP)
                samplingfrequencyplane.text = str(meta_info.get('EXIF:PlanarConfiguration'))
                #here we do not use xsamplingfrequency and ysamplingfrequency as advised by the Mag Manual
                #it will come in a later version of the app
                #photometric interpretation is given in exif tools documentation: https://exiftool.org/TagNames/EXIF.html
                photometric_interpretation = etree.SubElement(image_metrics,etree.QName(NISO_NAMESPACE, "photometricinterpretation"),nsmap=NSMAP)
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
                name = etree.SubElement(format,etree.QName(NISO_NAMESPACE, "name"),nsmap=NSMAP)
                name.text = str(meta_info.get('File:FileType'))
                #'File:MIMEType'
                mime = etree.SubElement(format,etree.QName(NISO_NAMESPACE, "mime"),nsmap=NSMAP)
                mime.text = str(meta_info.get('File:MIMEType'))
                compression = etree.SubElement(format,etree.QName(NISO_NAMESPACE, "compression"),nsmap=NSMAP)
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

        #create list of <image> tag until the end of the document

        #write complete xml file
        #stampa del file con aggiunta della dichiarazione xml
        print(etree.tostring(root, pretty_print=True, encoding="utf8", xml_declaration=True))

        #creo file temporaneo se non esiste già, in modo che possa essere riscritto in seguito,
        #per esempio durante il caricamento foto, con un processo parallelo
        base_path_xml = Path.home() / 'AppData' / 'Local' / 'Temp' / 'temporary_iccu_folder_xml'
        p = Path(base_path_xml)
        if p.exists() and p.is_dir():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)
        #write xml file
        filename_xml = "metadata_archivio.xml"
        tree = etree.ElementTree(root)
        os.chdir(base_path_xml)
        tree.write(filename_xml)
        #validate xml document against given MAG schema
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
        #if the file exists, copy the file in the download folder and open it
        if os.path.exists(path_xml):
            shutil.move(path_xml, download_path)
            if os.path.exists(download_path / filename_xml):
                webbrowser.open(download_path / filename_xml)
            else:
                print("The xml file has not been moved and is still in the Appdata folder")
        else:
            print("The xml file does not exist")



        
        #validate this againts given existing schema XSD


    B1 = ttk.Button(second_frame, text="Carica Foto", command=carica_foto).grid(column=1, row=27, sticky=W)
    #B2 = ttk.Button(root, text="Carica Dati", command= carica_dati).grid(column=1, row=13, sticky=W)
    B3 = ttk.Button(second_frame, text="Genera XML", command=genera_xml).grid(column=1, row=28, sticky=W)

    #adding some polish
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
