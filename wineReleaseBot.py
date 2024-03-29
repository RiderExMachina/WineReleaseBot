#!/usr/bin/env python3
import requests, re, time, os, argparse, json, logging, datetime
## Create aruments for debug and setup. Could potentially make more, like -m or -t for desired platforms to post to.
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help="Debug mode: will not post to Twitter or Mastodon", default=False, action='store_true')
parser.add_argument('-s', '--setup', help="Install prerequisites to make sure everything is good to go.", default=False, action='store_true')
args = parser.parse_args()

debug = args.debug
setup = args.setup
## Set global folders for config and log files. I know, the log files are not in /var/log or ~/.cache, I may fix this later
def get_settings_folder():
	user = os.geteuid()
	if user == 0:
		return "/etc/wrb"
	elif os.path.isdir(".git"):
		print(f"Git version detected.")
		return "."
	else:
		home_folder = os.path.expanduser("~")
		return os.path.join(home_folder, ".config/wrb")

settingsFolder = get_settings_folder()
## Set up logging
logging.basicConfig(filename=f"{settingsFolder}/wrb-{datetime.datetime.now().strftime('%B-%d-%Y')}.log", encoding="utf-8", level=logging.DEBUG)
def relay(msg):
	logging.debug(msg)
	print(msg)

relay(f"Setting {settingsFolder} as settingsFolder...")
if not os.path.isdir(settingsFolder):
	os.mkdir(settingsFolder)

## If setup argument is passed, install the necessary requirements
if setup:
	import subprocess
	relay("Setup argument passed. Performing setup")
	relay("Attempting to install requirements...")
	cmd = "pip3 install -r requirements.txt"
	if os.geteuid() != 0:
		cmd = f"sudo {cmd}"
	subprocess.run(cmd, shell=True, check=True)
	relay("Success! Please start the script without the '-s' argument")
	exit()
## Now that we know these should be installed, we can import them
try:
	from bs4 import BeautifulSoup as bsoup
	from mastodon import Mastodon
	import tweepy
except:
	if debug:
		pass
	else:
		relay("\nOne of the dependencies has not been installed on this system!\nPlease run with the -s flag!\n")
		quit()

## Internal config and initializations
settingsConf = os.path.join(settingsFolder, "settings.conf")
authFile = os.path.join(settingsFolder, "auth.cred")
stable = "0"
devel = "0"
proton = "0"
dxvk = "0"
ge = "0"
## Set font colors for terminal
## TODO: remove now that this is installable?
class style():
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	CYAN = '\033[36m'
	RESET = '\033[0m'
## Wizard to set up an auth.cred file if one is not found
def newSetup(platform):
	if platform == "Twitter":
		relay("If you haven't already, please go to https://developer.twitter.com and get your App's keys and tokens.")
		twit_con_key = input("Paste your API Key here > ").strip()
		twit_con_sec = input("Paste your API Secret Key here > ").strip()
		twit_acc_key = input("Paste your Access Token here > ").strip()
		twit_acc_sec = input("Paste your Access Token Secret here >").strip()

		relay(f"This information is being written to {authFile}. Please wait.")
		with open(authFile, 'a') as twitterAuth:
			twitInfo = {"twitter": [{"twit_api_key": twit_con_key, "twit_api_sec": twit_con_sec, "twit_access_key": twit_acc_key, "twit_access_secret": twit_acc_sec}]}
			json.dump(twitInfo, twitterAuth, indent=4)
		time.sleep(5)
		relay(f"Data written to {authFile}. You are now ready to use the Twitter API!")

	if platform == "Mastodon":
		relay("If you haven't already, please go to your Mastodon's instance and get your keys and tokens.")
		mast_con_key = input("Paste your API Key here > ").strip()
		mast_con_sec = input("Paste your API Secret Key here > ").strip()
		mast_acc_key = input("Paste your Access Token here > ").strip()

		relay(f"This information is being written to {authFile}. Please wait.")
		with open(authFile, 'a') as mastAuth:
			mastInfo = {"mastodon": [{"mast_api_key": mast_con_key, "mast_api_secret": mast_con_sec, "mast_access_key": mast_acc_key}]}
			json.dump(mastInfo, mastAuth, indent=4)
		time.sleep(5)
		relay(f"Data written to {mastAuthFile}. You are now ready to use the Mastodon API!")
