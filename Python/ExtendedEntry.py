from tkinter import *
from tkinter.ttk import *

class ExtendedDoubleVar(DoubleVar):
    def __init__(self):
        DoubleVar.__init__(None)
    def get(self):
        try:
            val = super.get()
            return val
        except:
            return 0

class DecimalEntry(Entry):
    def __init__(self, master, maxDecimals, maxValue, minValue, minIncrement, *args, **kwargs):
        self.minValue = minValue
        self.minIncrement = minIncrement
        self.maxValue = maxValue
        self.maxDecimals = maxDecimals
        
        if self.maxDecimals > 0:
            self.textVar = DoubleVar(None)
        else:
            self.textVar = IntVar(None)
        
        self.textVar.set(self.VerifyInitialValue(self.textVar.get()))
        vcmd = (master.register(self.OnValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        Entry.__init__(self, master, validate="key", validatecommand=vcmd, textvariable=self.textVar, *args, **kwargs)
        
    def get(self):
        try:
            val = self.textVar.get()
            return val
        except:
            return 0    
        
    def set(self, value):
        self.textVar.set(self.VerifyInitialValue(value))    
                  
    def VerifyInitialValue(self,initialValue):
        if initialValue > self.maxValue:
            return self.maxValue
        if initialValue < self.minValue:
            return self.minValue
        if not self.ValidNumberOfDecimals(str(initialValue)):
            return round(initialValue, self.maxDecimals)
        return initialValue
    
    def OnValidate(self, d, i, P, s, S, v, V, W):
        #print("OnValidate:")
        #print("d='%s'" % d)
        #print("i='%s'" % i)
        #print("P='%s'" % P)
        #print("s='%s'" % s)
        #print("S='%s'" % S)
        #print("v='%s'" % v)
        #print("V='%s'" % V)
        #print("W='%s'" % W)

        if P == "":
            return True

        if S == "." and self.maxDecimals == 0:
            return False

        if S not in ".,0123456789":
            return False
        
        try:
            float(P)
        except ValueError:
            return False
        
        return self.VerifyNumericInput(P)
    
    def VerifyNumericInput(self, numberString):
        if float(numberString) > self.maxValue:
            return False
        
        if float(numberString) < self.minValue:
            return False
        
        return self.ValidNumberOfDecimals(numberString)     
  
    def ValidNumberOfDecimals(self, numberString):
        if "." in numberString:
            numberOfDecimals = len(numberString.split(".")[-1])
            return numberOfDecimals <= self.maxDecimals
        return True   