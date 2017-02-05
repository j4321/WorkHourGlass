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

Timer GUI
"""
# TODO: change tasks CONFIG

from subprocess import Popen
from tkinter import Tk, Toplevel, StringVar, Menu, IntVar, PhotoImage
from tkinter.ttk import Style, Button, Label, Entry, Frame, Menubutton, Checkbutton
from tkinter.messagebox import askyesno
import os
import matplotlib.pyplot as plt
from numpy import zeros, zeros_like, array, arange, concatenate, loadtxt
import datetime as dt
from WorkHourGlass.constants import CONFIG, CMAP, STYLE, PATH_CONFIG, PATH_STATS, PL
from WorkHourGlass.constants import GO, STOP, PLUS, MOINS, TOMATE, PARAMS, GRAPH, ICON, ICON_WIN
from WorkHourGlass.params import Params
from WorkHourGlass.constants import LANG
_ = LANG.gettext

class Timer(Tk):
    """ Chronométre de temps de travail pour plus d'efficacité """
    def __init__(self):
        Tk.__init__(self)
        self.on = False  # is the timer on?

        if not CONFIG.options("Tasks"):
            CONFIG.set("Tasks", _("Work"), CMAP[0])
        # colors
        self.background = {_("Work"): CONFIG.get("Work", "bg"),
                           _("Break"): CONFIG.get("Break", "bg"),
                           _("Rest"): CONFIG.get("Rest", "bg")}
        self.foreground = {_("Work"): CONFIG.get("Work", "fg"),
                           _("Break"): CONFIG.get("Break", "fg"),
                           _("Rest"): CONFIG.get("Rest", "fg")}
        # window configuration
        if PL[0] == "w":
            self.iconbitmap(ICON_WIN, default=ICON_WIN)
        else:
            self.icon = PhotoImage(master=self, file=ICON)
            self.iconphoto(True, self.icon)

        self.title("WorkHourGlass")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.minsize(181, 190)
        self.geometry("200x190+%i+%i" % ((self.winfo_screenwidth() - 200)//2,
                                         (self.winfo_screenheight() - 190)//2))
        self.configure(background=self.background[_("Work")])

        # style
        self.style = Style(self)
        self.style.theme_use(STYLE)
        self.style.configure('fen.TLabel',
                             foreground=self.foreground[_("Work")],
                             background=self.background[_("Work")])

        # nombre de séquence de travail effectuées d'affilée (pour
        # faire des pauses plus longues tous les 4 cycles)
        self.nb_cycles = 0
        self.pomodori = IntVar(self, 0)

        # images
        self.im_go = PhotoImage(master=self, file=GO)
        self.im_stop = PhotoImage(master=self, file=STOP)
        self.im_plus = PhotoImage(master=self, file=PLUS)
        self.im_moins = PhotoImage(master=self, file=MOINS)
        self.im_params = PhotoImage(master=self, file=PARAMS)
        self.im_tomate = PhotoImage(master=self, file=TOMATE)
        self.im_graph = PhotoImage(master=self, file=GRAPH)

        # tasks list
        tasks_frame = Frame(self)
        tasks_frame.grid(row=3, column=0, columnspan=3, sticky="wnse")
        tasks = [t.capitalize() for t in CONFIG.options("Tasks")]
        self.task = StringVar(self, tasks[0])
        self.menu_tasks = Menu(tasks_frame, tearoff=False)
        for task in tasks:
            self.menu_tasks.add_radiobutton(label=task,
                                            value=task,
                                            variable=self.task)
        self.menu_tasks.add_command(label=_("New task"), image=self.im_plus,
                                    compound="left", command=self.add_task)
        self.menu_tasks.add_command(label=_("Remove task"), image=self.im_moins,
                                    compound="left", command=self.del_task)
        self.menu_tasks.add_command(label=_("Statistics"), image=self.im_graph,
                                    compound="left", command=self.display_stats)
        self.choose_task = Menubutton(tasks_frame, textvariable=self.task,
                                      menu=self.menu_tasks)
        Label(tasks_frame,
              text=_("Task: "),
              font="CMU\ Sans\ Serif\ Demi\ Condensed 12",
              width=6,
              anchor="e").pack(side="left")
        self.choose_task.pack(side="right", fill="x")

        # display
        self.tps = [CONFIG.getint("Work", "time"), 0]  # time: min, sec
        self.activite = StringVar(self, _("Work"))
        self.titre = Label(self,
                           textvariable=self.activite,
                           font='CMU\ Sans\ Serif\ Demi\ Condensed 14',
                           style='fen.TLabel',
                           anchor="center")
        self.titre.grid(row=0, column=0, columnspan=2, sticky="we")
        self.temps = Label(self,
                           text= "{0:02}:{1:02}".format(self.tps[0], self.tps[1]),
                           font="%s %i" % (CONFIG.get("General", "font"),
                                           CONFIG.getint("General", "fontsize")),
                           style='fen.TLabel',
                           anchor="center")
        self.temps.grid(row=1, column=0, columnspan=2, sticky="nswe",
                        pady=(0, 10))

        self.aff_pomodori = Label(self, textvariable=self.pomodori,
                                  image=self.im_tomate, compound="left",
                                  style='fen.TLabel',
                                  font='CMU\ Sans\ Serif\ Demi\ Condensed 14')
        self.aff_pomodori.grid(row=2, columnspan=2, sticky="e", padx=20)

        # buttons
        self.b_go = Button(self, image=self.im_go, command=self.go)
        self.b_go.grid(row=4, column=0, sticky="ew")
        self.b_params = Button(self, image=self.im_params, command=self.params)
        self.b_params.grid(row=4, column=1, sticky="ew")

    def set_config(self):
        self.background = {_("Work"): CONFIG.get("Work", "bg"),
                           _("Break"): CONFIG.get("Break", "bg"),
                           _("Rest"): CONFIG.get("Rest", "bg")}
        self.foreground = {_("Work"): CONFIG.get("Work", "fg"),
                           _("Break"): CONFIG.get("Break", "fg"),
                           _("Rest"): CONFIG.get("Rest", "fg")}
        act = self.activite.get()
        self.configure(background=self.background[act])
        self.style.configure('fen.TLabel',
                             foreground=self.foreground[act],
                             background=self.background[act])
        self.temps.configure(font="%s %i" % (CONFIG.get("General", "font"),
                                             CONFIG.getint("General", "fontsize")))

    def add_task(self):
        def ajoute(event=None):
            task = nom.get()
            if task and not CONFIG.has_option("Tasks", task):
                index = len(CONFIG.options("Tasks"))
                self.menu_tasks.insert_radiobutton(index,
                                                   label=task,
                                                   value=task,
                                                   variable=self.task)
                CONFIG.set("Tasks", task, CMAP[index % len(CMAP)])
                top.destroy()
                with open(PATH_CONFIG, "w") as file:
                    CONFIG.write(file)
                self.menu_tasks.invoke(index)
            else:
                nom.delete(0, "end")

        top = Toplevel(self)
        top.title(_("New task"))
        top.transient(self)
        top.grab_set()
        nom = Entry(top, width=20)
        nom.grid(row=0, columnspan=2, sticky="ew")
        nom.focus_set()
        nom.bind('<Key-Return>', ajoute)
        Button(top, text=_("Cancel"), command=top.destroy).grid(row=1, column=0)
        Button(top, text=_("Ok"), command=ajoute).grid(row=1, column=1)
        top.wait_window(top)

    def del_task(self):
        """ Suppression de tâches """

        def supprime():
            rep = askyesno(_("Confirmation"),
                           _("Are you sure you want to delete these tasks?"))
            if rep:
                for i in range(len(boutons)-1,-1,-1):
                    # l'ordre de parcours permet de supprimer les derniers
                    # éléments en premier afin de ne pas modifier les index des
                    # autres éléments lors des suppressions
                    task = tasks[i]
                    if "selected" in boutons[i].state():
                        # suppression de la tâche de la liste des tâches
                        CONFIG.remove_option("Tasks", task)
                        tasks.remove(task)
                        # suppression de l'entrée correspondante dans le menu
                        self.menu_tasks.delete(i)
                        if not tasks:
                            CONFIG.set("Tasks", _("Work"), CMAP[0])
                            tasks.append(_("Work"))
                            self.menu_tasks.insert_radiobutton(0,
                                                               label=_("Work"),
                                                               value=_("Work"),
                                                               variable=self.task)
                        if self.task.get() == task:
                            self.task.set(tasks[0])
                        # suppression des stats associées
                        chemin = PATH_STATS + "_" + "_".join(task.split(" "))
                        if os.path.exists(chemin):
                            os.remove(chemin)


                top.destroy()
                with open(PATH_CONFIG, "w") as file:
                    CONFIG.write(file)
            else:
                top.destroy()

        tasks = [t.capitalize() for t in CONFIG.options("Tasks")]
        top = Toplevel(self)
        top.title(_("Remove task"))
        top.transient(self)
        top.grab_set()
        style = Style(top)
        style.theme_use(STYLE)
        boutons = []
        for i, task in enumerate(tasks):
            boutons.append(Checkbutton(top, text=task))
            boutons[-1].grid(row=i, columnspan=2, sticky="w")
        Button(top, text=_("Cancel"), command=top.destroy).grid(row=i+1, column=0)
        Button(top, text=_("Delete"), command=supprime).grid(row=i+1, column=1)



    def stats(self):
        """ Enregistre la durée de travail (en min) effectuée ce jour pour la
            tâche qui vient d'être interrompue.
            Seul les pomodori complets sont pris en compte. """
        # TODO: translate, correct date/time format
        pom = self.pomodori.get()
        if pom:
            # la tâche en cours a été travaillée, il faut enregistrer les stats
            date = dt.date.today()
            task = self.task.get()
            chemin = PATH_STATS + "_" + "_".join(task.split(" "))
            if not os.path.exists(chemin):
                with open(chemin, 'w') as fich:
                    fich.write("# tâche : %s\n# jour\tmois\tannée\ttemps de travail (min)\n" % task)
            with open(chemin, 'r') as fich:
                stats = fich.readlines()
            if len(stats) > 2:
                last = stats[-1][:10], stats[-1][:-1].split("\t")[-1]
            else:
                last = "", 0
            if last[0] != date.strftime("%d\t%m\t%Y"):
                with open(chemin, 'a') as fich:
                    fich.write("%s\t%i\n" % (date.strftime("%d\t%m\t%Y"),
                                             pom*CONFIG.getint("Work", "time")))
            else:
                # un nombre a déjà été enregistré plus tôt dans la journée
                # il faut les additioner
                with open(chemin, 'w') as fich:
                    fich.writelines(stats[:-1])
                    fich.write("%s\t%i\n" % (date.strftime("%d\t%m\t%Y"),
                                             pom*CONFIG.getint("Work", "time") + int(last[1])))

    def display_stats(self):
        """ affiche les statistiques """
        plt.figure("Statistiques")
        tasks = [t.capitalize() for t in CONFIG.options("Tasks")]
        coul = [CONFIG.get("Tasks", task) for task in tasks]
        stats_x = []
        stats_y = []

        demain = dt.date.today().toordinal() + 1
        min_x = demain

        # récupération des données
        no_data = True
        for i, task in enumerate(tasks):
            chemin = PATH_STATS + "_" + "_".join(task.split(" "))
            if os.path.exists(chemin):
                no_data = False
                stat = loadtxt(chemin, dtype=int)
                if len(stat.shape) == 1:
                    stat = stat.reshape(1, 4)
                x = [dt.date(an, mois, jour).toordinal() for jour, mois, an in stat[:, :3]]
                y = stat[:, -1]/60  # temps de travail
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
        if not no_data:
            for (i, task), x, y in zip(enumerate(tasks), stats_x, stats_y):
                ax0 = plt.subplot(111)
                plt.ylabel(_("time (h)"))
                plt.xlabel(_("date"))
                yy = array([], dtype=int)
                # comble les trous par des 0
                # ainsi, les jours où une tâche n'a pas été travaillée correspondent
                # à des 0 sur le graph
                xxx = arange(min_x, x[0])
                yy = concatenate((yy, zeros_like(xxx, dtype=int)))
                for j in range(len(x) - 1):
                    xxx = arange(x[j], x[j+1])
                    yy = concatenate((yy, [y[j]], zeros(len(xxx)-1, dtype=int)))
                xxx = arange(x[-1], demain)
                yy = concatenate((yy, [y[-1]], zeros(len(xxx)-1, dtype=int)))
                plt.bar(xx-0.4, yy, bottom=yy0, width=0.8, label=task, color=coul[i])
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
#                rep = askyesno(title=_("Confirmation"),
#                               message=_("You should not interrupt your work if you want to be efficient. Do you still want to suspend the timer?"),
#                               icon="warning")
#            else:
#                rep = True
                self.stop()
#            if rep:
#                self.b_go.configure(image=self.im_go)
#            else:
#                self.on = True
#                self.affiche()
        else:
            self.on = True
            self.choose_task.config(state="disabled")
            self.b_go.configure(image=self.im_stop)
            self.after(1000, self.affiche)

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
            self.nb_cycles = 0
            self.b_go.configure(image=self.im_go)
            self.tps = [CONFIG.getint("Work", "time"), 0]
            self.temps.configure(text="{0:02}:{1:02}".format(self.tps[0], self.tps[1]))
            act = _("Work")
            self.activite.set(act)
            self.style.configure('fen.TLabel',
                                 background=self.background[act],
                                 foreground=self.foreground[act])
            self.configure(background=self.background[act])
            self.choose_task.config(state="normal")
        else:
            self.on = True
            self.affiche()

    def ting(self):
        """ joue le son marquant le changement de période """
        if not CONFIG.get("mute", False):
            if PL[0] == "w":
                Popen(["powershell", "-c",
                       '(New-Object Media.SoundPlayer "%s").PlaySync();' % (CONFIG.get("Sound", "beep"))])
            else:
                Popen([CONFIG.get("Sound", "player"),
                       CONFIG.get("Sound", "beep")])

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
                            self.tps = [CONFIG.getint("Rest", "time"), 0]
                        else:
                            # pause courte
                            self.activite.set(_("Break"))
                            self.tps = [CONFIG.getint("Break", "time"), 0]
                    else:
                        self.activite.set(_("Work"))
                        self.tps = [CONFIG.getint("Work", "time"), 0]
                    act = self.activite.get()
                    self.style.configure('fen.TLabel',
                                         background=self.background[act],
                                         foreground=self.foreground[act])
                    self.configure(background=self.background[act])
            elif self.tps[1] == -1:
                self.tps[0] -= 1
                self.tps[1] = 59
            self.temps.configure(text="{0:02}:{1:02}".format(self.tps[0],self.tps[1]))
            self.after(1000, self.affiche)

    def params(self):
        on = self.on
        self.on = False
        self.b_go.configure(image=self.im_go)
        p = Params(self)
        self.wait_window(p)
        if on:
            self.on = True
            self.choose_task.config(state="disabled")
            self.b_go.configure(image=self.im_stop)
            self.after(1000, self.affiche)


    def exit(self):
        self.stats()
        plt.close()
        self.destroy()

