import subprocess
# Run daily batch at 4:00 AM IST (22:30 UTC of previous day)
cron_line = "30 22 * * * cd /root/youtube-automation && /root/youtube-automation/venv/bin/python run_daily_batch.py >> /var/log/youtube_automation.log 2>&1\n"
current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
if cron_line.strip() not in current:
    # Remove any old cron jobs for run_daily_batch.py to avoid duplicates
    cleaned_cron = "\n".join([line for line in current.splitlines() if "run_daily_batch.py" not in line])
    new_cron = cleaned_cron + "\n" + cron_line if cleaned_cron else cron_line
    subprocess.run(["crontab", "-"], input=new_cron, text=True)
    print("CRON UPDATED SUCCESSFULLY TO 4:00 AM IST!")
else:
    print("CRON ALREADY EXISTS WITH 4:00 AM IST SCHEDULE!")
