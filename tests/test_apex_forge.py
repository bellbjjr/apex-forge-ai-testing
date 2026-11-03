"""First smoke test: verify Apex Forge branding and a usable navigation link."""
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def test_apex_forge_homepage_and_navigation():
    target = os.environ.get("BASE_URL", "").strip()
    local_server = None
    if not target:
        site_directory = Path("site-under-test")
        if not (site_directory / "index.html").exists():
            pytest.fail("site-under-test/index.html is missing. Pull the latest repository changes.")
        local_server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "http.server",
                "4173",
                "--bind",
                "127.0.0.1",
                "--directory",
                str(site_directory),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", 4173), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            local_server.terminate()
            pytest.fail("The local Apex Forge test server did not start.")
        target = "http://127.0.0.1:4173/index.html"
    parsed = urlparse(target)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        pytest.fail("Set BASE_URL to the Apex Forge website URL before running.")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if Path("/usr/bin/chromium").exists():
        options.binary_location = "/usr/bin/chromium"
    # Visible Chrome: do not add --headless.
    selenium_url = os.environ.get("SELENIUM_URL", "").strip()
    if selenium_url:
        driver = webdriver.Remote(command_executor=selenium_url, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    verified_homepage = False
    artifacts = Path("artifacts")
    artifacts.mkdir(exist_ok=True)
    try:
        driver.get(target)
        print("If sign-in is required, complete it in the live browser view.")
        def branded_homepage(browser):
            same_origin = (
                urlparse(browser.current_url).scheme,
                urlparse(browser.current_url).netloc,
            ) == (parsed.scheme, parsed.netloc)
            return same_origin and re.search(
                r"apex\s*forge",
                browser.find_element(By.TAG_NAME, "body").text,
                re.IGNORECASE,
            )
        WebDriverWait(driver, int(os.environ.get("AUTH_WAIT_SECONDS", "180"))).until(
            branded_homepage,
            "Apex Forge content was not reached. Check the URL or finish private-site sign-in.",
        )
        verified_homepage = True
        driver.save_screenshot(str(artifacts / "01-homepage.png"))
        # Prefer Services; otherwise exercise a visible same-site navigation link.
        links = driver.find_elements(By.CSS_SELECTOR, "nav a[href], header a[href]")
        candidates = []
        for link in links:
            href = link.get_attribute("href")
            if not href or not link.is_displayed() or not link.text.strip():
                continue
            dest = urlparse(href)
            if dest.scheme not in ("http", "https") or dest.netloc != parsed.netloc:
                continue
            if href.rstrip("/") == driver.current_url.rstrip("/"):
                continue
            candidates.append(link)
        assert candidates, "No visible same-site navigation link was found."
        candidates.sort(key=lambda link: "services" not in link.text.lower())
        selected = candidates[0]
        label = selected.text.strip()
        expected = selected.get_attribute("href")
        time.sleep(float(os.environ.get("DEMO_PAUSE_SECONDS", "2")))
        selected.click()
        WebDriverWait(driver, 20).until(lambda browser: browser.current_url == expected)
        fragment = urlparse(expected).fragment
        if fragment:
            WebDriverWait(driver, 20).until(
                lambda browser: browser.find_element(By.ID, fragment).is_displayed()
            )
        else:
            WebDriverWait(driver, 20).until(
                lambda browser: browser.find_element(By.TAG_NAME, "body").text.strip()
            )
        time.sleep(float(os.environ.get("DEMO_PAUSE_SECONDS", "2")))
        driver.save_screenshot(str(artifacts / "02-navigation.png"))
        print(f"PASS: Apex Forge loaded and navigation '{label}' reached its destination.")
    except Exception:
        # Avoid capturing credentials or a third-party authentication screen.
        if verified_homepage and urlparse(driver.current_url).netloc == parsed.netloc:
            driver.save_screenshot(str(artifacts / "failure.png"))
        raise
    finally:
        driver.quit()
        if local_server is not None:
            local_server.terminate()
            try:
                local_server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                local_server.kill()
