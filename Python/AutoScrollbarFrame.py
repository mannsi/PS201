from tkinter import *


class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise TclError("cannot use pack with this widget")
    def place(self, **kw):
        raise TclError("cannot use place with this widget")


class AutoScrollbarFrame():
  def __init__(self,parent):
    vscrollbar = AutoScrollbar(parent)
    vscrollbar.grid(row=0, column=1, sticky=N+S)

    self.canvas = Canvas(parent,
                    yscrollcommand=vscrollbar.set)
    self.canvas.grid(row=0, column=0, sticky=N+S+E+W)

    vscrollbar.config(command=self.canvas.yview)

    # make the canvas expandable
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    # create canvas contents
    self.frame = Frame(self.canvas)
    self.frame.rowconfigure(1, weight=1)
    self.frame.columnconfigure(1, weight=1)

  def show(self):
    self.canvas.create_window(0, 0, anchor=NW, window=self.frame)
    self.frame.update_idletasks()
    self.canvas.config(scrollregion=self.canvas.bbox("all"))

rows = 50
def AddOne():
  global rows
  button = Button(autoScrollFrame.frame,padx=7, pady=7, text="[%d]" % (50))
  button.grid(row=rows, column=0, sticky='news')
  autoScrollFrame.show()
  rows += 1
"""
root = Tk()

frame = Frame(root)
frame.pack(expand=1, fill=BOTH)
autoScrollFrame = AutoScrollbarFrame(frame)


for i in range(1,rows):
  button = Button(autoScrollFrame.frame,padx=7, pady=7, text="[%d]" % (i))
  button.grid(row=i, column=0, sticky='news')
autoScrollFrame.show()

Button(root, text="add one", command=AddOne).pack()

root.mainloop()
"""