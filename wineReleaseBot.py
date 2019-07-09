#!/usr/bin/env python3

from bs4 import BeautifulSoup as bsoup
from mastodon import Mastodon
import requests, re, time, os, tweepy

settingsConf = "settings.conf"
stable = "0"
devel = "0"

# Remove this if you don't want Twitter support
if os.path.isfile("twitter-auth.cred"):
	with open("twitter-auth.cred", "r") as twitterAuth:
		authCred = twitterAuth.readlines()
		
		TWITTER_CONSUMER_KEY = authCred[0].split(" ")[-1].strip("\n")
		TWITTER_CONSUMER_SECRET = authCred[1].split(" ")[-1].strip("\n")
		TWITTER_ACCESS_KEY = authCred[2].split(" ")[-1].strip("\n")
		TWITTER_ACCESS_SECRET = authCred[3].split(" ")[-1].strip("\n")
else:
	print("Please create a twitter-auth.cred file with your Twitter API information!")
	exit()
# End Twitter remove

# Remove this if you don't want Mastodon support
if os.path.isfile("mast-auth.cred"):
	with open("mast-auth.cred", "r") as mastAuth:
		authCred = mastAuth.readlines()

		MAST_CONSUMER_KEY = authCred[0].split(" ")[-1].strip("\n")
		MAST_CONSUMER_SECRET = authCred[1].split(" ")[-1].strip("\n")
		MAST_ACCESS_KEY = authCred[2].split(" ")[-1].strip("\n")
else:
	print("Please create a mast-auth.cred file with your Mastodon API information!")
	exit()
# End Mastodon remove


# Remove this if you don't want Twitter support
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
twitter = tweepy.API(auth)
# End Twitter remove

#Remove the next line if you don't want mastodon support
mastodon = Mastodon(client_id=MAST_CONSUMER_KEY, client_secret=MAST_CONSUMER_SECRET, access_token=MAST_ACCESS_KEY, api_base_url='botsin.space')

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
	URL = "https://www.winehq.org"
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
					twitter.update_status("WINE Stable has updated to version {}!\nCheck the release notes here: {}".format(rawStable, URL+versions[0]))
					print("Sent update to Twitter.")
					mastodon.status_post("WINE Stable has updated to version {}!\nCheck the release notes here: {}".format(rawStable, URL+versions[0]))
					print("Sent update to Mastodon.")
					newSettings.write("Stable: {}{}".format(rawStable, settings[1]))
					print("Written update to file.")
				elif stable == rawStable and devel != rawDevel:
					twitter.update_status("WINE Development has updated to version {}!\nCheck the release notes here: {}".format(rawDevel, URL+versions[1]))
					print("Sent update to Twitter.")
					mastodon.status_post("WINE Development has updated to version {}!\nCheck the release notes here: {}".format(rawDevel, URL+versions[1]))
					print("Sent update to Mastodon.")
					newSettings.write("{}Development: {}".format(settings[0], rawDevel))
					print("Written update to file.")
				else:
					twitter.update_status("WINE Stable has updated to version {} and WINE Development has updated to version {}!\nCheck the release notes here: \n{} (Stable)\n{} (Development)".format(rawStable, rawDevel, URL+versions[0], URL+versions[1]))
					print("Sent update to Twitter.")
					mastodon.status_post("WINE Stable has updated to version {} and WINE Development has updated to version {}!\nCheck the release notes here: \n{} (Stable)\n{} (Development)".format(rawStable, rawDevel, URL+versions[0], URL+versions[1]))
					print("Sent update to Mastodon.")
					newSettings.write("Stable: {}Development: {}".format(rawStable, rawDevel))
					print("Written update to file.")

		os.rename(settingsConf +".new", settingsConf)

	else:
		print("No update detected.")
	
while True:
	versionCheck()
	main()
	print("Job done! Sleeping for 3 hours.")
	time.sleep(60**2 * 3.25)
