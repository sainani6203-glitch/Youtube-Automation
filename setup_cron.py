import subprocess
cron_line = "30 10 * * * cd /root/youtube-automation && /root/youtube-automation/venv/bin/python run_daily_batch.py >> /var/log/youtube_automation.log 2>&1\n"
current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
if cron_line.strip() not in current:
    new_cron = current + cron_line
    subprocess.run(["crontab", "-"], input=new_cron, text=True)
    print("CRON INSTALLED SUCCESSFULLY!")
else:
    print("CRON ALREADY EXISTS!")
