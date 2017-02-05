#! /usr/bin/python3
# -*-coding:Utf-8 -*

""" Install script for WorkHourGlass. Only works under Debian and Ubuntu. Check whether all the dependencies are installed, then, install the missing packages and the software """

import os
from locale import getdefaultlocale

lang = getdefaultlocale()[0][:2]

if lang == "fr":
    print("\t Installation de WorkHourGlass \t\n\t\t!!!! Attention !!!!\t\t\nce script ne fonctionne que sous Debian ou Ubuntu ")
    continu = input("Voulez vous continuer ? [o/n] : ")
    continu = continu.lower() == "o"
else:
    print("\t WorkHourGlass Install\t\n !!!! Warning !!!! \n this script only works under Debian or Ubuntu ")
    continu = input("Do you want to proceed? [y/n] : ")
    continu = continu.lower() == "y"
    
if continu:
    install = []
    if not (os.path.exists("/usr/bin/cvlc") or 
            os.path.exists("/usr/bin/aplay") or
            os.path.exists("/usr/bin/paplay") or
            os.path.exists("/usr/bin/mpg123")):
        install.append("mpg123")
    try:
        import tkinter
    except ImportError:
        install.append("python3-tk")

    try:
        from PIL import Image, ImageTk
    except ImportError:
        install.append("python3-pil.imagetk")
        
    try:
        import matplotlib.pyplot
    except ImportError:
        install.append("python3-matplotlib")
        
    try:
        import numpy
    except ImportError:
        install.append("python3-numpy")
        
    if install != []:
        install = " ".join(install)
        os.system("sudo apt-get install "+install)
        
    os.system("sudo python3 setup.py install")

    with open(os.path.join(os.path.expanduser("~"), ".local/share/applications/WorkHourGlass.desktop"), 'w') as fich:
        fich.write("""
[Desktop Entry]
Version=1.1
Encoding=UTF-8
Name=WorkHourGlass
Comment_fr="Améliorez votre efficacité en chronométrant votre temps de travail et vos pauses"
Comment="Enhance your efficiency by timing your work and breaks"
Exec=WorkHourGlass.py
Icon=/usr/local/lib/python3.4/dist-packages/WorkHourGlass_files/icon.ico
Terminal=false
Type=Application
Path=/usr/local/lib/python3.4/dist-packages/
Categories=Utility
StartupNotify=false
""")
    FONT_PATH = os.path.join(os.path.expanduser("~"), '.fonts')
    if not os.path.exists(FONT_PATH):
        os.mkdir(FONT_PATH)
    os.system("cp fonts/TimeDisplay.otf fonts/cmunssdc.otf %s" % FONT_PATH)

    if lang == "fr":
        print("\nL'installation est terminée, vous trouverez WorkHourGlass\
 dans la catégorie Accessoires du menu.\n\
Vous pouvez si vous le souhaitez supprimer le dossier d'installation\n")
    else:
        print("\nThe installation is finished. You will find WorkHourGlass\
 in the category Utility of the menu.\n\
Now, you can delete the installation folder if you wish\n")



