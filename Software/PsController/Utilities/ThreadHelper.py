from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler

class ThreadHelper():
    def runThreadedJob(self, function, args):
        threadedScheduler = Scheduler()
        threadedScheduler.start()
        threadedScheduler.add_date_job(function, datetime.now() + timedelta(seconds=0.5), args)

    def runIntervalJob(self, function, interval, args=None):
        intervalScheduler = Scheduler()
        intervalScheduler.start()
        intervalScheduler.add_interval_job(function, seconds=interval, args = args)
        return intervalScheduler

    def runDelayedJob(self, function, firingTime, args):
        delayedScheduler = Scheduler()
        delayedScheduler.start()
        delayedScheduler.add_date_job(function, firingTime, args)
    
    def runSchedule(self, listOfFunctions, listOfFiringTimes, listOfArgs, useLoggingTimeInterval, loggingTimeInterval, filePath, fileLoggingFunction): 
        self.scheduleScheduler = Scheduler()
        self.scheduleScheduler.start()
        for function, firingTime, args in zip(listOfFunctions, listOfFiringTimes, listOfArgs):
            self.scheduleScheduler.add_date_job(function, firingTime, args)   
        if useLoggingTimeInterval:
            self.runIntervalJob(fileLoggingFunction, loggingTimeInterval, [filePath])
      
    def stopSchedule(self):
        self.scheduleScheduler.shutdown(wait = False)
      

  