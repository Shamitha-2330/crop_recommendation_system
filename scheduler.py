# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess, sys, os
from config import CURRENT_INTERVAL_HOURS, HISTORY_DAILY_TIME

BASE = os.path.dirname(os.path.abspath(__file__))
PROD_HISTORY = os.path.join(BASE, "producer_history.py")
PROD_CURRENT = os.path.join(BASE, "producer_current.py")
RECO = os.path.join(BASE, "recommendation_engine.py")

def run_script(path):
    print("Running", path)
    try:
        r = subprocess.run([sys.executable, path], capture_output=True, text=True)
        print(r.stdout)
        if r.stderr:
            print("ERR:", r.stderr)
    except Exception as e:
        print("Failed to run", path, e)

hh, mm = HISTORY_DAILY_TIME.split(":")
scheduler = BlockingScheduler(job_defaults={'coalesce': True, 'max_instances': 1})

# run current every hour
scheduler.add_job(lambda: run_script(PROD_CURRENT), 'interval', hours=CURRENT_INTERVAL_HOURS, id='current_job')

# run history daily at hh:mm
scheduler.add_job(lambda: run_script(PROD_HISTORY), 'cron', hour=int(hh), minute=int(mm), id='history_job')

# optionally run recommendation engine 10 minutes after current job: schedule offset or add separate job
# Here we run RECO every hour, 10 minutes after current producer by waiting inside job is not ideal
# Instead run RECO every hour as well (can be tuned)
scheduler.add_job(lambda: run_script(RECO), 'interval', hours=CURRENT_INTERVAL_HOURS, id='reco_job', next_run_time=None)

# initial run of current (so we get current data immediately)
print("Initial run of current producer...")
run_script(PROD_CURRENT)
print("Starting scheduler...")
scheduler.start()
