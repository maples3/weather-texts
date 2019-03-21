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

# Get today's forecast from the database
today = datetime.date.today().strftime("%Y-%m-%d")
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

weathermsg = "Subject: \n"
### Build today's forecast ###
try:
	c = db.cursor()
	results = c.execute("SELECT DayDetailedForecast FROM GeneralForecast WHERE ForecastDate=?", (today, )).fetchall()
	c.close()
	if not (len(results) == 1):
		raise AssertionError()
	todaycast = "Today- "
	todaycast += results[0][0]
	weathermsg += todaycast
except Exception as e:
	errmsg = 'Weather error! (today)\n' + str(e)
	smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, errmsg)

weathermsg += "\n\n"
### Build the hourly forecast ###
try:
	hourcast = "Hourly forecast-"
	c = db.cursor()
	results = c.execute("SELECT TIME(ForecastDateTime) as ForecastTime, Temp, ShortForecast FROM HourlyForecast WHERE DATE(ForecastDateTime)=? ORDER BY ForecastTime", (today, )).fetchall()
	c.close()

	for row in results:
		if row[0][:2] in ["06", "09", "12", "15", "18"]:
			hourcast += "\n"
			# Print the time
			hourcast += row[0][:5]
			hourcast += "- "
			# Print the temp
			hourcast += str(row[1])
			hourcast += ", "
			# Print the description
			hourcast += row[2]

	weathermsg += hourcast
except Exception as e:
	errmsg = 'Weather error! (hourly)\n' + str(e)
	smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, errmsg)


### Send the message ###
smtpObj.sendmail(SMTP_EMAIL, DEST_ADDR, weathermsg)
#print(weathermsg)

smtpObj.quit()
db.close()

