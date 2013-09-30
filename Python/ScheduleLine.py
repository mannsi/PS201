from tkinter import *
from tkinter.ttk import *

class ScheduleLine():
  def __init__(self, parent, rowNumber, removeLineFunc, voltage=0.0, current=0, timeType='sec', duration=0):
    self.removeLineFunc = lambda:removeLineFunc(rowNumber,[self.voltageEntry,self.currentEntry,self.timeSizeType,self.durationEntry,self.removeLineButton])
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntryVar.set(voltage)
    self.voltageEntry = Entry(parent, textvariable=self.voltageEntryVar,width=10)
    self.currentEntryVar = IntVar(None)
    self.currentEntryVar.set(current)
    self.currentEntry = Entry(parent, textvariable=self.currentEntryVar,width=10)
    self.timeSizeType_value = StringVar()
    self.timeSizeType = Combobox(parent, textvariable=self.timeSizeType_value,state='readonly',width=7)
    self.timeSizeType['values'] = ('sec', 'min', 'hour')
    if timeType=='sec':
      self.timeSizeType.current(0)
    elif timeType=='min':
      self.timeSizeType.current(1)
    elif timeType=='hour':
      self.timeSizeType.current(2)
    self.durationEntryVar = DoubleVar(None)
    self.durationEntryVar.set(duration)
    self.durationEntry = Entry(parent, textvariable=self.durationEntryVar,width=10)
    self.removeLineButton = Button(parent,text="-",width=3, command= self.removeLineFunc)
  def getVoltage(self):
    return self.voltageEntryVar.get()

  def getCurrent(self):
    return self.currentEntryVar.get()

  def getTimeType(self):
    return self.timeSizeType_value.get()

  def getDuration(self):
    return self.durationEntryVar.get()

