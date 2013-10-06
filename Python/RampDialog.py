from tkinter import *
from tkinter.ttk import *
import tkBaseDialog
from ExtendedEntry import DecimalEntry
from SequenceLine import SequenceLineStruct

class LinearRamp():
  def __init__(self):
    self.startingCurrent = 0
    self.endingCurrent = 0
    self.startingVoltage = 0
    self.endingVoltage = 0
    self.duration = 0
    self.timeType = 'sec'
    self.numSteps = 0

class RampDialog(tkBaseDialog.Dialog):
  def body(self, master):   
    self.addRampGui(master)
    self.okClicked = False

  def addRampGui(self, master):
    Label(master,text="Starting current").grid(row=0,column=0,sticky=E)
    self.startingCurrentEntry = DecimalEntry(master,maxDecimals=0, maxValue = 1000, minValue = 0, minIncrement = 1,width=8,justify=RIGHT)
    self.startingCurrentEntry.grid(row=0,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Ending current").grid(row=1,column=0,sticky=E)
    self.endingCurrentEntry = DecimalEntry(master,maxDecimals=0, maxValue = 1000, minValue = 0, minIncrement = 1,width=8,justify=RIGHT)
    self.endingCurrentEntry.grid(row=1,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Starting voltage").grid(row=2,column=0,sticky=E)
    self.startingVoltageEntry = DecimalEntry(master,maxDecimals=2, maxValue = 20, minValue = 0, minIncrement = 0.01,width=8,justify=RIGHT)
    self.startingVoltageEntry.grid(row=2,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Ending voltage").grid(row=3,column=0,sticky=E)
    self.endingVoltageEntry = DecimalEntry(master,maxDecimals=2, maxValue = 20, minValue = 0, minIncrement = 0.01,width=8,justify=RIGHT)
    self.endingVoltageEntry.grid(row=3,column=1,columnspan=2,sticky=E+W)
    Label(master,text="Time span").grid(row=4,column=0,sticky=E)
    self.timeType_value = StringVar()
    self.timeType = Combobox(master, textvariable=self.timeType_value,state='readonly',width=7)
    self.timeType['values'] = ('sec', 'min', 'hour')
    self.timeType.current(0)
    self.timeType.grid(row=4,column=1,sticky=E+W)
    self.durationEntry = DecimalEntry(master,maxDecimals=1, maxValue = 1000, minValue = 0, minIncrement = 0.1,width=8,justify=RIGHT)
    self.durationEntry.grid(row=4,column=2,sticky=E+W)
    Label(master,text="# steps").grid(row=5,column=0,sticky=E)
    self.numStepsEntry = DecimalEntry(master, maxDecimals=0, maxValue = 1000, minValue = 0, minIncrement = 1,width=8,justify=RIGHT)
    self.numStepsEntry.grid(row=5,column=1,columnspan=2,sticky=E+W)

  def apply(self):
    self.createLinearRamp()
    self.okClicked = True  

  def createLinearRamp(self):
    voltageRamp = LinearRamp()
    voltageRamp.startingCurrent = self.startingCurrentEntry.get()
    voltageRamp.endingCurrent = self.endingCurrentEntry.get()
    voltageRamp.startingVoltage = self.startingVoltageEntry.get()
    voltageRamp.endingVoltage = self.endingVoltageEntry.get()
    voltageRamp.duration = self.durationEntry.get()
    voltageRamp.numSteps = self.numStepsEntry.get()
    voltageRamp.timeType = self.timeType_value.get()
    self.voltageRampLines = self.createLinesFromRamp(voltageRamp)
    self.okClicked = True

  def createLinesFromRamp(self, ramp):
    lines = []
    if ramp.numSteps == 0:
      return lines
    
    timeIncrement = float(ramp.duration)/ramp.numSteps
    voltageIncrement = float(ramp.endingVoltage - ramp.startingVoltage)/(ramp.numSteps - 1)
    currentIncrement = float(ramp.endingCurrent - ramp.startingCurrent)/(ramp.numSteps - 1)
    voltage = ramp.startingVoltage
    current = ramp.startingCurrent
    for i in range(ramp.numSteps):
      line = SequenceLineStruct()
      line.current = current
      line.voltage = voltage
      line.duration = timeIncrement
      line.timeType = ramp.timeType
      lines.append(line)
      voltage += voltageIncrement
      current += currentIncrement
    return lines
