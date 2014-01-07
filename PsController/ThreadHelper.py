from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler

class ThreadHelper():
    def runThreadedJob(self, function, args):
        self.threadedScheduler = Scheduler()
        self.threadedScheduler.start()
        self.threadedScheduler.add_date_job(function, datetime.now() + timedelta(seconds=0.5), args)

    def runIntervalJob(self, function, interval, args=None):
        self.intervalScheduler = Scheduler()
        self.intervalScheduler.start()
        self.intervalScheduler.add_interval_job(function, seconds=interval, args = args)

    def runDelayedJob(self, function, firingTime, args):
        self.delayedScheduler = Scheduler()
        self.delayedScheduler.start()
        self.delayedScheduler.add_date_job(function, firingTime, args)
    
    def runSchedule(self, listOfFunctions, listOfFiringTimes, listOfArgs, useLoggingTimeInterval, loggingTimeInterval, filePath, fileLoggingFunction): 
        self.scheduleScheduler = Scheduler()
        self.scheduleScheduler.start()
        for function, firingTime, args in zip(listOfFunctions, listOfFiringTimes, listOfArgs):
            self.scheduleScheduler.add_date_job(function, firingTime, args)   
        if useLoggingTimeInterval:
            self.runIntervalJob(fileLoggingFunction, loggingTimeInterval, [filePath])
      
    def stopSchedule(self):
        self.scheduleScheduler.shutdown()
      

  