## Stubs for in debug mode (mostly for testing without an auth.cred)
if debug:
	class twitter:
		def update_status(message):
			relay("\t\tFake Twitter post: {}".format(message))
	class mastodon:
		def status_post(message):
			relay("\t\tFake Mastodon post: {}".format(message))
## Import data from auth.cred
if not debug:
# Remove this if you don't want Twitter support
	relay("\tLooking for Twitter information...")
	if os.path.isfile(authFile):
		with open(authFile, "r") as Auth:
			twit_info = json.load(Auth)["twitter"]
			relay("Found.")
			for info in twit_info:
				TWITTER_CONSUMER_KEY = info["twit_api_key"]
				TWITTER_CONSUMER_SECRET = info["twit_api_secret"]
				TWITTER_ACCESS_KEY = info["twit_access_key"]
				TWITTER_ACCESS_SECRET = info["twit_access_secret"]
		relay("\tTwitter information loaded successfully.")
			
	else:
		relay(f"{style.RED}A file with your Twitter API information does not exist!{style.RESET}")
		setup = input(f"Would you like to create one? [{style.GREEN}Y{style.RESET}/{style.RED}n{style.RESET}]")
		affirmative = ["yes", "y", ""]
		negative = ["no", "n"]
		if setup.lower() in affirmative:
			newSetup("Twitter")
		if setup.lower() in negative:
			relay(f"{style.YELLOW}Please comment out or remove the Twitter code.{style.RESET}")
			exit()


	auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
	twitter = tweepy.API(auth)
	# End Twitter remove

	# Remove this if you don't want Mastodon support
	mastodonURL = "botsin.space"
	relay("\t - Looking for Mastodon information...")
	if os.path.isfile(authFile):
		with open(authFile, "r") as Auth:
			mast_info = json.load(Auth)["mastodon"]
			relay("\tFound.")
			for info in mast_info:	
				MAST_CONSUMER_KEY = info["mast_api_key"]
				MAST_CONSUMER_SECRET = info["mast_api_secret"]
				MAST_ACCESS_KEY = info["mast_access_key"]
		relay("Mastodon information loaded successfully.")
	else:
		relay(f"{style.RED}A file with your Mastodon API information does not exist!{style.RESET}")
		setup = input(f"Would you like to create one? [{style.GREEN}Y{style.RESET}/{style.RED}n{style.RESET}]")
		affirmative = ["yes", "y", ""]
		negative = ["no", "n"]
		if setup.lower() in affirmative:
			newSetup("Mastodon")
		if setup.lower() in negative:
			relay(f"{style.YELLOW}Please comment out or remove the Mastodon code.{style.RESET}")
			exit()

	mastodon = Mastodon(client_id=MAST_CONSUMER_KEY, client_secret=MAST_CONSUMER_SECRET, access_token=MAST_ACCESS_KEY, api_base_url=mastodonURL)
	# End Mastodon remove

## Clear out old logs
def clearOld():
	cleared = False
	relay("\t- Looking for old logs to clear out...")
	currentMonth = datetime.datetime.now().strftime("%B")
	for filename in os.listdir(settingsFolder):
		if ".log" in filename and currentMonth not in filename:
			cleared = True
			relay(f"\t\t-Removing {filename}")
			os.remove(os.path.join(settingsFolder, filename))
	if cleared == True: relay("\t- Old logs cleared out")
