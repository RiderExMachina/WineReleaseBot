#!/usr/bin/env python3
## Rewrite of the original Wine Release Bot
## Things could probably be improved further, but I'm happy with this

import requests, re, relay, time, os, argparse, json, logging, datetime, shutil
from bluepy import bsky

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help="Debug mode: will not actually create posts.", default=False, action='store_true')
#parser.add_argument('-s', '--setup', help="Install prerequisites to make sure everything is good to go.", default=False, action='store_true')
args = parser.parse_args()

debug = args.debug
#setup = args.setup
relay = relay.relay

## Clear out old logs
def clearOld(settingsFolder):
	cleared = False
	relay("\t- Looking for old logs to clear out...")
	currentMonth = datetime.datetime.now().strftime("%B")
	for filename in os.listdir(settingsFolder):
		if ".log" in filename and currentMonth not in filename:
			cleared = True
			relay(f"\t\t-Removing {filename}")
			os.remove(os.path.join(settingsFolder, filename))
	if cleared == True: relay("\t- Old logs cleared out")

def createAuth(authFile):
    relay("A new auth.cred file must be created. Which social media would you like to set up?\n\t1. Mastodon\n\t2. Bluesky\n\t3. Both")
    platform = input("> ")
    if platform in ["1", "3", "Mastodon"]:
        relay("If you haven't already, please go to your Mastodon's instance and get your keys and tokens.")
        mast_inst    = input("Paste your Mastodon instance here > ").strip()
        mast_con_key = input("Paste your API Key here > ").strip()
        mast_con_sec = input("Paste your API Secret Key here > ").strip()
        mast_acc_key = input("Paste your Access Token here > ").strip()

        relay(f"This information is being written to {authFile}. Please wait.")
        with open(authFile, 'a') as mastAuth:
            mastInfo = {"mastodon": {"mast_instance": mast_inst, "mast_api_key": mast_con_key, "mast_api_secret": mast_con_sec, "mast_access_key": mast_acc_key}}
            json.dump(mastInfo, mastAuth, indent=4)
        time.sleep(5)
        relay(f"Data written to {authFile}. You are now ready to use the Mastodon API!")
    if platform in ["2", "3", "Bluesky"]:
        relay("If you haven't already, please go to Bluesky and set up your App Password.")
        bsky_username = input("Enter your Bluesky username here > ").strip()
        bsky_pass     = input("Enter you Bluesky app password here > ").strip()

        relay(f"This information is being written to {authFile}. Please wait.")

        with open(authFile, 'a') as bskyAuth:
            bskyInfo = {"bsky": {"bsky_handle": bsky_username, "bsky_app_pass": bsky_pass}}
            json.dump(bskyInfo, bksyAuth, indent=4)
        time.sleep(3)
        relay(f"Data written to {authFile}. You are now ready to use the Bluesky API!")


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
        "bsky": [{
        "bsky_handle": "example.bluesky.social",
        "bsky_app_pass": "123-456-789",
    }]
    }
    """
    with open(authFile, 'r') as Auth:
        mast_info = json.load(Auth)["mastodon"]
        relay("\tMastodon info found.")

        bsky_info = json.load(Auth)["bsky"]
        relay("\tBluesky info found.")

    MAST_INSTANCE = mast_info["mast_instance"]
    MAST_CONSUMER_KEY = mast_info["mast_api_key"]
    MAST_CONSUMER_SECRET = mast_info["mast_api_secret"]
    MAST_ACCESS_KEY = mast_info["mast_access_key"]
    relay("Mastodon information loaded successfully.")

    BSKY_HANDLE = bsky_info["bsky_handle"]
    BSKY_APP_PASS = bsky_info["bsky_app_pass"]

    mastodon = Mastodon(api_base_url=MAST_INSTANCE, client_id=MAST_CONSUMER_KEY, client_secret=MAST_CONSUMER_SECRET, access_token=MAST_ACCESS_KEY)
    bsky = bsky(client_id=BSKY_HANDLE, app_password=BSKY_APP_PASS)

    return mastodon, bsky

def post(messages):
    ## Should probably not import everything if there's nothing to import
    if not debug:
        if not os.path.isfile(authFile):
            createAuth(authFile)
        mastodon, bsky = importAuth(authFile)
    if debug:
        class mastodon:
            def status_post(message):
                relay("\t\tFake Mastodon post: {}".format(message))
        class bsky:
            def status_post(message):
                relay("\t\tFake Bsky post: {}".format(message))
    for item in messages:
        update = messages[item]
        name = update["name"]
        url = update["url"]
        version = update["release"]
        tags = update["tags"]

        message = f"{name} has updated to version {version}. Check it out at the link below {tags} {url}"

        relay(f"\t\tPosting update to Bluesky.")
        bsky.status_post(message)
        relay(f"\t\tUpdated to Bluesky successfully.\n")

        relay(f"\t\tPosting update to Mastodon.")
        mastodon.status_post(message)
        relay(f"\t\tUpdated to Mastodon successfully.\n")

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

def writeUpdates(projFile, updates):
    with open(projFile+".new", 'w') as projectFile:
        json.dump(updates, projectFile, indent=4)
    shutil.copy(projFile+".new", projFile)

def checkUpdates(projects):
    updated = {}
    return_info = {}
    for project in projects:
        info = projects[project]

        name = info['name']
        release_url = info['url']
        api_url = info["api-url"]
        cached_release = info["latest-release"]
        tags = info["tags"]

        if  name == "Wine":
            new_url, new_release = getWineInfo(api_url)
        else:
            new_url, new_release = getGithubInfo(api_url)

        if new_release != cached_release:
            relay(f"\t!! {name} UPDATE DETECTED !!\n\tPrevious Release: {cached_release}\n\tUpdated Release: {new_release}")
            updated[name] = {"name": name, "release": new_release, "url": new_url, "tags": tags}
        else:
            relay(f"\t - No updates detected for {name}")

        return_info[name] = {"name": name, "url": new_url, "api-url": api_url, "latest-release": new_release, "tags":tags}

    post(updated)
    return return_info


def main():
    settingsFolder = importSettings()
    logFolder = "/var/log/wrb"

    authFile = os.path.join(settingsFolder, "auth.cred")
    projFile = os.path.join(settingsFolder, "projects.json")

    projects = importProjects(projFile)
    updates = checkUpdates(projects)

    writeUpdates(projFile, updates)
    clearOld(logFolder)

if __name__ == "__main__":
    relay(f"- Started at {datetime.datetime.now()}")
    if not os.path.isfile("settings.json"):
        import setup
        setup()
    main()
    relay(f"- Finished at {datetime.datetime.now()}")
