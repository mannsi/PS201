from tkinter import *
from tkinter.ttk import *
import tkBaseDialog


# Move this someplace else
class ScheduleLineStruct():
  def __init__(self):
    self.voltage = 0
    self.current = 0
    self.duration = 0
    self.timeType = 'sec'

class VoltageRamp():
  def __init__(self):
    self.current = 0
    self.startingVoltage = 0
    self.endingVoltage = 5
    self.duration = 10
    self.timeType = 'sec'
    self.numSteps = 1

class CurrentRamp():
  def __init__(self):
    self.voltage = 0
    self.startingCurrent = 0
    self.endingCurrent = 5
    self.duration = 10
    self.timeType = 'sec'
    self.numSteps = 1

class RampDialog(tkBaseDialog.Dialog):
  def body(self, master):   
    if self.type == "VoltageRamp":
        self.addVoltageRampGui(master)
    elif self.type == "CurrentRamp":
        self.addCurrentRampGui(master)
    Label(master,text="Time span").grid(row=3,column=0,sticky=E)
    self.timeType_value = StringVar()
    self.timeType = Combobox(master, textvariable=self.timeType_value,state='readonly',width=7)
    self.timeType['values'] = ('sec', 'min', 'hour')
    self.timeType.current(0)
    self.timeType.grid(row=3,column=1,sticky=E+W)
    self.durationEntryVar = DoubleVar(None)
    Entry(master, textvariable=self.durationEntryVar,width=10).grid(row=3,column=2,sticky=E+W)
    Label(master,text="# steps").grid(row=4,column=0,sticky=E)
    self.numStepsEntryVar = IntVar(None)
    Entry(master, textvariable=self.numStepsEntryVar,width=10).grid(row=4,column=1,columnspan=2,sticky=E+W)
    self.okClicked = False

  def addVoltageRampGui(self, master):
    Label(master,text="Current").grid(row=0,column=0,sticky=E)
    self.currentEntryVar = IntVar(None)
    Entry(master, textvariable=self.currentEntryVar,width=10).grid(row=0,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Starting voltage").grid(row=1,column=0,sticky=E)
    self.startingVoltageEntryVar = DoubleVar(None)
    Entry(master, textvariable=self.startingVoltageEntryVar,width=10).grid(row=1,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Ending voltage").grid(row=2,column=0,sticky=E)
    self.endingVoltageEntryVar = DoubleVar(None)
    Entry(master, textvariable=self.endingVoltageEntryVar,width=10).grid(row=2,column=1,columnspan=2,sticky=E+W)

  def addCurrentRampGui(self, master):
    Label(master,text="Voltage").grid(row=0,column=0,sticky=E)
    self.voltageEntryVar = IntVar(None)
    Entry(master, textvariable=self.voltageEntryVar,width=10).grid(row=0,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Starting current").grid(row=1,column=0,sticky=E)
    self.startingCurrentEntryVar = DoubleVar(None)
    Entry(master, textvariable=self.startingCurrentEntryVar,width=10).grid(row=1,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Ending current").grid(row=2,column=0,sticky=E)
    self.endingCurrentEntryVar = DoubleVar(None)
    Entry(master, textvariable=self.endingCurrentEntryVar,width=10).grid(row=2,column=1,columnspan=2,sticky=E+W)

  def apply(self):
    if self.type == "VoltageRamp":
        self.createVoltageRamp()
    elif self.type == "CurrentRamp":
        self.createCurrentRamp()  
    self.okClicked = True  

  def createVoltageRamp(self):
    voltageRamp = VoltageRamp()
    voltageRamp.current = self.currentEntryVar.get()
    voltageRamp.startingVoltage = self.startingVoltageEntryVar.get()
    voltageRamp.endingVoltage = self.endingVoltageEntryVar.get()
    voltageRamp.duration = self.durationEntryVar.get()
    voltageRamp.numSteps = self.numStepsEntryVar.get()
    voltageRamp.timeType = self.timeType_value.get()
    self.voltageRampLines = self.createLinesFromVoltageRamp(voltageRamp)
    self.okClicked = True
    
  def createCurrentRamp(self):
    voltageRamp = CurrentRamp()
    voltageRamp.voltage = self.voltageEntryVar.get()
    voltageRamp.startingCurrent = self.startingCurrentEntryVar.get()
    voltageRamp.endingCurrent = self.endingCurrentEntryVar.get()
    voltageRamp.duration = self.durationEntryVar.get()
    voltageRamp.numSteps = self.numStepsEntryVar.get()
    voltageRamp.timeType = self.timeType_value.get()
    self.currentRampLines = self.createLinesFromCurrentRamp(voltageRamp)

  def createLinesFromVoltageRamp(self, voltageRamp):
    lines = []
    timeIncrement = float(voltageRamp.duration)/voltageRamp.numSteps
    voltageIncrement = float(voltageRamp.endingVoltage - voltageRamp.startingVoltage)/(voltageRamp.numSteps - 1)
    currentVoltage = voltageRamp.startingVoltage
    for i in range(voltageRamp.numSteps):
      line = ScheduleLineStruct()
      line.current = voltageRamp.current
      line.voltage = currentVoltage
      line.duration = timeIncrement
      line.timeType = voltageRamp.timeType
      lines.append(line)

      currentVoltage += voltageIncrement
    return lines

  def createLinesFromCurrentRamp(self, currentRamp):
    lines = []
    timeIncrement = float(currentRamp.duration)/currentRamp.numSteps
    currentIncrement = float(currentRamp.endingCurrent - currentRamp.startingCurrent)/(currentRamp.numSteps - 1)
    current = currentRamp.startingCurrent
    for i in range(currentRamp.numSteps):
      line = ScheduleLineStruct()
      line.voltage = currentRamp.voltage
      line.current = current
      line.duration = timeIncrement
      line.timeType = currentRamp.timeType
      lines.append(line)

      current += currentIncrement
    return lines
