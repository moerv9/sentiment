from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from trade import trade_main
#Method for schedule task execution
# def schedule(self,interval = 20):
#         schedule.every(interval).minutes.do(trade_main)
#         while True:
#             schedule.run_pending()
#             sleep(1)
            
                
sched = BackgroundScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    print(f'Running scheduled job... at {datetime.now()}')
    trade_main()

sched.start()