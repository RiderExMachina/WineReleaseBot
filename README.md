# Wine Release Bot

TL;DR - See the bot in action at https://twitter.com/WineReleaseBot and https://botsin.space/@WineReleaseBot

This bot uses Tweepy, Mastodon.py, BeutifulSoup, and Requests to check https://winehq.org for wine updates and posts the updates on Twitter and Mastodon. Run `pip{3} install -r requirements.txt {--user}` to run the script.

If you wish to adapt this for your own need (I.E. to post website updates), you will need two files in the directory named twitter-auth.cred and mast-auth.cred. See the {twitter,mast}-auth.cred.example files for a quick start.

By default the bot will check every 3 hours, but you can change that in the designated spot.



#### Hardships for newbies

If you wish to have a dedicated Twitter bot make the account first and sign it up for a developer account. It should be accepted right away. Then make your app, get your tokens and place them in twitter-auth.cred.

Same thing on Mastodon but that takes much less time.
