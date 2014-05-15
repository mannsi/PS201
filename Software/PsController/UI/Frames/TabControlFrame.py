from tkinter.ttk import *
from .StatusTabFrame import StatusTabFrame
from .SequenceTabFrame import SequenceTabFrame


class TabControl(Notebook):
    """ The tab control on the lower part of the PsController """
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        Notebook.__init__(self, parent, name='tab control')

        self.statusTab = StatusTabFrame(self, self.controller)
        self.sequenceTab = SequenceTabFrame(self, self.resetSequenceTab, controller)

        self.add(self.statusTab, text='Status')
        self.add(self.sequenceTab, text='Sequence')

    def resetSequenceTab(self):
        self.forget(self.sequenceTab)
        self.sequenceTab = SequenceTabFrame(self, self.resetSequenceTab, self.controller)
        self.add(self.sequenceTab, text='Sequence')
        self.select(self.sequenceTab)

