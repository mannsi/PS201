import os
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from .tkBaseDialog import Dialog
from PsController.UI.Controls.DecimalEntry import DecimalEntry

class DataLoggingDialog(Dialog):
    def body(self, master):   
        self.createGui(master)
        self.okClicked = False
        self.logWhenValuesChange = False
        self.logEveryXSeconds = False
        return self.filePathEntry
    
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
      
