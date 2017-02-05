#! /usr/bin/python3
# -*-coding:Utf-8 -*

"""
WorkHourGlass - Enhance your efficiency by timing your work and breaks
Copyright 2015 Juliette Monsel <j_4321@sfr.fr>

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
"""

from subprocess import Popen
from tkinter import Tk, Toplevel, StringVar, Menu, IntVar, BooleanVar
from tkinter.ttk import Style, Button, Label, Entry, Frame, Menubutton, Separator, Checkbutton, Notebook
from tkinter.filedialog import askopenfilename
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo, showerror, askyesno
from PIL import Image, ImageTk
import os
from pickle import Pickler, Unpickler
from sys import platform as PL
import gettext
#from time import localtime
from locale import getdefaultlocale, setlocale, LC_ALL
import matplotlib.pyplot as plt
from matplotlib import rc
from numpy import zeros, zeros_like, array, arange, concatenate, loadtxt
import datetime as dt

LANGUES = {"en": "English", "fr": "Français"}
LOCAL_PATH = os.path.join(os.path.expanduser("~"), ".workhourglass/")
APP_NAME = "WorkHourGlass"

# Get the local directory since we are not installing anything
PATH = os.path.split(__file__)[0]
STOP = os.path.join(PATH, "stop.png")
GO = os.path.join(PATH, "go.png")
PAUSE = os.path.join(PATH, "pause.png")
PLUS = os.path.join(PATH, "plus.png")
MOINS = os.path.join(PATH, "moins.png")
TOMATE = os.path.join(PATH, "tomate.png")
GRAPH = os.path.join(PATH, "graph.png")
ICON = os.path.join(PATH, "icon128.png")
ICON_WIN = os.path.join(PATH, "icon.ico")
PARAMS = os.path.join(PATH, "params.png")
PATH_CONFIG = os.path.join(LOCAL_PATH,"workhourglass")
PATH_STATS = os.path.join(LOCAL_PATH, "stats")
COLOR = os.path.join(PATH, "color.png")
SON = os.path.join(PATH, "son.png")
MUTE = os.path.join(PATH, "mute.png")
# couleurs par défaut pour les stats
CMAP = ["blue", "green", "red", "cyan", "magenta", "yellow", "white", "black"]

if PL[0] == "w":
    STYLE=None
else:
    STYLE="clam"

# récupération des infos dans le fichier de configuration
if not os.path.exists(LOCAL_PATH):
    os.mkdir(LOCAL_PATH)

if os.path.exists(PATH_CONFIG):
    with open(PATH_CONFIG,'rb') as fichier:
        dp = Unpickler(fichier)
        # dictionnaire contenant les paramètres
        CONFIG = dp.load()
else:
    CONFIG = {'workbg': '#ffffff', 'workfg': '#000000', 'work': 25,
              'pausebg': '#77ABE2', 'pausefg': '#000000', 'pause': 5,
              'restbg': '#FF7A40', 'restfg': '#000000',
              'rest': 20, 'son': os.path.join(PATH, 'ting.wav'), 'langue': '',
              'tasks': [], 'task_col': CMAP, 'font': ("TimeDisplay", 48),
              'player': '', 'mute': False}

    with open(PATH_CONFIG, "wb") as fich:
        dp = Pickler(fich)
        dp.dump(CONFIG)

LANGUE = CONFIG.get("langue","")
if LANGUE not in ["en", "fr"]:
    # Check the default locale
    lc = getdefaultlocale()[0][:2]
    # If we have a default, it's the first in the list
    if lc == "fr":
        LANGUE = "fr_FR"
    else:
        LANGUE = "en_US"
    CONFIG['langue'] = LANGUE[:2]
# Now langs is a list of all of the languages that we are going
# to try to use.  First we check the default, then what the system
# told us, and finally the 'known' list

gettext.find(APP_NAME, PATH)
gettext.bind_textdomain_codeset(APP_NAME, "UTF - 8")
gettext.bindtextdomain(APP_NAME, PATH)
gettext.textdomain(APP_NAME)


# Get the language to use
LANG = gettext.translation(APP_NAME, PATH,
                           languages=[LANGUE], fallback=True)
# Install the language, map _() (which we marked our
# strings to translate with) to self.lang.gettext() which will
# translate them.
_ = LANG.gettext

if not CONFIG["tasks"]:
    CONFIG["tasks"] = [_("Work")]

# config affichage de la date
setlocale(LC_ALL, '')

# config matplotlib
rc("axes.formatter", use_locale=True)
rc('text', usetex=False)
rc('font', size=12)

