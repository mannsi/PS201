from tkinter import *
import os

class Dialog(Toplevel):
    def __init__(self,parent,title=None,showCancel=True,type=None):
        Toplevel.__init__(self, parent)
        self.type = type
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.result = None
        self.showCancel = showCancel
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        # Centering to parent
        self.update_idletasks()
        selfWidth = self.winfo_width()
        selfHeight = self.winfo_height()
        parentWidth = parent.winfo_width()
        parentHeight = parent.winfo_height()
        x = (parentWidth / 2) - (selfWidth / 2) + parent.winfo_rootx()
        y = (parentHeight / 2) - (selfHeight / 2)  + parent.winfo_rooty()     
        self.geometry("+%d+%d" % (x,y))
        
        
        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        separator = Frame(self,height=2, bd=1, relief=SUNKEN)
        separator.pack(fill=X, padx=5, pady=5)
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)

        if self.showCancel:
          w = Button(box, text="Cancel", width=10, command=self.cancel)
          w.pack(side=LEFT, padx=5, pady=5)
          self.bind("<Escape>", self.cancel)

        box.pack(anchor=S+E)

    #
    # standard button semantics

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        return 1 # override

    def apply(self):
        pass # override