from tkinter import *
from .tkBaseDialog import Dialog

class AboutDialog(Dialog):
    def body(self, master):
        Label(master, text="PsController", font=("Verdana", 24)).pack(fill=X)
        Label(master, text="Control software for the PS201. See http://githbub.com/mannsi/PS201 for source. An information website is pending").pack(fill=X)
        Label(master, text="All questions and comments can be sent to gudbjorn.einarsson@gmail.com").pack(fill=X) 
   
    def apply(self):
        pass
