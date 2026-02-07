"""
One-time helper to obtain Strava OAuth2 tokens.

Run this script once to authorize the app and get your .env credentials:

    uv run python strava_auth.py

Prerequisites:
  1. Create a Strava API application at https://www.strava.com/settings/api
  2. Set the "Authorization Callback Domain" to "localhost"
  3. Note your Client ID and Client Secret
"""

import http.server
import urllib.parse
import webbrowser

import httpx

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
REDIRECT_URI = "http://localhost:8000"
SCOPES = "read,activity:read"


def main():
    client_id = input("Enter your Strava Client ID: ").strip()
    client_secret = input("Enter your Strava Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Client ID and Client Secret are required.")
        return

    # Open browser for authorization
    auth_url = (
        f"{STRAVA_AUTH_URL}"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=force"
        f"&scope={SCOPES}"
    )
    print("\nOpening browser for authorization...")
    print(f"If the browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for the callback
    auth_code = None

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authorization successful!</h1>"
                    b"<p>You can close this tab and return to the terminal.</p>"
                )
            else:
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                error = params.get("error", ["unknown"])[0]
                self.wfile.write(f"<h1>Authorization failed: {error}</h1>".encode())

        def log_message(self, format, *args):
            pass  # suppress request logs

    server = http.server.HTTPServer(("localhost", 8000), Handler)
    print("Waiting for authorization callback on http://localhost:8000 ...")
    server.handle_request()
    server.server_close()

    if not auth_code:
        print("Failed to get authorization code.")
        return

    # Exchange code for tokens
    print("Exchanging authorization code for tokens...")
    resp = httpx.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    athlete_id = data["athlete"]["id"]
    refresh_token = data["refresh_token"]

    print("\n" + "=" * 50)
    print("Copy the following into your .env file:")
    print("=" * 50)
    print(f"STRAVA_CLIENT_ID={client_id}")
    print(f"STRAVA_CLIENT_SECRET={client_secret}")
    print(f"STRAVA_REFRESH_TOKEN={refresh_token}")
    print(f"STRAVA_ATHLETE_ID={athlete_id}")
    print("=" * 50)


if __name__ == "__main__":
    main()
