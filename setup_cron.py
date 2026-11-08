import subprocess
# Run daily batch at 2:00 AM IST (20:30 UTC of previous day) with automatic git pull sync
cron_line = "30 20 * * * cd /root/youtube-automation && git pull origin main && /root/youtube-automation/venv/bin/pip install -r requirements.txt && SCHEDULED_PUBLISH=true /root/youtube-automation/venv/bin/python run_daily_batch.py >> /var/log/youtube_automation.log 2>&1\n"
current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
if cron_line.strip() not in current:
    # Remove any old cron jobs for run_daily_batch.py to avoid duplicates
    cleaned_cron = "\n".join([line for line in current.splitlines() if "run_daily_batch.py" not in line])
    new_cron = cleaned_cron + "\n" + cron_line if cleaned_cron else cron_line
    subprocess.run(["crontab", "-"], input=new_cron, text=True)
    print("CRON UPDATED SUCCESSFULLY TO 2:00 AM IST!")
else:
    print("CRON ALREADY EXISTS WITH 2:00 AM IST SCHEDULE!")
