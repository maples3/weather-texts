#!/usr/bin/python3
import json
from noaa_sdk import noaa
import datetime
import sqlite3
import os

db = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'db.sqlite'))
n = noaa.NOAA()

### Get the general forecast ###
api_response = n.points_forecast(39.0299125,-84.4598131)

# Note: the generatedAt attribute is in UTC, everything else is local time
forecast_datetime = api_response['properties']['generatedAt'][:-6]

forecasts = api_response['properties']['periods']
# Create a startDate attribute that only has date info (not time)
for f in forecasts:
	f['date'] = f['startTime'][:10]

#print(forecast_datetime)
for f in forecasts:
	c = db.cursor();
	results = c.execute("SELECT ForecastDate, META_DayUpdateDateTime, META_NightUpdateDateTime FROM GeneralForecast WHERE ForecastDate=?", ( f['date'], )).fetchall()
	c.close()
	META_DayUpdateDateTime = '2001-01-01'
	META_NightUpdateDateTime = '2001-01-01'

	if (len(results) == 0):
		c = db.cursor()
		c.execute("INSERT INTO GeneralForecast(ForecastDate) VALUES (?)", ( f['date'], ))
		c.close()
	else:
		META_DayUpdateDateTime = results[0][1]
		META_NightUpdateDateTime = results[0][2]

	if (f['isDaytime'] and META_DayUpdateDateTime < forecast_datetime): # It's a daytime forecast with updated data
		c = db.cursor()
		c.execute("UPDATE GeneralForecast SET HighTemp=?, DayShortForecast=?, DayDetailedForecast=?, META_DayUpdateDateTime=? WHERE ForecastDate=?",
			(f['temperature'], f['shortForecast'], f['detailedForecast'], forecast_datetime, f['date']))
		c.close()
#		print("Updating " + f['date'] + " day")

	if ( (not f['isDaytime']) and META_NightUpdateDateTime < forecast_datetime): # It's a nighttime forecast with updated data
		c = db.cursor()
		c.execute("UPDATE GeneralForecast SET LowTemp=?, NightShortForecast=?, NightDetailedForecast=?, META_NightUpdateDateTime=? WHERE ForecastDate=?",
			(f['temperature'], f['shortForecast'], f['detailedForecast'], forecast_datetime, f['date']))
		c.close()
#		print("Updating " + f['date'] + " night")


### Get the hourly forecast ###
api_response = n.points_forecast(39.0299125,-84.4598131, hourly=True)

# Note: the generatedAt attribute is in UTC, everything else is local time
forecast_datetime = api_response['properties']['generatedAt'][:-6]

forecasts = api_response['properties']['periods']
# Create a dateTime attribute that doesn't include the time zone
for f in forecasts:
	f['dateTime'] = f['startTime'][:-6]

for f in forecasts:
	c = db.cursor();
	results = c.execute("SELECT ForecastDateTime, META_UpdateDateTime FROM HourlyForecast WHERE ForecastDateTime=?", ( f['dateTime'], )).fetchall()
	c.close()
	META_UpdateDateTime = '2001-01-01'

	if (len(results) == 0):
		c = db.cursor()
		c.execute("INSERT INTO HourlyForecast(ForecastDateTime) VALUES (?)", ( f['dateTime'], ))
		c.close()
	else:
		META_UpdateDateTime = results[0][1]

	if (META_UpdateDateTime < forecast_datetime): # It's newer than what's in the DB
		c = db.cursor()
		c.execute("UPDATE HourlyForecast SET Temp=?, ShortForecast=?, META_UpdateDateTime=? WHERE ForecastDateTime=?",
			(f['temperature'], f['shortForecast'], forecast_datetime, f['dateTime']))
		c.close()
		#print("Updated " + f['dateTime'])

db.commit()
db.close()
