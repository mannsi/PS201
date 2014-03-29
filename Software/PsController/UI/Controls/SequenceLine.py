from tkinter import *
from tkinter.ttk import *
from .DecimalEntry import DecimalEntry
from PsController.Model.SequenceLineStruct import SequenceLineStruct

class SequenceLine():
  def __init__(self, parent, rowNumber, removeLineFunc, voltage=0.0, current=0, timeType='sec', duration=0):
    self.rowNumber = rowNumber
    self.removeLineFunc = removeLineFunc
    self.labelText = StringVar()
    self.labelText.set("     ")
    self.selectedLabel = Label(parent,textvariable = self.labelText)
    self.voltageEntry = DecimalEntry(parent,maxDecimals=2, maxValue = 20, minValue = 0, minIncrement = 0.01,width=10)
    self.voltageEntry.set(voltage)
    self.currentEntry = DecimalEntry(parent,maxDecimals=0, maxValue = 1000, minValue = 0, minIncrement = 1,width=10)
    self.currentEntry.set(current)
    self.timeSizeType_value = StringVar()
    self.timeSizeType = Combobox(parent, textvariable=self.timeSizeType_value,state='readonly',width=7)
    self.timeSizeType['values'] = ('sec', 'min', 'hour')
    if timeType=='sec':
      self.timeSizeType.current(0)
    elif timeType=='min':
      self.timeSizeType.current(1)
    elif timeType=='hour':
      self.timeSizeType.current(2)
    self.durationEntry = DecimalEntry(parent, maxDecimals=1, maxValue = 1000, minValue = 0, minIncrement = 0.1,width=10)
    self.durationEntry.set(duration)
    self.removeLineButton = Button(parent,text="-",width=3, command= self.removeLine)
  
  def getLineData(self):
      data = SequenceLineStruct()
      data.voltage = self.getVoltage()
      data.current = self.getCurrent()
      data.duration = self.getDuration()
      data.timeType = self.getTimeType()
  
  def getVoltage(self):
    return self.voltageEntry.get()

  def getCurrent(self):
    return self.currentEntry.get()

  def getTimeType(self):
    return self.timeSizeType_value.get()

  def getDuration(self):
    return self.durationEntry.get()

  def removeLine(self):
    self.removeLineFunc(self.rowNumber,[self.voltageEntry,self.currentEntry,self.timeSizeType,self.durationEntry,self.removeLineButton, self.selectedLabel])  

  