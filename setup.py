#! /usr/bin/python3
# -*-coding:Utf-8 -*

from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.



setup(name = "WorkHourGlass",
      version = "1.2",
      description = "Enhance your efficiency by timing your work and breaks",
      author = "Juliette Monsel",
      author_email = "j_4321@sfr.fr",
      url = "http://sourceforge.net/projects/workhourglass/",
      license = "GNU General Public License v3",
      #Name the folder where your packages live:
      #(If you have other packages (dirs) or modules (py files) then
      #put them into the package directory - they will be found 
      #recursively.)
      packages = ['WorkHourGlass_files'],
      package_data = {'WorkHourGlass_files' : ["*", "en_US/LC_MESSAGES/*","fr_FR/LC_MESSAGES/*"]},
      scripts = ["WorkHourGlass.py"],
      long_description = """WorkHourGlass is a simple timer that allows you to manage easily your 
working time. It times your work and breaks, making a beep sound at the 
end of each so that you know you can take a break / return to your work.
There is also a change of color between break time and work time. Moreover, the times, sound and colors are customizable.

In fact, I found out that it is an basic implementation of the Pomodoro technique """,
      requires = ["PIL","tkinter","subprocess","os","tkinter.ttk",
                  "tkinter.filedialog","tkinter.colorchooser","tkinter.messagebox",
                  "pickle","locale","gettext", "sys", "matplotlib", "numpy"]
)





