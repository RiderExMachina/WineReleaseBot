#!/usr/bin/env python3

from bs4 import BeautifulSoup as bsoup
from mastodon import Mastodon
import requests, re, time, os, tweepy, argparse, json

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help="Debug mode: will not post to Twitter or Mastodon", default=False, action='store_true')
args = parser.parse_args()

debug = args.debug

os.system("")
settingsFolder = ("/etc/wrb")
if not os.path.isdir(settingsFolder):
	os.mkdir(settingsFolder)
settingsConf = os.path.join(settingsFolder, "settings.conf")
authFile = os.path.join(settingsFolder, "auth.cred")
stable = "0"
devel = "0"
proton = "0"
dxvk = "0"
ge = "0"

class style():
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	CYAN = '\033[36m'
	RESET = '\033[0m'

def newSetup(platform):
	if platform == "Twitter":
		print("If you haven't already, please go to https://developer.twitter.com and get your App's keys and tokens.")
		twit_con_key = input("Paste your API Key here > ").strip()
		twit_con_sec = input("Paste your API Secret Key here > ").strip()
		twit_acc_key = input("Paste your Access Token here > ").strip()
		twit_acc_sec = input("Paste your Access Token Secret here >").strip()

		print(f"This information is being written to {twitAuthFile}. Please wait.")
		with open(twitAuthFile, 'w') as twitterAuth:
			twitterAuth.write(f"API Key: {twit_con_key}\nAPI Secret: {twit_con_sec}\nAccess Key: {twit_acc_key}\nAccess Secret: {twit_acc_sec}")
		time.sleep(5)
		print(f"Data written to {twitAuthFile}. You are now ready to use the Twitter API!")

	if platform == "Mastodon":
		print("If you haven't already, please go to your Mastodon's instance and get your keys and tokens.")
		mast_con_key = input("Paste your API Key here > ").strip()
		mast_con_sec = input("Paste your API Secret Key here > ").strip()
		mast_acc_key = input("Paste your Access Token here > ").strip()

		print(f"This information is being written to {mastAuthFile}. Please wait.")
		with open(mastAuthFile, 'w') as mastAuth:
			mastAuth.write(f"API Key: {mast_con_key}\nAPI Secret: {mast_con_sec}\nAccess Key: {mast_acc_key}")
		time.sleep(5)
		print(f"Data written to {mastAuthFile}. You are now ready to use the Mastodon API!")

if debug:
	class twitter:
		def update_status(message):
			print("Fake Twitter post: {}".format(message))
	class mastodon:
		def status_post(message):
			print("Fake Mastodon post: {}".format(message))

if not debug:
# Remove this if you don't want Twitter support
	if os.path.isfile(authFile):
		with open(authFile, "r") as Auth:
			if json.load(Auth)["twitter"]:	
				TWITTER_CONSUMER_KEY = json.load(Auth)["twit_api_key"]
				TWITTER_CONSUMER_SECRET = json.load(Auth)["twit_api_secret"]
				TWITTER_ACCESS_KEY = json.load(Auth)["twit_access_key"]
				TWITTER_ACCESS_SECRET = json.load(Auth)["twit_access_secret"]
	else:
		print(f"{style.RED}A file with your Twitter API information does not exist!{style.RESET}")
		setup = input(f"Would you like to create one? [{style.GREEN}Y{style.RESET}/{style.RED}n{style.RESET}]")
		affirmative = ["yes", "y", ""]
		negative = ["no", "n"]
		if setup.lower() in affirmative:
			newSetup("Twitter")
		if setup.lower() in negative:
			print(f"{style.YELLOW}Please comment out or remove the Twitter code.{style.RESET}")
			exit()


	auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
	twitter = tweepy.API(auth)
	# End Twitter remove

	# Remove this if you don't want Mastodon support
	mastodonURL = "botsin.space"
	if os.path.isfile(authFile):
		with open(authFile, "r") as Auth:
			if json.load(Auth)["mastodon"]:	
				MAST_CONSUMER_KEY = json.load(Auth)["mast_api_key"]
				MAST_CONSUMER_SECRET = json.load(Auth)["mast_api_secret"]
				MAST_ACCESS_KEY = json.load(Auth)["mast_access_key"]
	else:
		print(f"{style.RED}A file with your Mastodon API information does not exist!{style.RESET}")
		setup = input(f"Would you like to create one? [{style.GREEN}Y{style.RESET}/{style.RED}n{style.RESET}]")
		affirmative = ["yes", "y", ""]
		negative = ["no", "n"]
		if setup.lower() in affirmative:
			newSetup("Mastodon")
		if setup.lower() in negative:
			print(f"{style.YELLOW}Please comment out or remove the Mastodon code.{style.RESET}")
			exit()

	mastodon = Mastodon(client_id=MAST_CONSUMER_KEY, client_secret=MAST_CONSUMER_SECRET, access_token=MAST_ACCESS_KEY, api_base_url=mastodonURL)
	# End Mastodon remove

