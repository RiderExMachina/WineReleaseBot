#!/usr/bin/env python3

from bs4 import BeautifulSoup as bsoup
from mastodon import Mastodon
import requests, re, time, os, tweepy

settingsConf = "settings.conf"
stable = "0"
devel = "0"
proton = "0"
dxvk = "0"
d9vk = "0"

mastodonURL = "botsin.space"
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
mastodon = Mastodon(client_id=MAST_CONSUMER_KEY, client_secret=MAST_CONSUMER_SECRET, access_token=MAST_ACCESS_KEY, api_base_url=mastodonURL)

def versionCheck():
	global stable, devel, proton, d9vk, dxvk
	if os.path.isfile(settingsConf):
		with open(settingsConf, "r") as settingsFile:
			settings = settingsFile.readlines()

			for line in settings:
				if line.startswith("Stable"):
					stable = line.split(" ")[-1].strip("\n")
				elif line.startswith("Development"):
					devel = line.split(" ")[-1].strip("\n")
				elif line.startswith("Proton"):
					proton = line.split(" ")[-1].strip("\n")
				elif line.startswith("DXVK"):
					dxvk = line.split(" ")[-1].strip("\n")
				elif line.startswith("D9VK"):
					d9vk = line.split(" ")[-1].strip("\n")
		print("--- From file ---")
		for line in settings:
			print(line.replace("\n", ""))
		print("")

def post(message):
    print("Posting update to Twitter.")
    twitter.update_status(message)
    print("Updated to Twitter posted successfully.\n")

    print("Posting update to Mastodon.")
    mastodon.status_post(message)
    print("Updated to Mastodon successfully.\n")

def write2File():
	global stable, devel, proton, dxvk, d9vk

	print("Writing to configuration file.\n")
	with open(settingsConf + ".new", "w") as newSettings:
		newSettings.write("Stable: {}\nDevelopment: {}\nProton: {}\nDXVK: {}\nD9VK: {}".format(stable, devel, proton, dxvk, d9vk))

	os.rename(settingsConf + ".new", settingsConf)
	print("Written to file.\n")

def main():
	global stable, devel, proton, dxvk, d9vk
	# Get information from winehq website
	URLs = ["https://www.winehq.org", "https://github.com/ValveSoftware/Proton/releases", "https://github.com/doitsujin/dxvk/releases", "https://github.com/Joshua-Ashton/d9vk/releases"]
	gitURL = "https://github.com"
	URL = URLs[0]
	for URL in URLs:
		if URL == URLs[0]:
			current = "wine"
		elif URL == URLs[1]:
			current = "proton"
		elif URL == URLs[2]:
			current = "dxvk"
		elif URL == URLs[3]:
			current = "d9vk"


		page = requests.get(URL)
		parsed = bsoup(page.content, 'html.parser')

		if current == "wine":
			# Look for anything with "/announce/" in the href. We can then just look at the first two in the list.
			versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("/announce/"))]

			rawStable = versions[0].split("/")[-1]
			rawDevel = versions[1].split("/")[-1]

			#TODO: Fix this awful spaghetti
			if stable != rawStable or devel != rawDevel:
				print("!!! WINE UPDATE DETECTED! !!!")
				print("--- From web --- \n\nStable release: {} \nDevelopment release: {}\n".format(rawStable, rawDevel))
				print("Writing to configuration file.")
				
				if stable != rawStable and devel == rawDevel:
					post("WINE Stable has updated to version {}!\nCheck the release notes here: {}".format(rawStable, URL+versions[0]))
					
				elif stable == rawStable and devel != rawDevel:
					post("WINE Development has updated to version {}!\nCheck the release notes here: {}".format(rawDevel, URL+versions[1]))

				else:
					post("WINE Stable has updated to version {} and WINE Development has updated to version {}!\nCheck the release notes here: \n{} (Stable)\n{} (Development)".format(rawStable, rawDevel, URL+versions[0], URL+versions[1]))
				stable = rawStable
				devel = rawDevel

				write2File()


		if current == "proton":
			versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("releases/tag"))]
			latest = versions[0]
			link = gitURL + latest
			version = latest.split("/")[-1].replace("proton-", "")

			if proton != version:
				print("!!! PROTON UPDATE DETECTED !!!")
				print("--- From web -- \n\nLatest release: {}\n".format(version))
				
				post("Proton has update to version {}!\nCheck out the release here: {}".format(version, link))
				
				proton = version
				write2File()
		
		if current == "dxvk":
			versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("releases/tag"))]
			latest = versions[0]
			link = gitURL + latest
			version = latest.split("/")[-1].replace("v", "")

			if dxvk != version:
				print("!!! DXVK UPDATE DETECTED !!!")
				print("--- From web -- \n\nLatest release: {}\n".format(version))
				
				post("DXVK has update to version {}!\nCheck out the release here: {}".format(version, link))

				dxvk = version
				write2File()

		if current == "d9vk":
			versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("releases/tag"))]
			latest = versions[0]
			link = gitURL + latest
			version = latest.split("/")[-1]

			if d9vk != version:
				print("!!! D9VK UPDATE DETECTED !!!")
				print("--- From web -- \n\nLatest release: {}\n".format(version))
				
				post("D9VK has update to version {}!\nCheck out the release here: {}".format(version, link))
				d9vk = version
				write2File()

	else:
		print("No update detected.")
	

versionCheck()

while True:
	main()
	print("Checked! Sleeping for 3 hours.\n")
	time.sleep(60**2 * 3.25)
