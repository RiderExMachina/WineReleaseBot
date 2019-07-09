#!/usr/bin/env python3

from bs4 import BeautifulSoup as bsoup
import requests, re, time, os, tweepy

settingsConf = "settings.conf"
stable = "0"
devel = "0"

with open("auth.cred", "r") as authFile:
	authCred = authFile.readlines()
	
	CONSUMER_KEY = authCred[0].split(" ")[-1].strip("\n")
	CONSUMER_SECRET = authCred[1].split(" ")[-1].strip("\n")
	ACCESS_KEY = authCred[2].split(" ")[-1].strip("\n")
	ACCESS_SECRET = authCred[3].split(" ")[-1].strip("\n")

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
	api = tweepy.API(auth)

def versionCheck():
	global stable, devel
	if os.path.isfile(settingsConf):
		with open(settingsConf, "r") as settingsFile:
			settings = settingsFile.readlines()

			for line in settings:
				if line.startswith("Stable"):
					stable = line.split(" ")[-1].strip("\n")
				if line.startswith("Development"):
					devel = line.split(" ")[-1].strip("\n")
		print("--- From file --- \n\nStable release: {} \nDevelopment release: {}\n".format(stable, devel))

def main():
	# Get information from winehq website
	URL = "https://www.winehq.org/"
	page = requests.get(URL)
	parsed = bsoup(page.content, 'html.parser')

	# Look for anything with "/announce/" in the href. We can then just look at the first two in the list.
	versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("/announce/"))]
	versions = versions[0:2]

	rawStable = versions[0].split("/")[-1]
	rawDevel = versions[1].split("/")[-1]

	#TODO: Fix this awful spaghetti
	if stable != rawStable or devel != rawDevel:
		print("!!! UPDATE DETECTED! !!!")
		print("--- From web --- \n\nStable release: {} \nDevelopment release: {}\n".format(rawStable, rawDevel))
		print("Writing to configuration file.")
		with open(settingsConf, "r") as settingsFile:
			with open(settingsConf + ".new", "w") as newSettings:
				settings = settingsFile.readlines()
				if stable != rawStable and devel == rawDevel:
					api.update_status("WINE Stable has updated to version {}!\nCheck the release notes here: {}".format(rawStable, URL+versions[0]))
					newSettings.write("Stable: {}{}".format(rawStable, settings[1]))
				elif stable == rawStable and devel != rawDevel:
					api.update_status("WINE Development has updated to version {}!\nCheck the release notes here: {}".format(rawDevel, URL+versions[1]))
					newSettings.write("{}Development: {}".format(settings[0], rawDevel))
				else:
					api.update_status("WINE Stable has updated to version {} and WINE Development has updated to version {}!\nCheck the release notes here: \n{} (Stable)\n{} (Development)".format(rawStable, rawDevel, URL+versions[0], URL+versions[1]))
					newSettings.write("Stable: {}Development: {}".format(rawStable, rawDevel))
		os.rename(settingsConf +".new", settingsConf)

	else:
		print("No update detected.")
	
while True:
	versionCheck()
	main()
	time.sleep(60**2 * 3.25)
