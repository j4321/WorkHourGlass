#! /usr/bin/python3
# -*-coding:Utf-8 -*

from setuptools import setup


setup(name="workhourglass",
      version="2.0.0",
      description="Enhance your efficiency by timing your work and breaks",
      author="Juliette Monsel",
      author_email="j_4321@protonmail.com",
      url="http://sourceforge.net/projects/workhourglass/",
      license="GNU General Public License v3",
      packages=['WorkHourGlass'],
      package_data={'WorkHourGlass' : ["*", "images/*", "locale/en_US/LC_MESSAGES/*","locale/fr_FR/LC_MESSAGES/*"]},
      scripts=["workhourglass"],
      long_description="""WorkHourGlass is a simple timer that allows you to manage easily your 
working time. It times your work and breaks, making a beep sound at the 
end of each so that you know you can take a break / return to your work.
There is also a change of color between break time and work time. Moreover, the times, sound and colors are customizable.

In fact, I found out that it is an basic implementation of the Pomodoro technique """,
      install_requires=["pillow", "matplotlib", "numpy"]
)





