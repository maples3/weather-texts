#!/usr/bin/python3
import smtplib

class smtpConnection:
	def __init__(self, server, port, email, password):
		self.email = email
		self.smtpObj = smtplib.SMTP(server, port)
		self.smtpObj.ehlo()
		self.smtpObj.starttls()
		self.smtpObj.login(self.email, password)

	def send(self, destination, message):
		self.smtpObj.sendmail(self.email, destination, message)

	def close(self):
		self.smtpObj.quit()
