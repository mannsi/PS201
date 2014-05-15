from tkinter import *
from tkinter.ttk import *
from PsController.UI.Controls.SequenceLine import SequenceLine


class SequenceLineFrame(Frame):
    """Displays a list of SequenceLine objects"""
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = parent
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self, anchor="nw", tags="self")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.bind("<Configure>", self.OnFrameConfigure)
        self.headerLabelVoltage = Label(self, text="Voltage(V)")
        self.scrollbarActive = False
        self.initializingView = True
        self.gridNumber = 0
        self.lines = []
        self.rowNumber = 0
        self.addHeaderLine()
        self.addLine()
        self.initializingView = False
        self.verticalScrollBar = None

    def _on_mousewheel(self, event):
        if self.scrollbarActive:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def checkIfAddScrollbar(self):
        if not self.scrollbarActive and not self.initializingView:
            widgetsHeight = self.getWidgetsHeight()
            totalHeight = self.canvas.winfo_height()
            return widgetsHeight > totalHeight

    def checkIfRemoveScrollbar(self):
        if self.scrollbarActive:
            widgetsHeight = self.getWidgetsHeight()
            totalHeight = self.canvas.winfo_height()
            return widgetsHeight <= totalHeight

    def addScrollbar(self):
        self.verticalScrollBar = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.verticalScrollBar.set)
        self.verticalScrollBar.pack(side="right", fill="y")
        self.scrollbarActive = True

    def removeScrollbar(self):
        self.verticalScrollBar.pack_forget()
        self.scrollbarActive = False

    def getWidgetsHeight(self):
        self.update_idletasks()
        widgetsHeight = self.headerLabelVoltage.winfo_height()
        for line in self.lines:
            if line:
                widgetsHeight += line.removeLineButton.winfo_height()
        return widgetsHeight

    def addHeaderLine(self):
        self.headerLabelVoltage.grid(row=0, column=1, sticky=W)
        Label(self, text="Current(mA)").grid(row=0, column=2, sticky=W)
        Label(self, text="Duration").grid(row=0, column=3, columnspan=2)

    def addLine(self, voltage=None, current=None, timeType=None, duration=None):
        if voltage is not None and current is not None and timeType is not None and duration is not None:
            line = SequenceLine(self, self.rowNumber, self.removeLine, voltage=voltage, current=current,
                                timeType=timeType, duration=duration)
        elif self.rowNumber == 0:
            line = SequenceLine(self, self.rowNumber, self.removeLine)
        else:
            prevLine = self.lines[self.rowNumber - 1]
            line = SequenceLine(self, self.rowNumber, self.removeLine, voltage=prevLine.getVoltage(),
                                current=prevLine.getCurrent(), timeType=prevLine.getTimeType(),
                                duration=prevLine.getDuration())
        self.gridNumber += 1
        line.selectedLabel.grid(row=self.gridNumber, column=0)
        line.voltageEntry.grid(row=self.gridNumber, column=1)
        line.currentEntry.grid(row=self.gridNumber, column=2)
        line.timeSizeType.grid(row=self.gridNumber, column=3)
        line.durationEntry.grid(row=self.gridNumber, column=4)
        line.removeLineButton.grid(row=self.gridNumber, column=5)
        self.lines.append(line)
        self.rowNumber += 1
        self.canvas.update_idletasks()
        if self.checkIfAddScrollbar():
            self.addScrollbar()

    def removeLine(self, rowNumber, widgetsToRemove):
        for widget in widgetsToRemove:
            widget.grid_remove()
        for i in range(rowNumber + 1, len(self.lines)):
            self.lines[i].rowNumber -= 1
        self.lines.pop(rowNumber)
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

    def selectLine(self, rowNumber):
        for line in self.lines:
            if line.rowNumber == rowNumber:
                line.labelText.set("->")
            else:
                line.labelText.set("     ")

    def OnFrameConfigure(self, event):
        self.canvas.configure(scrollregion=(0, 0, 0, self.getWidgetsHeight()))
