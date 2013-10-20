from tkinter import *
from tkinter.ttk import *
import tkBaseDialog
from tkinter import filedialog
from ExtendedEntry import DecimalEntry
from SequenceLine import SequenceLineStruct
import os

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

class DataLoggingDialog(tkBaseDialog.Dialog):
  def body(self, master):   
    self.createGui(master)
    self.okClicked = False
    self.logWhenValuesChange = False
    self.logEveryXSeconds = False

  def createGui(self, master):
    Label(master,text="File name").grid(row=0,column=0)
    self.filePathVar = StringVar(None)
    self.filePathEntry = Entry(master,textvariable = self.filePathVar)
    self.filePathEntry.grid(row=0,column=1, sticky=W+E)   
    Button(master,text="Browse",command=self.browse).grid(row=0,column=2)
    Label(master,text="Log when:").grid(row=1,column=0)
    self.radioVar = IntVar()
    subFrame1 = Frame(master)
    Radiobutton(subFrame1, text="Values change",variable=self.radioVar, value=1,command=self.ValuesChangedSelected).pack(side=LEFT)
    subFrame1.grid(row=1,column=1,sticky=W)
    subFrame2 = Frame(master)
    Radiobutton(subFrame2,text="Every", variable=self.radioVar, value=2,command=self.TimeIntervalSelected).pack(side=LEFT)
    self.intervalEntry = DecimalEntry(subFrame2,maxDecimals=0, maxValue = 1000, minValue = 0, minIncrement = 1,width=10,justify=RIGHT,state=DISABLED)
    self.intervalEntry.pack(side=LEFT)
    Label(subFrame2,text="seconds").pack(side=LEFT)
    subFrame2.grid(row=2,column=1,sticky=W)
    self.radioVar.set(1)
    
    
  def ValuesChangedSelected(self):
    self.intervalEntry.configure(state = DISABLED)
    
  def TimeIntervalSelected(self):
    self.intervalEntry.configure(state = NORMAL)  

  def apply(self):
    self.filePath = self.filePathVar.get()
    self.initializeFile(self.filePath)
    self.logWhenValuesChange = self.radioVar.get() is 1
    self.logEveryXSeconds = not self.logWhenValuesChange  
    if self.logEveryXSeconds:
      self.timeInterval = self.intervalEntry.get()
    self.okClicked = True 
    
  def browse(self):
    file = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    self.filePathVar.set(file.name)
    file.close()
    
  def initializeFile(self, filePath):
    if not os.path.isfile(filePath):
      with open(filePath, "a") as myfile:
        fileString = "DateTime\tVoltage\tCurrent\n"
        myfile.write(fileString)
      
