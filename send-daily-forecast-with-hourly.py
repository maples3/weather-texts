#!/usr/bin/python3
from db import dbConnection
from smtp import smtpConnection

dbc = dbConnection('db.sqlite')
serverSettings = dbc.getServerLoginInfo()
smtp = smtpConnection(serverSettings[0], serverSettings[1], serverSettings[2], serverSettings[3])

# According to the Internet, the message must begin with a subject
weathermsg = "Subject: \n"
weathermsg += "Today- " + dbc.getTodayForecast()
weathermsg += "\n\n"
weathermsg += "Hourly forecast-\n" + dbc.getTodayHourly()

# Send the messages
for r in dbc.getRecipients():
	smtp.send(r, weathermsg)

smtp.close()
dbc.close()
