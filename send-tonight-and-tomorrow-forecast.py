#!/usr/bin/python3
import sys
import os
import datetime
import sqlite3
import smtplib

db = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'db.sqlite'))

smtpObj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login(SMTP_EMAIL, SMTP_PASSWORD)
#smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, 'Test from Python!')

# Get today's forecast from the database
today = datetime.date.today().strftime("%Y-%m-%d")
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

weathermsg = "Subject: \n"
### Build this evening's forecast ###
try:
	c = db.cursor()
	results = c.execute("SELECT NightDetailedForecast FROM GeneralForecast WHERE ForecastDate=?", (today, )).fetchall()
	c.close()
	if not (len(results) == 1):
		raise AssertionError()
	tonightcast = "Tonight- "
	tonightcast += results[0][0]
	weathermsg += tonightcast
except Exception as e:
	errmsg = 'Weather error! (today)\n' + str(e)
	smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, errmsg)

weathermsg += "\n"
### Build tomorrow's forecast ###
try:
	c = db.cursor()
	results = c.execute("SELECT DayDetailedForecast FROM GeneralForecast WHERE ForecastDate=?", (tomorrow, )).fetchall()
	c.close()
	if not (len(results) == 1):
		raise AssertionError()
	tomorrowcast = "Tomorrow-"
	tomorrowcast += results[0][0]
	weathermsg += tomorrowcast
except Exception as e:
	errmsg = 'Weather error! (tomorrow)\n'  + str(e)
	smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, errmsg)

### Send the message ###
smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, weathermsg)
#print(weathermsg)

smtpObj.quit()
db.close()
