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
	from mastodon import Mastodon
except ImportError as e:
	if debug:
		relay(f"Importing modules: {e}")
	else:
		relay("\nOne of the dependencies has not been installed on this system!\nPlease run with the -s flag!\n")
		quit()

## Internal config and initializations
settingsConf = os.path.join(settingsFolder, "settings.conf")
authFile = os.path.join(settingsFolder, "auth.cred")
wine = "0"
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
	global wine, proton, dxvk, ge
	relay("\t- Checking cached versions of software...")
	if os.path.isfile(settingsConf):
		relay(f"\t- Opening {settingsConf}...")
		with open(settingsConf, "r") as settingsFile:
			settings = json.load(settingsFile)
			wine = settings["Wine"]
			proton = settings["Proton"]
			dxvk = settings["DXVK"]
			ge = settings["GE"]

		relay("\t\t--- From file ---")
		relay(f"\t\tWine:\t{wine}\n\t\tProton:\t{proton}\n\t\tDXVK:\t{dxvk}\n\t\tGE:\t{ge}\n")

def post(message):
	relay(f"\t\t{style.CYAN}Posting update to Twitter.{style.RESET}")
	twitter.update_status(message)
	relay(f"\t\t{style.GREEN}Updated to Twitter successfully.\n{style.RESET}")
	
	relay(f"\t\t{style.BLUE}Posting update to Mastodon.{style.RESET}")
	mastodon.status_post(message + "\n#WineHQ #Proton #Linux #DXVK")
	relay(f"\t\t{style.GREEN}Updated to Mastodon successfully.\n{style.RESET}")
## Write updated information to settings.conf
def write2File():
	global wine, proton, dxvk, ge

	relay("\tWriting to configuration file...")
	with open(settingsConf + ".new", "w") as newSettings:
		info = {"Wine":wine, "Proton": proton, "DXVK": dxvk, "GE": ge}
		json.dump(info, newSettings, indent=4)

	os.rename(settingsConf + ".new", settingsConf)
	relay("\tWritten to file.\n")
## Pull information from Github via Github API
def getGithubInfo(url):
	page = requests.get(url)
	information = page.json()

	latest = information[0]
	directURL = latest['html_url']
	release = latest['tag_name']

	return directURL, release

def getWineInfo(url):
	page = requests.get(url)
	information = page.json()

	latest = information[0]
	directURL = latest["_links"]["self"]
	release = latest["tag_name"]

	return directURL, release

def main():
	global wine, proton, dxvk, ge

	# URLs of the different projects
	URLs = {
			"Wine":	  "https://gitlab.winehq.org/api/v4/projects/5/releases",
			"Proton": "https://api.github.com/repos/ValveSoftware/Proton/releases",
			"DXVK":   "https://api.github.com/repos/doitsujin/dxvk/releases",
			"GE": 	  "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases"
			}

	for current in URLs:
		if current == "Wine":
			link, release = getWineInfo(URLs[current])
		else:
			link, release = getGithubInfo(URLs[current])

		if eval(current.lower()) != release:
			relay(f"\t\t!!! {style.YELLOW}{current.upper()} UPDATE DETECTED!{style.RESET} !!!")
			relay("\t\t--- From web -- \n\n\t\tLatest release: {}\n".format(release))

			post(f"{current} has updated to release {release}!\nCheck out the release here: {link}")

			match current:
				case "Wine":
					wine = release
				case "Proton":
					proton = release
				case "DXVK":
					dxvk = release
				case "GE":
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
