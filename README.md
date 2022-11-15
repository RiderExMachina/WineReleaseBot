# Wine Release Bot

TL;DR - See the bot in action on [Twitter](https://twitter.com/WineReleaseBot) or [Mastodon](https://botsin.space/@WineReleaseBot)

This bot uses Tweepy, Mastodon.py, BeautifulSoup, and Requests to check https://winehq.org for Wine updates, as well as Github for some other Wine-related projects (Proton, Proton GE, and DXVK) and posts the updates on Twitter and Mastodon. Run `pip{3} install -r requirements.txt {--user}` to run the script.

If you wish to adapt this for your own need (I.E. to post website updates), you will need a file in the directory named auth.cred. See the auth.cred.example file for a quick start.

By default the bot will check every hour, but you can change that in the designated spot.



#### Hardships for newbies

If you wish to have a dedicated Twitter bot make the account first and sign it up for a developer account. It should be accepted right away. Then make your app, get your tokens and place them in twitter-auth.cred.

Same thing on Mastodon but that takes much less time.
