from tkinter import *
from tkinter.ttk import *
from ScheduleLine import ScheduleLine

class ScheduleLineFrame(Frame):
  def __init__(self,parent):
    Frame.__init__(self,parent)
    self.canvas = parent
    self.canvas.pack(fill="both",expand=True)
    self.canvas.create_window((0,0), window=self, anchor="nw",tags ="self")
    self.bind("<Configure>", self.OnFrameConfigure)
    self.scrollbarActive = False
    self.initializeView()

  def initializeView(self):
    self.initalizingView = True
    self.lines = []
    self.rowNumber = 1
    self.addHeaderLine()
    self.addLine()
    self.initalizingView = False

  def checkIfAddScrollbar(self):
    if not self.scrollbarActive and not self.initalizingView:
      widgetsHeight = self.getWidgetsHeight()
      #print("Widgets ",widgetsHeight)
      totalHeight = self.canvas.winfo_height()
      #print("Total ",totalHeight)
      return widgetsHeight > totalHeight

  def checkIfRemoveScrollbar(self):
    if self.scrollbarActive:
      widgetsHeight = self.getWidgetsHeight()
      #print("Widgets ",widgetsHeight)
      totalHeight = self.canvas.winfo_height()
      #print("Total ",totalHeight)
      return widgetsHeight <= totalHeight

  def addScrollbar(self):
    self.vsb = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
    self.canvas.configure(yscrollcommand=self.vsb.set)
    self.vsb.pack(side="right", fill="y")
    self.scrollbarActive = True

  def removeScrollbar(self):
    self.vsb.pack_forget()
    self.scrollbarActive = False

  def getWidgetsHeight(self):
    self.update_idletasks()
    widgetsHeight = self.headerLabelV.winfo_height()
    for line in self.lines:
      if line:
        widgetsHeight += line.removeLineButton.winfo_height()
    return widgetsHeight

  def addHeaderLine(self):
    self.headerLabelV = Label(self,text="Voltage(V)")
    self.headerLabelV.grid(row=0,column=0,sticky=W)
    Label(self,text="Current(mA)").grid(row=0,column=1,sticky=W)
    Label(self,text="Duration").grid(row=0,column=2, columnspan=2)

  def addLine(self,voltage=None,current=None,timeType=None,duration=None):
    if voltage is not None and current is not None and timeType is not None and duration is not None:
      line = ScheduleLine(self,self.rowNumber,self.removeLine,voltage=voltage,current=current,timeType=timeType,duration=duration)
    elif self.rowNumber == 1:
      line = ScheduleLine(self,self.rowNumber,self.removeLine)
    else:
      counter = 1
      prevLine = self.lines[self.rowNumber - 2]
      while prevLine is None and (self.rowNumber - 1) > 0:
        counter += 1
        prevLine = self.lines[self.rowNumber - counter]
      if prevLine:
        line = ScheduleLine(self,self.rowNumber,self.removeLine,voltage=prevLine.getVoltage(),current=prevLine.getCurrent(),timeType=prevLine.getTimeType(),duration=prevLine.getDuration())
      else:
        line = ScheduleLine(self,self.rowNumber,self.removeLine)
    line.voltageEntry.grid(row=self.rowNumber,column=0)
    line.currentEntry.grid(row=self.rowNumber,column=1)
    line.timeSizeType.grid(row=self.rowNumber,column=2)
    line.durationEntry.grid(row=self.rowNumber,column=3)
    line.removeLineButton.grid(row=self.rowNumber,column=4)
    if len(self.lines) > self.rowNumber:
      self.lines[self.rowNumber-1] = line
    else:
      self.lines.append(line)
    self.rowNumber += 1
    self.canvas.update_idletasks()
    if self.checkIfAddScrollbar():
      self.addScrollbar()


  def removeLine(self, rowNumber, widgetsToRemove):
    for widget in widgetsToRemove:
      widget.grid_forget()
    self.lines[rowNumber - 1] = None
    self.rowNumber -= 1
    self.canvas.update_idletasks()
    if self.checkIfRemoveScrollbar():
      self.removeScrollbar()

  def clearAllLines(self):
    for line in self.lines:
      if line:
        line.removeLineFunc()

  def getLines(self):
    return [x for x in self.lines if x]

  def OnFrameConfigure(self, event):
    '''Reset the scroll region to encompass the inner frame'''
    self.canvas.configure(scrollregion=(0,0,0,self.getWidgetsHeight()))
    #self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    #print(self.canvas.bbox("all"))


"""
def AddLine():
  scheduleLineFrame.addLine()

def RemoveScrollbar():
  scheduleLineFrame.vsb.pack_forget()

def AddScrollbar():
  scheduleLineFrame.addScrollbar()

root = Tk()
mainWindowSize = '600x300'
root.geometry(mainWindowSize)
canvas = Canvas(root,background="green",height=100)
scheduleLineFrame = ScheduleLineFrame(canvas)
#scheduleLineFrame.pack()
#scheduleLineFrame.addLine("bla","blabla")

Button(root,text="Add line",command=AddLine).pack(anchor=S+E)
Button(root,text="Remove scrollbar",command=RemoveScrollbar).pack(anchor=S+E)
Button(root,text="Add scrollbar",command=AddScrollbar).pack(anchor=S+E)

root.mainloop()
"""
