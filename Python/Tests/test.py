from datetime import datetime
from apscheduler.scheduler import Scheduler

# Start the scheduler
sched = Scheduler()
sched.start()

blabla = 5

def job_function():
  global blabla
  print("Hello World" , blabla)
  blabla += 5

# Schedule job_function to be called every two hours
sched.add_interval_job(job_function, seconds=5)

#sched.shutdown()