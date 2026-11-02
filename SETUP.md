# Apex Forge Selenium testing

This project runs visible Chrome remotely. Watch it from your iPad through noVNC.
It is a Selenium smoke-test foundation, not an autonomous AI agent.

## Start from your iPad
1. On this repository select **Code → Codespaces → Create codespace on main**.
2. Wait for the Python dependencies and Docker environment to finish installing.
3. In the Codespaces terminal run:
   `bash scripts/start-browser.sh`
4. Open the **Ports** panel. Forward **7900** if it is not already listed.
   Keep its visibility **Private**, then use **Open in Browser**.
   Do not forward port 4444 publicly.
5. The live viewer asks for a password. Read the generated **.env** file in the
   editor and use the SE_VNC_PASSWORD value. Never commit this file.
6. Return to the terminal and run, replacing the example address:
   `BASE_URL='https://your-apex-forge-site.example' python -m pytest -s -v --html=artifacts/report.html --self-contained-html`
7. Watch the browser in the other Safari tab or iPad multitasking window.
   If your prototype requires account sign-in, complete it in the live browser.
   The script waits up to 180 seconds for Apex Forge content. Change this with
   AUTH_WAIT_SECONDS if necessary. Do not enter passwords in chat or test code.
8. Open **artifacts/report.html** and the PNGs in **artifacts/** to inspect results.

## What the first test checks
- The requested site loads and displays Apex Forge branding.
- A visible same-site navigation link exists (Services is preferred).
- Clicking it reaches the linked URL, and an anchor target exists if applicable.
- Screenshots are captured after verified site content is reached.

This does not yet verify registration, OAuth, checkout, or all service pages.
Authentication blockers and actual test failures are reported as failures, not passes.
If the site's navigation uses buttons instead of links, selectors will need adjustment
after inspecting the running prototype.

## Finish a session
Run `docker compose down`, then stop the Codespace at https://github.com/codespaces.
Stopping browser containers alone does not stop Codespaces compute billing.
Commit source changes you want to retain; artifacts and secrets are ignored.
Codespaces has included quotas and may incur charges beyond them.

## Privacy and future automation
This repository is public. No prototype source, credentials, or session data are included.
Keep reports/screenshots local unless reviewed for publication.
The current Apex Forge prototype may be owner-private; access settings are unchanged.
There is no scheduled CI workflow because private-site authentication must first be resolved.
For future unattended runs, use an authorized staging environment and test accounts.
