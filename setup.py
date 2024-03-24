"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['ICCU_MAG_METADATA.py']
EXTRA_SCRIPTS = ['handle_upload.py']
install_requires = [
    'lxml==5.1.0',
    'filetype==1.0.8',
    'requests==2.31.0',
    'tk==0.1.0',
    'pillow==10.2.0',
    'filetype==1.0.8',
    'exif==1.3.4',
    'setuptools==69.1.1',
    'PyExifTool==0.5.6'
]
OPTIONS =  {'includes': install_requires, 'extra_scripts': EXTRA_SCRIPTS}

setup(
    name='ICCU_MAG_METADATA',
    description='Read picture metadata and fill out an xml',
    author='Nicola Romeo',
    author_email='nicolaromeo1@gmail.com',
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
