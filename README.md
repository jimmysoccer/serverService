# serverService

## Canvas to Google Tasks authentication

The sync uses an OAuth refresh token so the deployed backend can run without an
interactive browser. Authorize it once on a local machine from the `backend`
directory:

```powershell
python authorize_google_tasks.py
```

This opens Google consent and writes `backend/token.json`. The file is ignored
by Git and must never be committed. For local use, the sync reads that file
automatically.

For App Engine or another stateless deployment, store the complete contents of
`token.json` as the secret environment variable `GOOGLE_TOKEN_JSON`. The code
can refresh its access token from this value on every new instance; it does not
need to persist the short-lived access token.

To prevent the refresh token from expiring every seven days, open Google Cloud
Console, select the OAuth project, go to **Google Auth Platform > Audience**, and
change **Publishing status** from **Testing** to **In production**. Then run the
authorization command once more and replace the deployed `GOOGLE_TOKEN_JSON`
secret with the newly generated token. A refresh token can still require
reauthorization if access is revoked or it remains unused for a long period.

Optional configuration:

- `GOOGLE_TOKEN_PATH`: local token file path (defaults to `backend/token.json`)
- `GOOGLE_CREDENTIALS_PATH`: desktop OAuth client file path (defaults to
  `backend/credentials.json`)

The `/canvas_sync/sync` endpoint now returns HTTP 401 with a useful message when
Google needs reauthorization, instead of attempting a localhost browser flow
inside the deployed server and returning a generic successful response.
