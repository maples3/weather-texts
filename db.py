#!/usr/bin/python3
import sqlite3
import os
import datetime

### Time helper methods
def getTodayString():
	return datetime.date.today().strftime("%Y-%m-%d")

def getTomorrowString():
	return (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

class dbConnection:
	def __init__(self, dbfilename):
		self.db = sqlite3.connect(os.path.join(os.path.dirname(__file__), dbfilename))

	def getServerLoginInfo(self):
		c = self.db.cursor()
		results = c.execute("SELECT Server, Port, Email, Password FROM SmtpSettings").fetchall()
		c.close()
		return results[0]

	# Returns a string with the detailed forecast
	def getTodayForecast(self):
		c = self.db.cursor()
		results = c.execute("SELECT DayDetailedForecast FROM GeneralForecast WHERE ForecastDate=?", (getTodayString(), )).fetchall()
		c.close()
		if not (len(results) == 1):
			raise AssertionError()
		return results[0][0]

	def getTonightForecast(self):
		c = self.db.cursor()
		results = c.execute("SELECT NightDetailedForecast FROM GeneralForecast WHERE ForecastDate=?", (getTodayString(), )).fetchall()
		c.close()
		if not (len(results) == 1):
			raise AssertionError()
		return results[0][0]

	# Returns a string with the detailed forecast
	def getTomorrowForecast(self):
		c = self.db.cursor()
		results = c.execute("SELECT DayDetailedForecast FROM GeneralForecast WHERE ForecastDate=?", (getTomorrowString(), )).fetchall()
		c.close()
		if not (len(results) == 1):
			raise AssertionError()
		return results[0][0]

	# Returns an array of tuples: (time string, temperature, short description)
	def getTodayHourlyList(self):
		c = self.db.cursor()
		results = c.execute("SELECT strftime('%H:%M', ForecastDateTime) as ForecastTime, Temp, ShortForecast FROM HourlyForecast WHERE DATE(ForecastDateTime)=? ORDER BY ForecastTime", (getTodayString(), )).fetchall()
		c.close()
		return results

	def getTodayHourly(self):
		hourcast = ""
		for row in self.getTodayHourlyList():
			if row[0][:2] in ["06", "09", "12", "15", "18"]:
				# Print the time
				hourcast += row[0]
				hourcast += "- "
				# Print the temp
				hourcast += str(row[1])
				hourcast += ", "
				# Print the description
				hourcast += row[2]
				hourcast += "\n"
		return hourcast[:-1]

	# Returns a list of recipients
	def getRecipients(self):
		c = self.db.cursor()
		results = c.execute("SELECT EmailAddress FROM Recipients").fetchall()
		c.close()

		# Convert the list of tuples to a basic list
		recipients = list()
		for row in results:
			recipients.append(results[0])

		return recipients

	def close(self):
		self.db.close()