if PL[0] != "w" and not CONFIG.get("player",""):
    if os.path.exists("/usr/bin/aplay"):
        CONFIG["player"] = "aplay"
    elif os.path.exists("/usr/bin/paplay"):
        CONFIG["player"] = "paplay"
    elif os.path.exists("/usr/bin/mpg123"):
        CONFIG["player"] = "mpg123"
    elif os.path.exists("/usr/bin/cvlc"):
        CONFIG["player"] = "cvlc"
    else:
        top = Toplevel()
        top.resizable((0,0))
        top.title(_("Sound configuration"))
        Label(top, text=_("The automatic detection of command line soundplayer has failed. \
If you want to hear the beep between work sessions and breaks, please give the \
name of a command line soundplayer installed on your system. If you do not know, \
you can install mpg123.")).grid(row=0, columnspan=2)
        player = Entry(top, justify='center')
        player.grid(row=1, columnspan=2, sticky="ew")
        def valide():
            CONFIG["player"] = player.get()
            top.destroy()
        Button(top, _("Cancel"), command=top.destroy).grid(row=2,column=0)
        Button(top, _("Ok"), command=valide).grid(row=2,column=1)



def valide_entree_nb(d, S):
    """ commande de validation des champs devant contenir
        seulement des chiffres """
    if d == '1':
        return S.isdigit()
    else:
        return True

def fct(fonction, *args):
    """ un truc pour éviter les problèmes lors de l'attribution de commandes
        dans des boucles for """
    return lambda : fonction(*args)

