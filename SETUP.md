# Apex Forge Selenium testing

This project runs visible Chrome remotely. Watch it from your iPad through noVNC.
It is a Selenium smoke-test foundation, not an autonomous AI agent.

## Start from your iPad
1. On this repository select **Code → Codespaces → Create codespace on main**.
2. Wait for Chromium, noVNC, and the Python dependencies to finish installing.
   The live browser service starts automatically.
3. If the service does not start automatically, run:
   `bash scripts/start-browser.sh`
4. Open the **Ports** panel. Forward **7900** if it is not already listed.
   Keep its visibility **Private**, then use **Open in Browser**.
5. The live viewer asks for a password. Read the generated **.env** file in the
   editor and use the SE_VNC_PASSWORD value. Never commit this file.
6. Return to the terminal and run:
   `python -m pytest tests/test_apex_forge.py -s -v --html=artifacts/report.html --self-contained-html`
   The test automatically starts the bundled Apex Forge testing copy. To test another
   authorized website, set `BASE_URL` explicitly.
7. Watch the browser in the other Safari tab or iPad multitasking window.
   The bundled testing copy has no ChatGPT sign-in or human-verification gate.
   Do not enter passwords in chat or test code.
8. Open **artifacts/report.html** and the PNGs in **artifacts/** to inspect results.

## Watch the full navigation and scrolling tour
Run this test while the noVNC viewer is open:
`python -m pytest tests/test_visible_tour.py -s -v`

The tour visits Home, Services, Our Approach, About, Insights, and Shop. It
scrolls through each page, returns to the top, and continues to the next tab.
Slow it down by adding, for example, `TOUR_PAUSE_SECONDS=1.5` before the command.
Screenshots are saved in `artifacts/visible-tour/`.

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
Stop the Codespace at https://github.com/codespaces when finished.
Commit source changes you want to retain; artifacts and secrets are ignored.
Codespaces has included quotas and may incur charges beyond them.

## Privacy and future automation
This repository is public. No prototype source, credentials, or session data are included.
Keep reports/screenshots local unless reviewed for publication.
The current Apex Forge prototype may be owner-private; access settings are unchanged.
There is no scheduled CI workflow because private-site authentication must first be resolved.
For future unattended runs, use an authorized staging environment and test accounts.