## Check cached versions from settings.conf
def versionCheck():
	global stable, devel, proton, dxvk, ge
	relay("\t- Checking cached versions of software...")
	if os.path.isfile(settingsConf):
		relay(f"\t- Opening {settingsConf}...")
		with open(settingsConf, "r") as settingsFile:
			settings = json.load(settingsFile)

			stable = settings["Stable"]
			devel = settings["Development"]
			proton = settings["Proton"]
			dxvk = settings["DXVK"]
			ge = settings["GE"]

		relay("\t\t--- From file ---")
		relay(f"\t\tWine Stable:\t{stable}\n\t\tWine Devel:\t{devel}\n\t\tProton:\t{proton}\n\t\tDXVK:\t{dxvk}\n\t\tGE:\t{ge}\n")

def post(message):
	relay(f"\t\t{style.CYAN}Posting update to Twitter.{style.RESET}")
	twitter.update_status(message)
	relay(f"\t\t{style.GREEN}Updated to Twitter successfully.\n{style.RESET}")
	
	relay(f"\t\t{style.BLUE}Posting update to Mastodon.{style.RESET}")
	mastodon.status_post(message + "\n#WineHQ #Proton #Linux #DXVK")
	relay(f"\t\t{style.GREEN}Updated to Mastodon successfully.\n{style.RESET}")
## Write updated information to settings.conf
def write2File():
	global stable, devel, proton, dxvk, ge

	relay("\tWriting to configuration file...")
	with open(settingsConf + ".new", "w") as newSettings:
		info = {"Stable":stable, "Development":devel, "Proton": proton, "DXVK": dxvk, "GE": ge}
		json.dump(info, newSettings, indent=4)

	os.rename(settingsConf + ".new", settingsConf)
	relay("\tWritten to file.\n")
## Pull information from Github via Github API
def getGithubInfo(project, url):
	page = requests.get(url)
	information = page.json()

	latest = information[0]
	directURL = latest['html_url']
	release = latest['tag_name']

	return directURL, release

def main():
	global stable, devel, proton, dxvk, ge

	# URLs of the different projects
	URLs = {
			"Wine":	  "https://www.winehq.org",
			"Proton": "https://api.github.com/repos/ValveSoftware/Proton/releases",
			"DXVK":   "https://api.github.com/repos/doitsujin/dxvk/releases",
			"GE": 	  "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases"
			}

	for current in URLs:
		## Start with Wine since it has a stable release cadence (avg every 2 weeks for Devel)
		if current.lower() == "wine":
			page = requests.get(URLs[current])
			parsed = bsoup(page.content, 'html.parser')
			# Look for anything with "/announce/" in the href. We can then just look at the first two in the list.
			versions = [a['href'] for a in parsed.find_all(name="a", href=re.compile("/announce/"))]

			newStable = versions[0].split("/")[-1]
			newDevel = versions[1].split("/")[-1]

			if stable != newStable or devel != newDevel:
				relay(f"\t\t!!! {style.RED}WINE{style.RESET} {style.YELLOW}UPDATE DETECTED!{style.RESET} !!!")
				relay("\t\t--- From web --- \n\n\t\tStable release: {} \n\t\tDevelopment release: {}\n".format(newStable, newDevel))
				relay("\tWriting to configuration file.")
				
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
				relay(f"\t\t!!! {style.YELLOW}{current.upper()} UPDATE DETECTED!{style.RESET} !!!")
				relay("\t\t--- From web -- \n\n\t\tLatest release: {}\n".format(release))
				
				post(f"{current} has updated to release {release}!\nCheck out the release here: {link}")
				
				if current == "Proton":
					proton = release
				elif current == "DXVK":
					dxvk = release
				elif current == "GE":
					ge = release

				write2File()
	else:
		relay("\tNo update detected.")
if __name__ == "__main__":
	relay(f"- Started at {datetime.datetime.now()}")
	versionCheck()
	main()
	clearOld()
	relay(f"- Finished at {datetime.datetime.now()}")