class Timer(object):
    """ Chronométre de temps de travail pour plus d'efficacité """
    def __init__(self, config):
        self.on = False  # le chrono est-il en marche ?

        self.config = config
        if not self.config["tasks"]:
            self.config["tasks"] = [_("Work")]

        self.background = {_("Work"): self.config["workbg"],
                           _("Break"): self.config["pausebg"],
                           _("Rest"): self.config["restbg"]}
        self.foreground = {_("Work"): self.config["workfg"],
                           _("Break"): self.config["pausefg"],
                           _("Rest"): self.config["restfg"]}
        # interface
        # fenêtre de l'application
        self.fen = Tk()
        if PL[0] == "w":
            self.fen.iconbitmap(ICON_WIN)
        else:
            self.icon = ImageTk.PhotoImage(Image.open(ICON))
            self.fen.tk.call('wm', 'iconphoto', self.fen._w, self.icon)
        self.fen.title("WorkHourGlass")
        self.fen.protocol("WM_DELETE_WINDOW", self.quitter)
        self.fen.rowconfigure(1, weight=1)
        self.fen.columnconfigure(0, weight=1)
        self.fen.columnconfigure(1, weight=1)
        self.fen.columnconfigure(2, weight=1)
        self.fen.minsize(181,190)

        self.fen.geometry("200x190+%i+%i" % ((self.fen.winfo_screenwidth() - 200)//2,(self.fen.winfo_screenheight() - 190)//2))
        self.fen.configure(background=self.background[_("Work")])
        # style
        self.style = Style(self.fen)
        self.style.theme_use(STYLE)
        #~ self.style.configure('work.TLabel', background = self.config["workbg"],
                             #~ foreground = self.config["workfg"])
        #~ self.style.configure('pause.TLabel', background = self.config["pausebg"],
                             #~ foreground = self.config["pausefg"])
        #~ self.style.configure('rest.TLabel', background = self.config["restbg"],
                             #~ foreground = self.config["restfg"])
        self.style.configure('fen.TLabel',
                             foreground = self.foreground[_("Work")],
                             background = self.background[_("Work")])

        # nombre de séquence de travail effectuées d'affilée (pour
        # faire des pauses plus longues tous les 4 cycles)
        self.nb_cycles = 0
        self.pomodori = IntVar(self.fen,0)

        # images
        self.im_go = ImageTk.PhotoImage(Image.open(GO))
        self.im_pause = ImageTk.PhotoImage(Image.open(PAUSE))
        self.im_stop = ImageTk.PhotoImage(Image.open(STOP))
        self.im_plus = ImageTk.PhotoImage(Image.open(PLUS))
        self.im_moins = ImageTk.PhotoImage(Image.open(MOINS))
        self.im_params = ImageTk.PhotoImage(Image.open(PARAMS))
        self.im_tomate= ImageTk.PhotoImage(Image.open(TOMATE))
        self.im_graph= ImageTk.PhotoImage(Image.open(GRAPH))

        # liste de tâches
        tache_frame = Frame(self.fen)
        tache_frame.grid(row=3, column=0, columnspan=3, sticky="wnse")
        self.tache = StringVar(self.fen, self.config["tasks"][0])
        self.menu_tache = Menu(tache_frame, tearoff=False)
        for tache in self.config["tasks"]:
            self.menu_tache.add_radiobutton(label=tache,
                                            value=tache,
                                            variable=self.tache)
#                                            command=self.change_tache)
        self.menu_tache.add_command(label=_("New task"), image=self.im_plus,
                                    compound="left", command=self.ajoute_tache)
        self.menu_tache.add_command(label=_("Remove task"), image=self.im_moins,
                                    compound="left", command=self.enleve_tache)
        self.menu_tache.add_command(label=_("Statistics"), image=self.im_graph,
                                    compound="left", command=self.aff_stats)
        self.choix_tache = Menubutton(tache_frame, textvariable=self.tache,
                                      menu=self.menu_tache)
        Label(tache_frame,
              text=_("Task: "),
              font="CMU\ Sans\ Serif\ Demi\ Condensed 12",
              width=6,
              anchor="e").pack(side="left")
        self.choix_tache.pack(side="right", fill="x")
        # affichage
        self.tps = [self.config["work"], 0]  # décompte du temps : min, sec
        self.activite = StringVar(self.fen, _("Work"))
        self.titre = Label(self.fen,
                           textvariable = self.activite,
                           font='CMU\ Sans\ Serif\ Demi\ Condensed 14',
                           style='fen.TLabel',
                           anchor="center")
        self.titre.grid(row=0, column=0, columnspan=3, sticky="we")
        self.temps = Label(self.fen,
                           text= "{0:02}:{1:02}".format(self.tps[0],self.tps[1]),
                           font="%s %i" % (self.config["font"]),
                           style='fen.TLabel',
                           anchor="center")
        self.temps.grid(row=1, column=0, columnspan=3, sticky="nswe", pady=(0,10))

        self.aff_pomodori = Label(self.fen, textvariable=self.pomodori,
                                  image=self.im_tomate, compound="left",
                                  style='fen.TLabel',
                                  font='CMU\ Sans\ Serif\ Demi\ Condensed 14')
        self.aff_pomodori.grid(row=2, columnspan=3, sticky="e", padx=20)
        # boutons de contrôle
        self.b_go = Button(self.fen, image=self.im_go, command = self.go)
        self.b_go.grid(row=4, column=0, sticky="ew")
        self.b_stop = Button(self.fen, image=self.im_stop, command = self.stop, state='disabled')
        self.b_stop.grid(row=4, column=1, sticky="ew")
        self.b_params = Button(self.fen, image=self.im_params, command = self.params)
        self.b_params.grid(row=4, column=2, sticky="ew")

        self.fen.mainloop()

    def get_fen(self):
        return self.fen

    def get_config(self):
        return self.config

    def set_config(self, config):
        self.config = config
        self.background = {_("Work"): self.config["workbg"],
                           _("Break"): self.config["pausebg"],
                           _("Rest"): self.config["restbg"]}
        self.foreground = {_("Work"): self.config["workfg"],
                           _("Break"): self.config["pausefg"],
                           _("Rest"): self.config["restfg"]}
        act = self.activite.get()
        self.fen.configure(background=self.background[act])
        self.style.configure('fen.TLabel',
                             foreground = self.foreground[act],
                             background=self.background[act])
        self.temps.configure(font="%s %i" % self.config['font'])

#    def change_tache(self):
#        if self.on and self.activite.get() == _("Work"):
#            rep = askyesno(_("Confirmation"),
#                           _("Are you sure you want to interrupt the current task to begin a new one?"))
#        else:
#            rep = True
#        if rep:
#            self.stats()
#            self.stop(False, False)

    def ajoute_tache(self):
        def ajoute(event=None):
            tache = nom.get()
            if tache and not tache in self.config["tasks"]:
                self.config["tasks"].append(tache)
                index = len(self.config["tasks"]) - 1
                self.menu_tache.insert_radiobutton(index,
                                                   label=tache,
                                                   value=tache,
                                                   variable=self.tache)
                top.destroy()
                with open(PATH_CONFIG, "wb") as fich:
                    dp = Pickler(fich)
                    dp.dump(self.config)
                self.menu_tache.invoke(index)

        top = Toplevel(self.fen)
        top.title(_("New task"))
        top.transient(self.fen)
        top.grab_set()
        nom = Entry(top, width=20)
        nom.grid(row=0, columnspan=2, sticky="ew")
        nom.focus_set()
        nom.bind('<Key-Return>', ajoute)
        Button(top, text=_("Cancel"), command=top.destroy).grid(row=1, column=0)
        Button(top, text="Ok", command=ajoute).grid(row=1, column=1)
        top.wait_window(top)

    def enleve_tache(self):
        """ Suppression de tâches """

        def supprime():
            rep = askyesno(_("Confirmation"), _("Are you sure you want to delete these tasks?"))
            if rep:
                for i in range(len(boutons)-1,-1,-1):
                    # l'ordre de parcours permet de supprimer les derniers
                    # éléments en premier afin de ne pas modifier les index des
                    # autres éléments lors des suppressions
                    tache = self.config["tasks"][i]
                    if "selected" in boutons[i].state():
                        # suppression de la tâche de la liste des tâches
                        self.config["tasks"].remove(tache)
                        # suppression de l'entrée correspondante dans le menu
                        self.menu_tache.delete(i)
                        if self.tache.get() == tache:
                            self.tache.set(self.config["tasks"][0])
                        # suppression des stats associées
                        chemin = PATH_STATS + "_" + "_".join(tache.split(" "))
                        if os.path.exists(chemin):
                            os.remove(chemin)


                top.destroy()
                with open(PATH_CONFIG, "wb") as fich:
                    dp = Pickler(fich)
                    dp.dump(self.config)
            else:
                top.destroy()

        top = Toplevel(self.fen)
        top.title(_("Remove task"))
        top.transient(self.fen)
        top.grab_set()
        style = Style(top)
        style.theme_use(STYLE)
        boutons = []
        for i,tache in enumerate(self.config["tasks"]):
            boutons.append(Checkbutton(top, text=tache))
            boutons[-1].grid(row=i, columnspan=2, sticky="w")
        Button(top, text=_("Cancel"), command=top.destroy).grid(row=i+1, column=0)
        Button(top, text=_("Delete"), command=supprime).grid(row=i+1, column=1)



    def stats(self):
        """ Enregistre la durée de travail (en min) effectuée ce jour pour la
            tâche qui vient d'être interrompue.
            Seul les pomodori complets sont pris en compte. """
        pom = self.pomodori.get()
        if pom:
            # la tâche en cours a été travaillée, il faut enregistrer les stats
            date = dt.date.today()
            tache = self.tache.get()
            chemin = PATH_STATS + "_" + "_".join(tache.split(" "))
            if not os.path.exists(chemin):
                with open(chemin, 'w') as fich:
                    fich.write("# tâche : %s\n# jour\tmois\tannée\ttemps de travail (min)\n" % tache)
            with open(chemin, 'r') as fich:
                stats = fich.readlines()
            if len(stats) > 2:
                last = stats[-1][:10], stats[-1][:-1].split("\t")[-1]
            else:
                last = "", 0
            if last[0] != date.strftime("%d\t%m\t%Y"):
                with open(chemin, 'a') as fich:
                    fich.write("%s\t%i\n" % (date.strftime("%d\t%m\t%Y"), pom*self.config["work"]))
            else:
                # un nombre a déjà été enregistré plus tôt dans la journée
                # il faut les additioner
                with open(chemin, 'w') as fich:
                    fich.writelines(stats[:-1])
                    fich.write("%s\t%i\n" % (date.strftime("%d\t%m\t%Y"), pom*self.config["work"] + int(last[1])))


    def aff_stats(self):
        """ affiche les statistiques """
        plt.figure("Statistiques")
        n = len(self.config["tasks"])
        coul = self.config.get('task_col', CMAP)
        n2 = len(coul)
        if n2 < n:
#            # pas assez de couleurs
            coul = coul + [CMAP[i % len(CMAP)] for i in range(n2,n)]
        stats_x = []
        stats_y = []

        demain = dt.date.today().toordinal() + 1
        min_x = demain

        # récupération des données
        for i,tache in enumerate(self.config["tasks"]):
            chemin = PATH_STATS + "_" + "_".join(tache.split(" "))
            if os.path.exists(chemin):
                stat = loadtxt(chemin, dtype=int)
                if len(stat.shape) == 1:
                    stat = stat.reshape(1,4)
                x = [dt.date(an, mois, jour).toordinal() for jour, mois, an in stat[:,:3]]
                y = stat[:,-1]/60 # temps de travail
                min_x = min(x[0], min_x)
                stats_x.append(x)
                stats_y.append(y)
            else:
                # la taĉhe n'a jamais été travaillée
                stats_x.append([demain - 1])
                stats_y.append(array([0]))

        # plots
        xx = arange(min_x, demain, dtype=float)
        yy0 = zeros_like(xx)  # pour empiler les stats

        for (i,tache),x,y in zip(enumerate(self.config["tasks"]), stats_x, stats_y):
            ax0 = plt.subplot(111)
            plt.ylabel(_("time (h)"))
            plt.xlabel(_("date"))


            yy = array([], dtype=int)
            # comble les trous par des 0
            # ainsi, les jours où une tâche n'a pas été travaillée correspondent
            # à des 0 sur le graph
            xxx = arange(min_x, x[0])
            yy = concatenate((yy, zeros_like(xxx, dtype=int)))
            for j in range(len(x) -1):
                xxx = arange(x[j], x[j+1])
                yy = concatenate((yy, [y[j]], zeros(len(xxx)-1, dtype=int)))
            xxx = arange(x[-1], demain)
            yy = concatenate((yy, [y[-1]], zeros(len(xxx)-1, dtype=int)))
            plt.bar(xx-0.4, yy, bottom=yy0, width=0.8, label=tache, color=coul[i])
            yy0 += yy
        axx = array([int(xt) for xt in ax0.get_xticks() if xt.is_integer()])
        ax0.set_xticks(axx)
        ax0.set_xticklabels([dt.date.fromordinal(i).strftime("%x") for i in axx])
        plt.gcf().autofmt_xdate()
        ax0.set_xlim(min_x-0.5, demain-0.5)
        lgd = plt.legend(fontsize=10)
        lgd.draggable()
        plt.subplots_adjust(top=0.95)
        max_y = yy0.max()
        ax0.set_ylim(0, max_y + 0.1*max_y)
        plt.show()

    def go(self):
        if self.on:
            self.on = False
            if self.activite.get() == _("Work"):
                rep = askyesno(title=_("Confirmation"),
                               message=_("You should not interrupt your work if you want to be efficient. Do you still want to suspend the timer?"),
                               icon="warning")
            else:
                rep = True
            if rep:
                self.b_go.configure(image=self.im_go)
            else:
                self.on = True
                self.affiche()
        else:
            self.on = True
            self.b_stop.configure(state="normal")
            self.choix_tache.config(state="disabled")
            self.b_go.configure(image=self.im_pause)
            self.fen.after(1000, self.affiche)


    def stop(self, confirmation=True):
        """ Arrête le décompte du temps et le réinitialise,
            demande une confirmation avant de le faire si confirmation=True """
        self.on = False
        if confirmation:
            rep = askyesno(title=_("Confirmation"),
                           message=_("Are you sure you want to give up the current session?"))
        else:
            rep = True
        if rep:
            self.stats()
            self.pomodori.set(0)
            if self.config.get("reset_cycles",True):
                self.nb_cycles = 0
            self.b_go.configure(image=self.im_go)
            self.b_stop.configure(state="disabled")
            self.tps = [self.config["work"], 0]
            self.temps.configure(text="{0:02}:{1:02}".format(self.tps[0],self.tps[1]))
            act = _("Work")
            self.activite.set(act)
            self.style.configure('fen.TLabel',
                                 background=self.background[act],
                                 foreground=self.foreground[act])
            self.fen.configure(background=self.background[act])
            self.choix_tache.config(state="normal")
        else:
            self.on = True
            self.affiche()

    def ting(self):
        """ joue le son marquant le changement de période """
        if not self.config.get("mute", False):
            if PL[0] == "w":
                Popen(["powershell", "-c", '(New-Object Media.SoundPlayer "%s").PlaySync();' % (self.config["son"])])
            else:
                Popen([self.config["player"], self.config["son"]])

    def affiche(self):
        if self.on:
            self.tps[1] -= 1
            if self.tps[1] == 0:
                if self.tps[0] == 0:
                    self.ting()
                    if self.activite.get() == _("Work"):
                        self.pomodori.set(self.pomodori.get() + 1)
                        self.nb_cycles += 1
                        if self.nb_cycles % 4 == 0:
                            # pause longue
                            self.activite.set(_("Rest"))
                            self.tps = [self.config["rest"], 0]
                        else:
                            # pause courte
                            self.activite.set(_("Break"))
                            self.tps = [self.config["pause"], 0]
                    else:
                        self.activite.set(_("Work"))
                        self.tps = [self.config["work"], 0]
                    act = self.activite.get()
                    self.style.configure('fen.TLabel',
                                         background=self.background[act],
                                         foreground=self.foreground[act])
                    self.fen.configure(background=self.background[act])
            elif self.tps[1] == -1:
                self.tps[0] -= 1
                self.tps[1] = 59
            self.temps.configure(text="{0:02}:{1:02}".format(self.tps[0],self.tps[1]))
            self.fen.after(1000, self.affiche)

    def params(self):
        self.on = False
        self.b_go.configure(image=self.im_go)
        Params(self)

    def quitter(self):
        self.stats()
        plt.close()
        self.fen.destroy()

class Params(Toplevel):

    def __init__(self, parent, **options):
        """ créer le Toplevel permettant de modifier les paramètres """
        Toplevel.__init__(self, parent.fen, **options)
        self.parent = parent
        self.grab_set()
        self.transient(self.parent.get_fen())
        self.title(_("Settings"))
        self.resizable(0, 0)
        self.onglets = Notebook(self)
        self.onglets.grid(row=0,column=0,columnspan=2)
        self.im_color = ImageTk.PhotoImage(Image.open(COLOR))
        self.style = Style(self)
        self.style.theme_use(STYLE)
        self.style.configure('title.TLabel', font='CMU\ Sans\ Serif\ Demi\ Condensed 12')
        self.okfct = self.register(valide_entree_nb)

        # récupération de la config actuelle
        config = self.parent.get_config()
        self.nb_tache = len(config["tasks"])

        # Général (temps, police et langue)
        self.general = Frame(self.onglets, padding=10)
        self.general.pack(fill="both", expand=True, padx=10, pady=10)
        self.onglets.add(self.general, text=_("General"))

            # Temps
        Label(self.general, text=_("Times:"),
              style='title.TLabel').grid(row=0, pady=4, sticky="w")
        self.time_frame = Frame(self.general)
        self.time_frame.grid(row=1, sticky="ew")
        Label(self.time_frame, text=_("Work: ")).grid(row=0, column=0)
        self.travail = Entry(self.time_frame, width=4, justify='center',
                             validatecommand=(self.okfct, '%d', '%S'),
                             validate='key')
        self.travail.insert(0, config["work"])
        self.travail.grid(row=0, column=1, padx=(0,10))
        Label(self.time_frame, text=_("Break: ")).grid(row=0, column=2)
        self.pause = Entry(self.time_frame, width=4, justify='center',
                           validatecommand=(self.okfct, '%d', '%S'),
                           validate='key')
        self.pause.insert(0, config["pause"])
        self.pause.grid(row=0, column=3, padx=(0,10))
        Label(self.time_frame, text=_("Rest: ")).grid(row=0, column=4)
        self.rest = Entry(self.time_frame, width=4, justify='center',
                          validatecommand=(self.okfct, '%d', '%S'),
                          validate='key')
        self.rest.insert(0, config["rest"])
        self.rest.grid(row=0, column=5)

        Separator(self.general,
                  orient='horizontal').grid(row=2, sticky="ew", pady=10)

              # Police
        self.font_frame = Frame(self.general)
        self.font_frame.grid(row=3, pady=4, sticky="ew")
        Label(self.font_frame, text=_("Font:"),
              style='title.TLabel').pack(anchor="n", side="left")
        self.exemple = Label(self.font_frame, text="02:17", anchor="center",
                             font="%s %i" % config["font"], relief="groove")
        self.exemple.pack(side="right")
        self.font_frame2 = Frame(self.general)
        self.font_frame2.grid(row=4)
        Label(self.font_frame2, text=_("Family: ")).grid(row=0, column=0, sticky="e")
        self.font = Entry(self.font_frame2, justify='center')
        self.font.insert(0, config["font"][0])
        self.font.grid(row=0, column=1, padx=(0,10), sticky="ew")
        self.font.bind('<FocusOut>', self.actualise_police)
        self.font.bind('<Key-Return>', self.actualise_police, True)
        Label(self.font_frame2, text=_("Size: ")).grid(row=0, column=2, sticky="e")
        self.size = Entry(self.font_frame2, width=4, justify='center',
                          validatecommand=(self.okfct, '%d', '%S'),
                          validate='key')
        self.size.insert(0, config["font"][1])
        self.size.grid(row=0, column=3, pady=2, sticky="w")
        self.size.bind('<FocusOut>', self.actualise_police)
        self.size.bind('<Key-Return>', self.actualise_police, True)

        Separator(self.general,
                  orient='horizontal').grid(row=5, sticky="ew", pady=10)

            # Langues
        self.lang_frame = Frame(self.general)
        self.lang_frame.grid(row=6, pady=4, sticky="ew")
        Label(self.lang_frame, text=_("Language:"),
              style='title.TLabel').pack(side="left")
        self.lang = StringVar(self.lang_frame, LANGUES[config["langue"]])
        b_lang = Menubutton(self.lang_frame, textvariable=self.lang)
        menu = Menu(b_lang, tearoff=False)
        menu.add_radiobutton(label="English", variable=self.lang,
                             value="English", command=self.change_langue)
        menu.add_radiobutton(label="Français", variable=self.lang,
                             value="Français", command=self.change_langue)
        b_lang.configure(menu=menu)
        b_lang.pack(side="right")

        # Son
        self.im_son = ImageTk.PhotoImage(Image.open(SON))
        self.im_mute = ImageTk.PhotoImage(Image.open(MUTE))

        self.son = Frame(self.onglets, padding=10)
        self.son.pack(fill="both", expand=True, padx=10, pady=10)
        self.son.columnconfigure(1, weight=1)
        self.onglets.add(self.son, text=_("Sound"))

        Label(self.son, text=_("Sound:"),
              style='title.TLabel').grid(row=0, pady=4, sticky="w")
        self.mute = BooleanVar(self)
        self.mute.set(not config.get("mute", False))

        def mute_unmute():
            if self.mute.get():
                self.mute.set(False)
                b_son.configure(image=self.im_son)
            else:
                self.mute.set(True)
                b_son.configure(image=self.im_mute)

        b_son = Button(self.son, command=mute_unmute)
        mute_unmute()
        b_son.grid(row=0, column=1, sticky="e", pady=4)
        self.son_frame = Frame(self.son)
        self.son_frame.grid(row=1, sticky="ew", columnspan=2)
        self.bip = Entry(self.son_frame, justify='center')
        self.bip.insert(0, config["son"])
        self.bip.pack(side="left", fill="both", expand=True)
        Button(self.son_frame, text="...", width=2,
               command=self.choix_son).pack(side="right", padx=(2,0))

        if PL[0] != "w":
            Separator(self.son, orient='horizontal').grid(row=2, columnspan=2,
                                                          sticky="ew", pady=10)
            son_frame2 = Frame(self.son)
            son_frame2.grid(row=3, sticky="ew", columnspan=2)
            Label(son_frame2, text=_("Audio player: "),
                  style='title.TLabel').pack(side="left")
            self.player = Entry(son_frame2, justify='center')
            self.player.insert(0, config["player"])
            self.player.pack(side="right", fill="both", expand=True)


        # Couleurs
        self.couleurs = Frame(self.onglets, padding=10)
        self.couleurs.pack(fill="both", expand=True, padx=10, pady=10)
        self.onglets.add(self.couleurs, text=_("Colors"))
            # style des boutons de choix des couleurs
        self.style.configure("fond_w.TButton", background=config["workbg"])
        self.style.configure("fond_p.TButton", background=config["pausebg"])
        self.style.configure("fond_r.TButton", background=config["restbg"])
        self.style.configure("texte_w.TButton", background=config["workfg"])
        self.style.configure("texte_p.TButton", background=config["pausefg"])
        self.style.configure("texte_r.TButton", background=config["restfg"])
        self.couleurs.grid_columnconfigure(3, weight=3)
        self.couleurs.grid_rowconfigure(0, weight=1)
        Label(self.couleurs, text=_("Work: "),
              style='title.TLabel').grid(row=0, column=0, pady=4,
                                         padx=(2,10), sticky="w")
        Label(self.couleurs, text=_("Background: ")).grid(row=0, column=1,
                                                          sticky="e", pady=(6,4))
        Button(self.couleurs, width=2, command=fct(self.choix_couleur, "fond_w"),
               style='fond_w.TButton').grid(row=0, column=2, pady=4)
        Label(self.couleurs, text=_("Text: ")).grid(row=1, column=1, sticky="e")
        Button(self.couleurs, width=2, command=fct(self.choix_couleur, "texte_w"),
               style='texte_w.TButton').grid(row=1, column=2, pady=4)

        Separator(self.couleurs, orient='horizontal').grid(row=2, sticky="ew",
                                                           pady=10, columnspan=4)

        Label(self.couleurs, text=_("Break: "),
              style='title.TLabel').grid(row=3, column=0, pady=4,
                                         padx=(2,10), sticky="w")
        Label(self.couleurs, text=_("Background: ")).grid(row=3, column=1,
                                                          sticky="e", pady=(6,4))
        Button(self.couleurs, width=2, command=fct(self.choix_couleur, "fond_p"),
               style='fond_p.TButton').grid(row=3, column=2, pady=4)
        Label(self.couleurs, text=_("Text: ")).grid(row=4, column=1, sticky="e")
        Button(self.couleurs, width=2, command=fct(self.choix_couleur, "texte_p"),
               style='texte_p.TButton').grid(row=4, column=2, pady=4)

        Separator(self.couleurs, orient='horizontal').grid(row=5, sticky="ew",
                                                           pady=10, columnspan=4)

        Label(self.couleurs, text=_("Rest: "),
              style='title.TLabel').grid(row=6, column=0, pady=4,
                                         sticky="w", padx=(2,10))
        Label(self.couleurs, text=_("Background: ")).grid(row=6, column=1,
                                                          sticky="e", pady=(6,4))
        Button(self.couleurs, width=2, command=fct(self.choix_couleur, "fond_r"),
               style='fond_r.TButton').grid(row=6, column=2, pady=4)
        Label(self.couleurs, text=_("Text: ")).grid(row=7, column=1, sticky="e")
        Button(self.couleurs, width=2, command=fct(self.choix_couleur, "texte_r"),
               style='texte_r.TButton').grid(row=7, column=2, pady=4)

        # Stats
        self.stats = Frame(self.onglets, padding=10)
        self.stats.pack(fill="both", expand=True, padx=10, pady=10)
        self.stats.grid_columnconfigure(2, weight=1)
        self.onglets.add(self.stats, text=_("Statistics"))

        Label(self.stats, text=_("Statistics:"),
              style='title.TLabel').grid(row=0, column=0, pady=4, sticky="w")
        cmap = config.get('task_col', CMAP)
        n2 = len(cmap)
        if n2 < self.nb_tache:
            # pas assez de couleurs
            cmap = cmap + [CMAP[i % len(CMAP)] for i in range(n2,self.nb_tache)]

        for i, coul, tache in zip(range(self.nb_tache), cmap , config["tasks"]):
            Label(self.stats, text=tache).grid(row=i+1, column=0, sticky="e", padx=4, pady=4)
            self.style.configure("t%i.TButton" % i, background=coul)
            Button(self.stats, style="t%i.TButton" % i, width=2,
                   command=fct(self.coul_stat, i)).grid(row=i+1, column=1, pady=4)

        # Validation
        Button(self, text="Ok", command=self.valide).grid(row=1,column=1, sticky="we")
        Button(self, text=_("Cancel"), command=self.destroy).grid(row=1,column=0, sticky="we")

        self.wait_window(self)



    def actualise_police(self, event):
        """ actualise le texte d'exemple de la police choisie """
        family = self.font.get()
        family = "\ ".join(family.split(" "))
        self.exemple.configure(font="%s %s" % (family, self.size.get()))

    def choix_couleur(self, type_mode):
        """ sélection de la couleur du fond/texte pour chaque mode (travail/pause/repos) """
        coul = askcolor(self.style.lookup(type_mode+".TButton", 'background'))
        if coul:
            self.style.configure(type_mode+".TButton", background=coul[1])

    def coul_stat(self, i):
        """ choix des couleurs pour l'affichage des stats """
        coul = askcolor(self.style.lookup("t%i.TButton" % i, "background"))
        if coul:
            self.style.configure("t%i.TButton" % i, background=coul[1])

    def valide(self):
        ancien = self.parent.get_config()

        tpsw = int(self.travail.get())
        tpsp = int(self.pause.get())
        tpsr = int(self.rest.get())
        pausefg = self.style.lookup("texte_p.TButton", "background")
        pausebg = self.style.lookup("fond_p.TButton", "background")
        workfg = self.style.lookup("texte_w.TButton", "background")
        workbg = self.style.lookup("fond_w.TButton", "background")
        restfg = self.style.lookup("texte_r.TButton", "background")
        restbg =self.style.lookup("fond_r.TButton", "background")
        son = self.bip.get()
        if PL[0] != "w":
            player = self.player.get()
        else:
            player = ancien.get("player","")
        mute = self.mute.get()
        family = self.font.get()
        family = "\ ".join(family.split(" "))
        size = int(self.size.get())
        cmap = []
        for i in range(self.nb_tache):
            cmap.append(self.style.lookup("t%i.TButton" % i, "background"))

        if PL[0] == "w":
            filetypes = ['wav']
        else:
            filetypes = ["ogg", "wav", "mp3"]
        if (tpsw > 0 and tpsp > 0 and tpsr > 0 and
            os.path.exists(son) and (son.split('.')[-1] in filetypes)):
            config = {'workbg': workbg, 'workfg': workfg,
                      'pausebg': pausebg, 'pausefg': pausefg,
                      'restbg': restbg, 'restfg': restfg,
                      'pause': tpsp, 'work': tpsw, 'rest': tpsr,
                      'font': (family, size), 'son': son,
                      'langue': self.lang.get()[:2].lower(),
                      'task_col': cmap, 'player': player,
                      'mute': mute}

            nv_config = ancien.copy()
            nv_config.update(config)
            self.parent.set_config(nv_config)

            with open(PATH_CONFIG, "wb") as fich:
                dp = Pickler(fich)
                dp.dump(nv_config)
            if (ancien["work"] != config["work"] or
                ancien["pause"] != config["pause"] or
                ancien["rest"] != config["rest"]):
                self.parent.stop(False)

            self.destroy()
        else:
            showerror(_("Error"),_("There is at least one invalid setting!"))

    def change_langue(self):
        showinfo(_("Information"),
                 _("The language setting will take effect after restarting the application."))

    def choix_son(self):
        if PL[0] == "w":
            filetypes = [('WAV','*.wav')]
        else:
            filetypes = [(_("sound file"), '*.mp3 *.ogg *.wav'),
                         ('OGG', '*.ogg'),
                         ('MP3', '*.mp3'),
                         ('WAV','*.wav')]
        init = self.bip.get()
        if not os.path.exists(init):
            init=self.parent.config["son"]
        fich = askopenfilename(filetypes=filetypes, initialfile=os.path.split(init)[1], initialdir=os.path.dirname(init))
        if fich:
            self.bip.delete(0,"end")
            self.bip.insert(0, fich)
