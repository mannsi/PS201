from tkinter import *
from tkinter.ttk import *
import PsController.Control.Controller
from PsController.UI.Dialogs.AboutDialog import *

class StatusTabFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        fontName = "Verdana"
        fontSize = 12
      
        self.controller = controller
        Label(self, text="Target voltage:",font=(fontName, fontSize)).grid(row=0,column=0,sticky=E)
        self.voltageEntryVar = DoubleVar(None)
        self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.voltageEntry.grid(row=0, column=1)
        Label(self, text="(V):").grid(row=0,column=2,sticky=W)
        Label(self, text="Current limit:",font=(fontName, fontSize)).grid(row=1,column=0,sticky=E)
        self.currentEntryVar = IntVar(None)
        self.currentEntry = Entry(self, textvariable=self.currentEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.currentEntry.grid(row=1, column=1)
        Label(self, text="(mA):").grid(row=1,column=2,sticky=W)
        Label(self, text="Input voltage:",font=(fontName, fontSize)).grid(row=2,column=0,sticky=E)
        self.voltageInputEntryVar = DoubleVar(None)
        self.voltageInputEntry = Entry(self, textvariable=self.voltageInputEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.voltageInputEntry.grid(row=2, column=1)
        Label(self, text="(V):").grid(row=2,column=2,sticky=W)
        Label(self, text="Pre reg voltage:",font=(fontName, fontSize)).grid(row=3,column=0,sticky=E)
        self.preRegVoltageEntryVar = DoubleVar(None)
        self.preRegVoltageEntry = Entry(self, textvariable=self.preRegVoltageEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.preRegVoltageEntry.grid(row=3, column=1)
        Label(self, text="(V):").grid(row=3,column=2,sticky=W)
        self.controller.notifyTargetVoltageUpdate(self.targetVoltageUpdate)
        self.controller.notifyInputVoltageUpdate(self.inputVoltageUpdate)
        self.controller.notifyTargetCurrentUpdate(self.targetCurrentUpdate)
        self.controller.notifyPreRegVoltageUpdate(self.preRegVoltageUpdate)

    def targetVoltageUpdate(self, newTargetVoltage):
        self.voltageEntryVar.set(newTargetVoltage) 

    def inputVoltageUpdate(self, newInputVoltage):
        self.voltageInputEntryVar.set(newInputVoltage)

    def targetCurrentUpdate(self, newTargetCurrent):
        self.currentEntryVar.set(int(newTargetCurrent))

    def preRegVoltageUpdate(self, preRegVoltage):
        self.preRegVoltageEntryVar.set(preRegVoltage)
