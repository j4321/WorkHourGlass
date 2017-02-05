WorkHourGlass - Enhance your efficiency by timing your work and breaks
======================================================================
Copyright 2015 Juliette Monsel <j_4321@hotmail.fr>

WorkHourGlass is a simple timer that allows you to manage easily your 
working time. It times your work and breaks, making a beep sound at the 
end of each so that you know you can take a break / return to your work.
There is also a change of color between break time and work time.

The times, sound and colors are customizable.

Install
=======

Windows version
---------------

1. Download WorkHourGlass-1.1.1-windows.zip

2. Unzip the archive

3. If you want to use the default fonts for the software, you need to 
install the fonts included in the /fonts folder (just doubleclick  on 
the font file, it should offer you to install it). 
If you dislike the font I used to display the time, just go to the 
settings to change it.

4. Launch WorkHourGlass from the shortcut in the folder, it is a 
standalone software. If the shortcut does not work, create another one 
from `WorkHourGlass-1.1.1-windows\exe.win32-3.4\WorkHourGlass.exe`

Souce code
----------

1. Prerequisites

This software is based on Python 3 and Tkinter interface so you will need 
to have them installed to use it. To play the sound I use VLC in command
line.

1.1. Windows users

Install Python 3: https://www.python.org/downloads/windows/
Install Pillow: https://pypi.python.org/pypi/Pillow/

In both case, be careful to choose the python 3 versions 
(it won't work with python 2)

1.2. Linux users

Install with your package manager the following packages (names might 
slightly change according to the distribution):

Ubuntu/Debian:
I you wish, you can launch install_debian-ubuntu to install 
automatically the needed dependencies and the software. Otherwise, 
you need to install:

- python3-tk 
- python3-pil
- python3-pil.imagetk
- vlc

Archlinux:

- tk
- python-pillow
- vlc

2. Getting started

Unpack the archive. If you want to use the default fonts for the software,
you need to install the two fonts included in the /fonts folder.

In many Linux distributions, you just need to move the font files to the
`~/.fonts` folder to do so.

In Windows, just doubleclick on the font file, it should offer you to
install it. The font I use to display the time does not look good on
Windows, so feel free to find a better one (go to the settings to change
it)

Now, you can launch WorkHourGlass.py.
In Windows, you might need to select open with pythonw.exe (which is in
the file `C:\Python3x`).

In Linux, you can make WorkHourGlass.py executable or launch it with

:: 
    $ python3 WorkHourGlass.py

If you have any troubles or comments, don't hesitate to send me an email
at j_4321@hotmail.fr



Changelog
=========

Changes between version 1.1.0 and 1.1.1
---------------------------------------

I just added a pomodoro counter and a popup message when one wants to
interrupt the timer to remind him/her that it is not good for efficiency.

I made a standalone version for Windows users so that they do not need
to install python.

/!\ If you encounter troubles after the update, locate the current 
configuration file .workhourglass (it should be either in the folder 
WorkHourGlass_files/ or in your home folder) and delete it. This should 
correct the problem.

Changes between version 1.0 and 1.1
-------------------------------------

I realized that what I had implemented is a pomodoro timer (see Pomodoro
technique on Wikipedia for more details). So I added a long break time
after four work session. I improved also a little bit the Settings
window.

I also realized that I had forgotten vlc in the dependencies and that my
program was not working on Windows. I think I managed to correct this
last point.
