import json
import os
from pathlib import Path
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import zipfile
import filetype
import shutil
from exiftool import ExifToolHelper
from PIL import Image as Image_PIL
import hashlib

def carica_foto(*args):
    def extract_zip(input_zip):
        input_zip = zipfile.ZipFile(input_zip)
        return {name: input_zip.read(name) for name in input_zip.namelist()}

    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    print(filename)
    # controlla che il file passato sia uno zip
    if filename.split('.')[-1] != 'zip':
        messagebox.showerror("Errore di caricamento",
                             "Il file {0} non è uno zip. Le immagini devono essere compresse in uno zip. Riprova.".format(
                                 filename))
    # estrai il zip in una cartella temporanea
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
    #delete temporary __MACOS folder
    macos_temp_dir = base_path / '__MACOSX'
    macos_temp_path = Path(macos_temp_dir)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(p.resolve())
    if macos_temp_path.exists() and macos_temp_path.is_dir():
        shutil.rmtree(macos_temp_path)
    dest_folder = filename.split('/')[-1].removesuffix('.zip')
    full_path_to_images = Path(base_path)
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

    # EXTRACT METADATA USING EXIFTOOLS (Working as of 2021-12-29)

    '''
    with ExifTool() as e:
        exiftools_metadata = e.get_metadata(*filenames)
        #print('metadata is a {}'.format(type(metadata)))
        #print(metadata)
        e.__exit__('i', 'j', 'k')
    '''
    # EXTRACT METADATA USING PYEXIFTOOL, a wrapper for exiftool TBD
    print("Testing using PyExifTool")
    exiftools_metadata = []
    with ExifToolHelper() as et:
        for file in filenames:
            metadata = et.get_metadata(file)
            for d in metadata:
                for k, v in d.items():
                    print(f"Dict: {k} = {v}")
            exiftools_metadata.append(metadata[0])
    print("exiftool metadata found in images: \n {}".format(exiftools_metadata))
    # starts writing the xml file in append mode, because img is the last of the tags.

    # first we have to check that the file is actually there, otherwise the user will have to go through the
    # process of generating the rest of the input

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
        Pillow_img_metadata[image.filename] = {"name": image.filename, "mode": image.mode, "size": image.size,
                                               "format": image.format, "md5": md5hash.hexdigest(), "info": image.info}

    # we create all the xml tags with immutable general information that are required in the <img> tag before adding actual metadata
    # this information contains: sequence_number,nomenclature, usage, side, file location
    counter = 1
    immutable_metadata = {}
    for im in filenames:
        sequence_number = counter
        nomenclature = "Pagina {}".format(counter)
        # we will not implement the usage and side tags in this version of the application
        file_location = im.split('/')[-1]
        '''
        print('image: {} \n'
              'sequence_number: {} \n'
              'nomenclature: {} \n'
              'file_location: {} \n'.format(im,sequence_number,nomenclature,file_location))
        '''
        counter = counter + 1
        immutable_metadata[im] = {'image': im}
        immutable_metadata[im].update({'sequence_number': sequence_number})
        immutable_metadata[im].update({'nomenclature': nomenclature})
    # print("immutable_metadata {}".format(immutable_metadata))
    # USE EXAMPLE OF EXIFTOOL to get complete exif metadata of the image
    '''
    for file in metadata:
        print(file.keys())
        print("getting file name from exiftool metadata: {}".format(file["File:FileName"]))
    '''
    # create a dictionary with all available metadata and save to a json file
    complete_metadata = []
    # add immutable metadata
    for image in filenames:
        for im in immutable_metadata:
            if image == im:
                complete_metadata.append({im: immutable_metadata.get(im)})
    # add Pillow metadata
    for full_meta_image in complete_metadata:
        for i in Pillow_img_metadata:
            if full_meta_image.get(i):
                full_meta_image[i].update(Pillow_img_metadata.get(i))
            else:
                continue
    # add exif tools metadata
    # here we need to update the data structure because otherwise it's really complicated to deal with
    # the structure will be similar to the other metadata dictionaries, with the filenames as keys

    #putting together all metadata
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
    print("printing complete metadata before saving to json file \n")
    print(metadata_json_file)
    destination = base_path / "data.json"
    with open(destination, "w") as jsonFile:
        jsonFile.write(metadata_json_file)

    messagebox.showinfo("INFO: Caricamento foto", "Le foto sono state caricate correttamente. Ora puoi generare l'xml ")
