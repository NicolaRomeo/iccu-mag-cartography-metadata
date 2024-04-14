# iccu-mag-cartography-metadata
python script for a Desktop app to be run on Mac Os that converts a set of images for the digitization of cartographical material following the italian MAG standard
The app was made and tested with Big Sur as operating system and it's not necessarily
compatible with other Mac Os operating systems. 

### How to build 
Clone the project in your Mac Os Big Sur
machine. Then from a terminal, inside the project folder, run

> python3 setup.py py2app


for documentation on py2app
https://py2app.readthedocs.io/en/latest/tutorial.html


you can build in alias mode with
> python setup.py py2app -A


To combine py2app with setup.py
https://py2app.readthedocs.io/en/latest/setuptools.html

# Run the application

### Prerequisite
Install the MacOS image for exiftool from the website
https://exiftool.org/

the application is tested with ExifTool-12.82.dmg.

### Run 
Go to the application package. Click right > Package Contents.
Navigate to MacOs > double click on ICCU_MAG_METADATA

