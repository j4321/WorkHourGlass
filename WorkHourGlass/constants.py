#! /usr/bin/python3
# -*-coding:Utf-8 -*

"""
WorkHourGlass - Enhance your efficiency by timing your work and breaks
Copyright 2015-2017 Juliette Monsel <j_4321@protonmail.com>

WorkHourGlass is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

WorkHourGlass  is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Constants
"""

import os
from sys import platform as PL
import gettext
from locale import getdefaultlocale, setlocale, LC_ALL
import matplotlib.pyplot as plt
from configparser import ConfigParser
from tkinter import Toplevel
from tkinter.ttk import Label, Entry, Button

APP_NAME = "WorkHourGlass"
LANGUES = {"en": "English", "fr": "Français"}

PATH = os.path.dirname(__file__)
if os.access(PATH, os.W_OK):
    # PATH is writeable, app is not installed
    LOCAL_PATH = os.path.join(PATH, "workhourglass")
else:
    # app is installed
    LOCAL_PATH = os.path.join(os.path.expanduser("~"), ".workhourglass")

PATH_CONFIG = os.path.join(LOCAL_PATH, "workhourglass.ini")
PATH_STATS = os.path.join(LOCAL_PATH, "stats")
PATH_IMAGE = os.path.join(PATH, "images")
PATH_LOCALE = os.path.join(PATH, "locale")

# images
STOP = os.path.join(PATH_IMAGE, "stop.png")
GO = os.path.join(PATH_IMAGE, "go.png")
PLUS = os.path.join(PATH_IMAGE, "plus.png")
MOINS = os.path.join(PATH_IMAGE, "moins.png")
TOMATE = os.path.join(PATH_IMAGE, "tomate.png")
GRAPH = os.path.join(PATH_IMAGE, "graph.png")
ICON = os.path.join(PATH_IMAGE, "icon128.png")
ICON_WIN = os.path.join(PATH_IMAGE, "icon.ico")
PARAMS = os.path.join(PATH_IMAGE, "params.png")
COLOR = os.path.join(PATH_IMAGE, "color.png")
SON = os.path.join(PATH_IMAGE, "son.png")
MUTE = os.path.join(PATH_IMAGE, "mute.png")

# couleurs par défaut pour les stats
CMAP = ["blue", "green", "red", "cyan", "magenta", "yellow", "white", "black"]

if PL[0] == "w":
    STYLE = None
else:
    STYLE = "clam"

# configuration file
CONFIG = ConfigParser()
if not os.path.exists(LOCAL_PATH):
    os.mkdir(LOCAL_PATH)
elif os.path.isfile(LOCAL_PATH):
    # old config file
    from pickle import Unpickler
    with open(LOCAL_PATH, 'rb') as fichier:
        dp = Unpickler(fichier)
        old_conf = dp.load()

    font = old_conf.get("font", ("TimeDisplay", 48))
    CONFIG.add_section("General")
    CONFIG.set("General", "language", old_conf.get("langue", ""))
    CONFIG.set("General", "font", font[0])
    CONFIG.set("General", "fontsize", str(font[1]))
    CONFIG.add_section("Work")
    CONFIG.set("Work", "time", str(old_conf.get("work", 25)))
    CONFIG.set("Work", "bg", old_conf.get("workbg", "#ffffff"))
    CONFIG.set("Work", "fg", old_conf.get("workfg", "#000000"))
    CONFIG.add_section("Break")
    CONFIG.set("Break", "time", str(old_conf.get("pause", 5)))
    CONFIG.set("Break", "bg", old_conf.get("pausebg", "#77ABE2"))
    CONFIG.set("Break", "fg", old_conf.get("pausefg", "#000000"))
    CONFIG.add_section("Rest")
    CONFIG.set("Rest", "time", str(old_conf.get("rest", 20)))
    CONFIG.set("Rest", "bg", old_conf.get("restbg", "#FF7A40"))
    CONFIG.set("Rest", "fg", old_conf.get("restfg", "#000000"))
    CONFIG.add_section("Sound")
    CONFIG.set("Sound", "beep",
               old_conf.get("son", os.path.join(PATH, 'ting.wav')))
    CONFIG.set("Sound", "player", "")
    CONFIG.set("Sound", "mute", "False")
    CONFIG.add_section("Tasks")
    os.remove(LOCAL_PATH)
    os.mkdir(LOCAL_PATH)
    with open(PATH_CONFIG, "w") as file:
        CONFIG.write(file)

