# Deploying EnduraForge: GitHub, your phone and your server

These steps assume the repository you already pushed (Salum Tracker) with its GitHub secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `POSTGRES_PASSWORD` and `JWT_SECRET`. Use Git Bash on Windows, or the Terminal on a Mac or Linux.

## 1. Replace the code in your repository

```
cd path/to/salum-tracker
```
Go into the folder you pushed to GitHub before.

```
git pull
```
Get the latest copy from GitHub first.

```
git rm -r -q .
```
Remove the old files from git and from the folder. The hidden `.git` history stays. This clears out files that no longer exist, such as `plan/source`.

Now extract `enduraforge.zip` somewhere else and copy everything inside its `salum-tracker` folder into this folder, including the hidden `.github` folder.

```
git add -A
```
Stage the new files.

```
git status
```
Check the list: you should see the new `docs/` and `server/app/engine/` folders, and files such as `app/lib/home_screen.dart`.

```
git commit -m "EnduraForge 2.0: plan engine, coach, new app"
```
Save the new version.

## 2. Set up the environments on GitHub (once)

In your repository on github.com:

1. **Settings > Environments > New environment**, name it `staging`. No reviewers.
2. **Settings > Environments > production > Required reviewers**: add yourself. Every production deploy then waits for your approval.
3. **Settings > Code security**: turn on Dependabot alerts, secret scanning and CodeQL (code scanning).
4. Optional: separate staging secrets `STAGING_POSTGRES_PASSWORD` and `STAGING_JWT_SECRET` under the staging environment. Without them, staging uses the production values with its own separate database.

## 3. Push and watch

```
git push
```
Upload to GitHub. This starts `deploy`. It runs every check, builds the server image, deploys staging on port 8091, runs smoke tests, then waits for your approval.

```
gh run watch
```
Follow the run in the terminal.

When staging is green, open **Actions > deploy > Review deployments**, tick `production` and approve. Production is backed up, updated on port 8090 and smoke-tested. If anything fails, it rolls back to the previous version by itself.

```
curl http://164.68.97.148:8090/health
```
Check the server: it should show `"ok": true` and `"version": "2.2.0"`.

## 4. Install the new app on your phone

The app is now called **EnduraForge** and installs next to the old Salum Tracker app.

1. Open the old app once with internet on, so its last changes sync to the server.
2. On github.com: **Actions > deploy > (latest run) > Artifacts > enduraforge-apk**. Download it, unzip it, and open the `.apk` on the phone (allow installs from your browser or files app if asked).
3. Open EnduraForge, go to **Profile > Server and sync**, and **Sign in** with your existing email and password. Your logs, results and plan come back.
4. When everything is there, uninstall the old Salum Tracker app.

For a permanent download link, tag a release:

```
git tag v2.2.0
```
Mark this commit as version 2.2.0.

```
git push origin v2.2.0
```
This starts `release`, which attaches the APK to **Releases**.

## 5. Roll back

Automatic rollback happens when a new version fails its checks on the server. To restore any earlier version by hand, go to **Actions > rollback > Run workflow**. Enter the commit SHA you want and choose `production` or `staging`.

```
cat ~/salum-tracker/deployed_images.log
```
On the server: lists every version that was deployed, newest last.

## 6. Backups

```
crontab -e
```
On the server: open the schedule editor. Add this line:

```
0 3 * * * STACK=salum-tracker /root/salum-tracker/backup.sh
```
Takes a database backup every night at 03:00 and keeps 30 days. Production deploys also back up first.

## 7. Run it on your computer (optional)

```
docker compose up --build
```
From the repo root: starts a development API with Postgres at http://localhost:8090/api/docs.

```
cd server
```
Go into the server folder.

```
pip install -r requirements-dev.txt
```
Install the server and test tools.

```
python -m pytest -q
```
Run all server tests.

## 8. Optional: AI-written explanations

Add `AI_BASE_URL`, `AI_API_KEY` and `AI_MODEL` (any OpenAI-compatible chat-completions provider) to the server's `.env` and restart the API. Only `/coach/explain` uses it, and only for wording. The training decisions stay with the rules. With nothing set, the rule-based text is used.
