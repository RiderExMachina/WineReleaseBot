# Wine Release Bot

TL;DR - See the bot in action on [Blueksy](https://bsky.app/profile/winereleasebot.bsky.social) or <a rel="me" href="https://mastodon.world/@WineReleaseBot">Mastodon</a>

This bot uses atproto, Mastodon.py, and Requests to check https://winehq.org for Wine updates, as well as Github for some other Wine-related projects (Proton, Proton GE, and DXVK) and posts the updates on Twitter and Mastodon. Run `pip{3} install -r requirements.txt {--user}` to run the script.

If you wish to adapt this for your own need (I.E. to post website updates), you will need a file in the directory named auth.cred. See the auth.cred.example file for a quick start.

By default the bot will check every hour, but that can be changed via the systemd timer.
