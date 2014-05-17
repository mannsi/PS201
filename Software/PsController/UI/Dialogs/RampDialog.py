from tkinter import *
from tkinter.ttk import *

from PsController.UI.DataObjects.SequenceLineData import SequenceLineData
from .tkBaseDialog import Dialog
from ..Controls.DecimalEntry import DecimalEntry


class RampDialog(Dialog):
    def __init__(self, parent, title):
        self.okClicked = False
        self.startingCurrentEntry = None
        self.endingCurrentEntry = None
        self.startingVoltageEntry = None
        self.endingVoltageEntry = None
        self.timeType_value = StringVar()
        self.timeType = None
        self.durationEntry = None
        self.numStepsEntry = None
        self.voltageRampLines = []
        super(RampDialog, self).__init__(parent, title, True)

    def body(self, master):
        self.addRampGui(master)
        return self.startingCurrentEntry

    def addRampGui(self, master):
        Label(master, text="Starting current").grid(row=0, column=0, sticky=E)
        self.startingCurrentEntry = DecimalEntry(master, maxDecimals=0, maxValue=1000, minValue=0, minIncrement=1,
                                                 width=8, justify=RIGHT)
        self.startingCurrentEntry.grid(row=0, column=1, columnspan=2, sticky=E + W)
        Label(master, text="Ending current").grid(row=1, column=0, sticky=E)
        self.endingCurrentEntry = DecimalEntry(master, maxDecimals=0, maxValue=1000, minValue=0, minIncrement=1,
                                               width=8, justify=RIGHT)
        self.endingCurrentEntry.grid(row=1, column=1, columnspan=2, sticky=E + W)
        Label(master, text="Starting voltage").grid(row=2, column=0, sticky=E)
        self.startingVoltageEntry = DecimalEntry(master, maxDecimals=2, maxValue=20, minValue=0, minIncrement=0.01,
                                                 width=8, justify=RIGHT)
        self.startingVoltageEntry.grid(row=2, column=1, columnspan=2, sticky=E + W)
        Label(master, text="Ending voltage").grid(row=3, column=0, sticky=E)
        self.endingVoltageEntry = DecimalEntry(master, maxDecimals=2, maxValue=20, minValue=0, minIncrement=0.01,
                                               width=8, justify=RIGHT)
        self.endingVoltageEntry.grid(row=3, column=1, columnspan=2, sticky=E + W)
        Label(master, text="Time span").grid(row=4, column=0, sticky=E)

        self.timeType = Combobox(master, textvariable=self.timeType_value, state='readonly', width=7)
        self.timeType['values'] = ('sec', 'min', 'hour')
        self.timeType.current(0)
        self.timeType.grid(row=4, column=1, sticky=E + W)
        self.durationEntry = DecimalEntry(master, maxDecimals=1, maxValue=1000, minValue=0, minIncrement=0.1, width=8,
                                          justify=RIGHT)
        self.durationEntry.grid(row=4, column=2, sticky=E + W)
        Label(master, text="# steps").grid(row=5, column=0, sticky=E)
        self.numStepsEntry = DecimalEntry(master, maxDecimals=0, maxValue=1000, minValue=0, minIncrement=1, width=8,
                                          justify=RIGHT)
        self.numStepsEntry.grid(row=5, column=1, columnspan=2, sticky=E + W)

    def apply(self):
        self.createLinearRamp()
        self.okClicked = True

    def createLinearRamp(self):
        linearRamp = _LinearRampData()
        linearRamp.startingCurrent = self.startingCurrentEntry.get()
        linearRamp.endingCurrent = self.endingCurrentEntry.get()
        linearRamp.startingVoltage = self.startingVoltageEntry.get()
        linearRamp.endingVoltage = self.endingVoltageEntry.get()
        linearRamp.duration = self.durationEntry.get()
        linearRamp.numSteps = self.numStepsEntry.get()
        linearRamp.timeType = self.timeType_value.get()
        self.voltageRampLines = self.createLinesFromRamp(linearRamp)
        self.okClicked = True

    @staticmethod
    def createLinesFromRamp(ramp):
        lines = []
        if ramp.numSteps == 0:
            return lines

        timeIncrement = float(ramp.duration) / ramp.numSteps
        voltageIncrement = float(ramp.endingVoltage - ramp.startingVoltage) / (ramp.numSteps - 1)
        currentIncrement = float(ramp.endingCurrent - ramp.startingCurrent) / (ramp.numSteps - 1)
        voltage = ramp.startingVoltage
        current = ramp.startingCurrent
        for i in range(ramp.numSteps):
            line = SequenceLineData()
            line.current = int(10 * round(current / 10))
            line.voltage = round(voltage, 1)
            line.duration = timeIncrement
            line.timeType = ramp.timeType
            lines.append(line)
            voltage += voltageIncrement
            current += currentIncrement
        return lines


class _LinearRampData():
    def __init__(self):
        self.startingCurrent = 0
        self.endingCurrent = 0
        self.startingVoltage = 0
        self.endingVoltage = 0
        self.duration = 0
        self.timeType = 'sec'
        self.numSteps = 0