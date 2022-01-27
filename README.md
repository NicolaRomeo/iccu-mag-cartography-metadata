# iccu-mag-cartography-metadata
python script for a Desktop app that converts a set of images for the digitization of cartographical material following the italian MAG standard


### How to build 
it is not necessary to build the application, as the desktop app is already packed in the zip file ICCU_MAG_METADATA_<os>_<app_version>.zip.
If you do want to build your own code however, 

from a terminal,
run 

> pyinstaller --windowed ICCU_MAG_METADATA.py


### How to run
Simply unzip the file ICCU_MAG_METADATA_<os>_<app_version>.zip anywhere.
Open the dist folder and double click on the ICCU_MAG_METADATA.exe file.



### Known issues

1. The application takes quite some time to load, therefore the user has to wait after double clicking
up to a minute before the application actually shows in the taskbar.