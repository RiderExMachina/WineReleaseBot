#!/usr/bin/env python3
import requests, re, relay, time, os, argparse, json, logging, datetime

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help="Debug mode: will not actually create posts.", default=False, action='store_true')
parser.add_argument('-s', '--setup', help="Install prerequisites to make sure everything is good to go.", default=False, action='store_true')
args = parser.parse_args()

debug = args.debug
setup = args.setup
relay = relay.relay

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

def post(message):
	relay(f"\t\t{style.CYAN}Posting update to Bluesky.{style.RESET}")
	bsky.update_status(message)
	relay(f"\t\t{style.GREEN}Updated to Bluesky successfully.\n{style.RESET}")

	relay(f"\t\t{style.BLUE}Posting update to Mastodon.{style.RESET}")
	mastodon.status_post(message + "\n#WineHQ #Proton #Linux #DXVK")
	relay(f"\t\t{style.GREEN}Updated to Mastodon successfully.\n{style.RESET}")

def createAuth(authFile):
    relay("A new auth.cred file must be created. Which social media would you like to set up?\n\t1. Mastodon\n\t2. Bluesky")
    platform = input("> ")
    if platform in ["1", "Mastodon"]:
        relay("If you haven't already, please go to your Mastodon's instance and get your keys and tokens.")
        mast_inst    = input("Paste your Mastodon instance here > ").strip()
        mast_con_key = input("Paste your API Key here > ").strip()
        mast_con_sec = input("Paste your API Secret Key here > ").strip()
        mast_acc_key = input("Paste your Access Token here > ").strip()

        relay(f"This information is being written to {authFile}. Please wait.")
        with open(authFile, 'a') as mastAuth:
            mastInfo = {"mastodon": [{"mast_instance": mast_inst, "mast_api_key": mast_con_key, "mast_api_secret": mast_con_sec, "mast_access_key": mast_acc_key}]}
            json.dump(mastInfo, mastAuth, indent=4)
        time.sleep(5)
        relay(f"Data written to {authFile}. You are now ready to use the Mastodon API!")
    if platform in ["2", "Bluesky"]:
        relay("If you haven't already, please go to Bluesky and aet up your App Password.")
        bsky_username = input("")

def importAuth(authFile):
    """
    Import auth information from auth.cred file.

    auth.json file should look something like:
    {
      "mastodon":[{
        "mast_instance": "examplemast.com",
        "mast_api_key": "deadbeef98174...",
        "mast_api_secret": "baebee9128ad...",
        "mast_access_key": "093487961324..."
    }],
        "bluesky": [{
        "bsky_handle": "example.bluesky.social",
        "bsky_app_pass": "123-456-789",
    }]
    }
    """
    with open(authFile, 'r') as Auth:
        mast_info = json.load(Auth)["mastodon"]
        relay("\tMastodon info found.")
        #bsky_info = json.load(Auth)["bsky"]

    for info in mast_info:
            MAST_INSTANCE = info["mast_instance"]
            MAST_CONSUMER_KEY = info["mast_api_key"]
            MAST_CONSUMER_SECRET = info["mast_api_secret"]
            MAST_ACCESS_KEY = info["mast_access_key"]
    relay("Mastodon information loaded successfully.")

    mastodon = Mastodon(client_id=MAST_CONSUMER_KEY, client_secret=MAST_CONSUMER_SECRET, access_token=MAST_ACCESS_KEY, api_base_url=MAST_INSTANCE)

    return mastodon

def importProjects(projFile):
    """
    Import projects from projects.json

    projects.json should look something like:
    {
        "project": {
            "url": "https://projectwebsite.com",
            "version": "v5.1",
        }
    ...
    }
    """
    with open(projFile, 'r') as projects:
        projList = json.load(projects)

    return projList

def importSettings():
    """
    Import settings from settings.conf file.

    settings.conf file should look something like:
    {
        "info-dir": "/etc/wrb"
    }
    """
    with open('settings.json', 'r') as settingsFile:
        info = json.load(settingsFile)

    settingsFolder = info["info-dir"]

    return settingsFolder

## Pull information from Github via Github API
def getGithubInfo(project, url):
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

def checkUpdates(projects):
    for project in projects:
        info = projects[project]

        name = info['name']
        release_url = info['url']
        api_url = info["api-url"]
        latest_release = info["latest-release"]
        tags = info["tags"]

        new_url, new_release = getGithubInfo(api_url)
        if new_release != latest_release:
            relay(f"!! {name} UPDATE DETECTED !!\n\tPrevious Release: {latest_release}\n\tUpdated Release: {new_release}")



def main():
    settingsFolder = importSettings()

    authFile = os.path.join(settingsFolder, "auth.cred")
    projFile = os.path.join(settingsFolder, "projects.json")

    if not debug:
        if not os.path.isfile(authFile):
            createAuth(authFile)
        mastodon = importAuth(authFile)
    if debug:
        class mastodon:
            def status_post(message):
                relay("\t\tFake Mastodon post: {}".format(message))

    projects = importProjects(projFile)
    checkUpdates(projects)

if __name__ == "__main__":
    relay(f"- Started at {datetime.datetime.now()}")
    if not os.path.isfile("settings.json"):
        import setup
        setup()
    main()
    clearOld()
    relay(f"- Finished at {datetime.datetime.now()}")
