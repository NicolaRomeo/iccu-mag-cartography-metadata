# iccu-mag-cartography-metadata
python script for a Desktop app to be run on Mac Os that converts a set of images for the digitization of cartographical material following the italian MAG standard
The app was made and tested with Big Sur as operating system and it's not necessarily
compatible with other Mac Os operating systems. 

### How to build 
it is not necessary to build the application, as the desktop app is already packed 
If you do want to build the application, clone the project in your Mac Os Big Sur
machine. Then from a terminal, inside the project folder, run

> rm -rf build dist
> python3 setup.py py2app 
