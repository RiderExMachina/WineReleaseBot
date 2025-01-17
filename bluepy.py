import requests
from dateteme import datetime, timezone

_DEFAULT_USER_AGENT = "Bsky at Home"

class bksy:
    @staticmethod
    def __init__(self,
                client_id = None,
                app_password = None,
                session = None,
                user_agent = _DEFAULT_USER_AGENT
                )
        self.client_id = client_id
        self.app_password = app_password
        self.session = session

        self.user_agent = user_agent

    def authenticate(self):
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": self.client_id, "password": app_password},
        )
        resp.raise_for_status()
        session = resp.json()
        return self.session = session["accessJwt"]


    def status_post(self, message):
        # Using a trailing "Z" is preferred over the "+00:00" format
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        post = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": now
            }

        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": "Bearer "+ self.session["accessJwt"]},
            json = {
                "repo": self.session["did"],
                "collection": "app.bsky.feed.post",
                "record": post,
            }
        )
        resp.raise_for_status()



