import requests
from dateteme import datetime, timezone

_DEFAULT_USER_AGENT = "Bsky at Home"

class bksy():
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

        if session:
            self.session
        else:
            self.session = requests.Session()

        self.user_agent = user_agent

    def authenticate(self):
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
        )
        resp.raise_for_status()
        session = resp.json()
        print(session["accessJwt"])


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
            headers={"Authorization": "Bearer "+ session["accessJwt"]},
            json = {
                "repo": session["did"],
                "collection": "app.bsky.feed.post",
                "record": post,
            }
        )
        response = json.dumps(resp.json(), indent=2)
        post_validation = response['validationStatus']
        if post_validation = "valid":

        resp.raise_for_status()