def versionCheck():
	global stable, devel, proton, dxvk, ge
	if os.path.isfile(settingsConf):
		with open(settingsConf, "r") as settingsFile:
			#settings = settingsFile.readlines()
			settings = json.load(settingsFile)

			stable = settings["Stable"]
			devel = settings["Development"]
			proton = settings["Proton"]
			dxvk = settings["DXVK"]
			ge = settings["GE"]
			#for line in settings:
			#	if line.startswith("Stable"):
			#		stable = line.split(" ")[-1].strip("\n")
			#	elif line.startswith("Development"):
			#		devel = line.split(" ")[-1].strip("\n")
			#	elif line.startswith("Proton"):
			#		proton = line.split(" ")[-1].strip("\n")
			#	elif line.startswith("DXVK"):
			#		dxvk = line.split(" ")[-1].strip("\n")
			#	elif line.startswith("GE"):
			#		ge = line.split(" ")[-1].strip("\n")
		print("--- From file ---")
		print(f"Wine Stable:\t{stable}\nWine Devel:\t{devel}\nProton:\t{proton}\nDXVK:\t{dxvk}\nGE:\t{ge}\n")

def post(message):
	print(f"{style.CYAN}Posting update to Twitter.{style.RESET}")
	twitter.update_status(message)
	print(f"{style.GREEN}Updated to Twitter posted successfully.\n{style.RESET}")
	
	print(f"{style.BLUE}Posting update to Mastodon.{style.RESET}")
	mastodon.status_post(message)
	print(f"{style.GREEN}Updated to Mastodon successfully.\n{style.RESET}")

def write2File():
	global stable, devel, proton, dxvk, ge

	print("Writing to configuration file...")
	with open(settingsConf + ".new", "w") as newSettings:
		info = {"Stable":stable, "Development":devel, "Proton": proton, "DXVK": dxvk, "GE": ge}
		json.dump(info, newSettings)

	os.rename(settingsConf + ".new", settingsConf)
	print("Written to file.\n")

def getGithubInfo(project, url):
	page = requests.get(url)
	information = page.json()

	latest = information[0]
	directURL = latest['html_url']
	release = latest['tag_name']

	return directURL, release

def main():
	global stable, devel, proton, dxvk, ge

	# Get information from winehq website and github
	URLs = {
			"Wine":	  "https://www.winehq.org",
			"Proton": "https://api.github.com/repos/ValveSoftware/Proton/releases",
			"DXVK":   "https://api.github.com/repos/doitsujin/dxvk/releases",
			"GE": 	  "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases"
			}

	for current in URLs:

		if current.lower() == "wine":
			page = requests.get(URLs[current])
			parsed = bsoup(page.content, 'html.parser')
			# Look for anything with "/announce/" in the href. We can then just look at the first two in the list.
			versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("/announce/"))]

			newStable = versions[0].split("/")[-1]
			newDevel = versions[1].split("/")[-1]

			if stable != newStable or devel != newDevel:
				print(f"!!! {style.RED}WINE{style.RESET} {style.YELLOW}UPDATE DETECTED!{style.RESET} !!!")
				print("--- From web --- \n\nStable release: {} \nDevelopment release: {}\n".format(newStable, newDevel))
				print("Writing to configuration file.")
				
				if stable != newStable and devel == newDevel:
					post("WINE Stable has updated to version {}!\nCheck the release notes here: {}".format(newStable, URLs[current]+versions[0]))
					
				elif stable == newStable and devel != newDevel:
					post("WINE Development has updated to version {}!\nCheck the release notes here: {}".format(newDevel, URLs[current]+versions[1]))

				else:
					post("WINE Stable has updated to version {} and WINE Development has updated to version {}!\nCheck the release notes here: \n{} (Stable)\n{} (Development)".format(newStable, newDevel, URLs[current]+versions[0], URLs[current]+versions[1]))
				stable = newStable
				devel = newDevel

				write2File()


		if current.lower() != "wine":
			link, release = getGithubInfo(current, URLs[current])

			if eval(current.lower()) != release:
				print(f"!!! {style.YELLOW}{current.upper()} UPDATE DETECTED!{style.RESET} !!!")
				print("--- From web -- \n\nLatest release: {}\n".format(release))
				
				post(f"{current} has updated to release {release}!\nCheck out the release here: {link}")
				
				if current == "Proton":
					proton = release
				elif current == "DXVK":
					dxvk = release
				elif current == "GE":
					ge = release

				write2File()
	else:
		print("No update detected.")
	
versionCheck()

while True:
	main()
	print("Checked! Sleeping for 1 hour.\n")
	time.sleep(60**2 * 0.999999)