if os.path.exists(PATH_CONFIG):
    CONFIG.read(PATH_CONFIG)
else:
    CONFIG.add_section("General")
    CONFIG.set("General", "language", "")
    CONFIG.set("General", "font", "TimeDisplay")
    CONFIG.set("General", "fontsize", "48")
    CONFIG.add_section("Work")
    CONFIG.set("Work", "time", "25")
    CONFIG.set("Work", "bg", "#ffffff")
    CONFIG.set("Work", "fg", "#000000")
    CONFIG.add_section("Break")
    CONFIG.set("Break", "time", "5")
    CONFIG.set("Break", "bg", "#77ABE2")
    CONFIG.set("Break", "fg", "#000000")
    CONFIG.add_section("Rest")
    CONFIG.set("Rest", "time", "20")
    CONFIG.set("Rest", "bg", "#FF7A40")
    CONFIG.set("Rest", "fg", "#000000")
    CONFIG.add_section("Sound")
    CONFIG.set("Sound", "beep", os.path.join(PATH, 'ting.wav'))
    CONFIG.set("Sound", "player", "")
    CONFIG.set("Sound", "mute", "False")
    CONFIG.add_section("Tasks")


LANGUE = CONFIG.get("General", "language")
if LANGUE not in ["en", "fr"]:
    # Check the default locale
    lc = getdefaultlocale()[0][:2]
    # If we have a default, it's the first in the list
    if lc == "fr":
        LANGUE = "fr_FR"
    else:
        LANGUE = "en_US"
    CONFIG.set("General", "language", LANGUE[:2])

gettext.find(APP_NAME, PATH_LOCALE)
gettext.bind_textdomain_codeset(APP_NAME, "UTF - 8")
gettext.bindtextdomain(APP_NAME, PATH_LOCALE)
gettext.textdomain(APP_NAME)

# Get the language to use
LANG = gettext.translation(APP_NAME, PATH_LOCALE,
                           languages=[LANGUE], fallback=True)
LANG.install()

if not CONFIG.options("Tasks"):
    # task = color
    CONFIG.set("Tasks", _("Work"), CMAP[0])

# config affichage de la date
setlocale(LC_ALL, '')

# config matplotlib
plt.rc("axes.formatter", use_locale=True)
plt.rc('text', usetex=False)
plt.rc('font', size=12)

if PL[0] != "w" and not CONFIG.get("Sound", "player"):
    if os.path.exists("/usr/bin/aplay"):
        CONFIG.set("Sound", "player",  "aplay")
    elif os.path.exists("/usr/bin/paplay"):
        CONFIG.set("Sound", "player",  "paplay")
    elif os.path.exists("/usr/bin/mpg123"):
        CONFIG.set("Sound", "player",  "mpg123")
    elif os.path.exists("/usr/bin/cvlc"):
        CONFIG.set("Sound", "player",  "cvlc")
    else:
        top = Toplevel()
        top.resizable((0, 0))
        top.title(_("Sound configuration"))
        Label(top, text=_("The automatic detection of command line soundplayer has failed. \
If you want to hear the beep between work sessions and breaks, please give the \
name of a command line soundplayer installed on your system. If you do not know, \
you can install mpg123.")).grid(row=0, columnspan=2)
        player = Entry(top, justify='center')
        player.grid(row=1, columnspan=2, sticky="ew")

        def valide():
            CONFIG.set("Sound", "player",  player.get())
            top.destroy()
        Button(top, _("Cancel"), command=top.destroy).grid(row=2, column=0)
        Button(top, _("Ok"), command=valide).grid(row=2, column=1)


def valide_entree_nb(d, S):
    """ commande de validation des champs devant contenir
        seulement des chiffres """
    if d == '1':
        return S.isdigit()
    else:
        return True
