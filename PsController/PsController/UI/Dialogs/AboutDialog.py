from tkinter import *
import UI.Dialogs.tkBaseDialog

class AboutDialog(UI.Dialogs.tkBaseDialog.Dialog):
  def body(self, master):
    Label(master, text="The text in the about dialog. Don't know if it should contain f.x. email addresses or stuff like that").pack()

  def apply(self):
    pass