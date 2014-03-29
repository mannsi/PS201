from tkinter import *
from .tkBaseDialog import Dialog

class AboutDialog(Dialog):
    def body(self, master):
        Label(master, text="The text in the about dialog. Don't know if it should contain f.x. email addresses or stuff like that").pack()
   
    def apply(self):
        pass