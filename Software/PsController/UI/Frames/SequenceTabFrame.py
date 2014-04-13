from tkinter import *
from tkinter.ttk import *
import PsController.Control.Controller
from PsController.UI.Dialogs.AboutDialog import *
from PsController.UI.Dialogs.RampDialog import RampDialog
from PsController.UI.Dialogs.DataLoggingDialog import DataLoggingDialog
from PsController.UI.Frames.SequenceLineFrame import SequenceLineFrame

class SequenceTabFrame(Frame):
    def __init__(self, parent, resetTabM, connected, controller):
        Frame.__init__(self,parent)
        self.parent = parent
        self.resetTabM = resetTabM
        self.controller = controller
        self.initalizeView(connected)
        controller.notifyScheduleDoneUpdate(self.sequenceDone) 
        controller.notifyScheduleLineUpdate(self.sequenceLineChanged)
        controller.notifyConnectedUpdate(self.connectedChanged)
    
    def initalizeView(self, connected):
        self.addLinesFrame()
        buttonFrame = Frame(self)
        self.btnAdd = Button(buttonFrame, text = "Add line", command=self.addLine)
        self.btnAdd.pack(side=LEFT)
        self.btnClearLines = Button(buttonFrame, text = "Clear", command=self.resetLines)
        self.btnClearLines.pack(side=LEFT)
        
        self.btnLinearRamping = Button(buttonFrame, text = "Linear ramping", command=self.linearRamping)
        self.btnLinearRamping.pack(side=LEFT)
        
        self.logToFileVar = IntVar(value=0)
        self.chkLogToFile = Checkbutton(buttonFrame, text = "Log to file", variable = self.logToFileVar)
        self.chkLogToFile.pack(side=LEFT)
        
        if connected:
            startButtonState = NORMAL
        else:
            startButtonState = DISABLED
        self.btnStop = Button(buttonFrame, text = "Stop", state=DISABLED, command=self.stop)
        self.btnStop.pack(side=RIGHT)
        self.btnStart = Button(buttonFrame, text = "Start", state=startButtonState, command=self.start)
        self.btnStart.pack(side=RIGHT)
        buttonFrame.pack(fill='x')
     
    def selectLine(self, rowNumber):
        self.sequenceLineFrame.selectLine(rowNumber)  
      
    def start(self):
        scheduleStarted = False
        if self.logToFileVar.get():
            dialog = DataLoggingDialog(self,title="Log to file")
            if dialog.okClicked:
                if dialog.logWhenValuesChange:
                    if dialog.filePath is not "":
                        scheduleStarted = self.controller.startSchedule(self.sequenceLineFrame.getLines(),
                                                                    startingTargetVoltage = self.controller.currentValues.targetVoltage,
                                                                    startingTargetCurrent = self.controller.currentValues.targetCurrent, 
                                                                    startingOutputOn = self.controller.currentValues.outputOn,
                                                                    logWhenValuesChange=True,
                                                                    filePath=dialog.filePath)
                elif dialog.logEveryXSeconds:
                    if dialog.timeInterval:
                        scheduleStarted = self.controller.startSchedule(self.sequenceLineFrame.getLines(),
                                                                     useLoggingTimeInterval=True,
                                                                     startingTargetVoltage = self.controller.currentValues.targetVoltage,
                                                                     startingTargetCurrent = self.controller.currentValues.targetCurrent, 
                                                                     startingOutputOn = self.controller.currentValues.outputOn,
                                                                     loggingTimeInterval=dialog.timeInterval,
                                                                     filePath=dialog.filePath)
        else:       
            scheduleStarted = self.controller.startSchedule(self.sequenceLineFrame.getLines(),
                                                         startingTargetVoltage = self.controller.currentValues.targetVoltage,
                                                         startingTargetCurrent = self.controller.currentValues.targetCurrent, 
                                                         startingOutputOn = self.controller.currentValues.outputOn)
        if (scheduleStarted):
            self.btnStop.configure(state = NORMAL)
            self.btnStart.configure(state = DISABLED)
            self.btnClearLines.configure(state = DISABLED)
            self.btnAdd.configure(state = DISABLED)
            self.btnLinearRamping.configure(state = DISABLED)
            self.chkLogToFile.configure(state = DISABLED)
        
    def stop(self):
        self.controller.stopSchedule()
         
    def scheduleStopped(self):  
        self.btnStart.configure(state = NORMAL)
        self.btnClearLines.configure(state = NORMAL)
        self.btnAdd.configure(state = NORMAL)
        self.btnLinearRamping.configure(state = NORMAL)
        self.chkLogToFile.configure(state = NORMAL)
        self.btnStop.configure(state = DISABLED)
      
    def addLine(self):
        self.sequenceLineFrame.addLine()
    
    def addLinesFrame(self):
        canvas = Canvas(self,height=100,highlightthickness=0)
        self.sequenceLineFrame = SequenceLineFrame(canvas)
    
    def resetLines(self):
        self.resetTabM(self.controller.connected)
    
    def linearRamping(self):
        dialog = RampDialog(self,title="Voltage ramp")
        if dialog.okClicked:
            for l in dialog.voltageRampLines:
                self.sequenceLineFrame.addLine(l.voltage,l.current,l.timeType,l.duration)

    def sequenceDone(self, args):
        self.selectLine(-1)  
        self.scheduleStopped()

    def sequenceLineChanged(self, rowNumber):
        self.selectLine(rowNumber)  

    def connectedChanged(self, value):
        connected = value[0]
        if connected:
            state = NORMAL
        else:
            state = DISABLED
        self.btnStart.configure(state=state)
