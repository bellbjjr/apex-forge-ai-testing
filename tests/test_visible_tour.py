"""Visible Apex Forge tour: click each navigation tab and scroll each page."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


PAGES = [
    ("Home", "index.html"),
    ("Services", "services.html"),
    ("Our Approach", "approach.html"),
    ("About", "about.html"),
    ("Insights", "insights.html"),
    ("Shop", "shop.html"),
]


def start_local_site():
    site_directory = Path("site-under-test")
    if not (site_directory / "index.html").exists():
        pytest.fail("site-under-test/index.html is missing. Pull the latest repository changes.")
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "http.server",
            "4174",
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
            with socket.create_connection(("127.0.0.1", 4174), timeout=0.2):
                return server
        except OSError:
            time.sleep(0.1)
    server.terminate()
    pytest.fail("The local Apex Forge tour server did not start.")


def scroll_page(driver, pause):
    driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
    time.sleep(pause)
    height = driver.execute_script("return document.documentElement.scrollHeight")
    viewport = driver.execute_script("return window.innerHeight")
    position = 0
    step = max(350, int(viewport * 0.65))
    while position + viewport < height:
        position = min(position + step, height - viewport)
        driver.execute_script(
            "window.scrollTo({top: arguments[0], behavior: 'smooth'});", position
        )
        time.sleep(pause)
    time.sleep(pause)


def test_visible_navigation_and_scroll_tour():
    pause = float(os.environ.get("TOUR_PAUSE_SECONDS", "0.8"))
    server = start_local_site()
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if Path("/usr/bin/chromium").exists():
        options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(options=options)
    artifacts = Path("artifacts/visible-tour")
    artifacts.mkdir(parents=True, exist_ok=True)
    try:
        driver.get("http://127.0.0.1:4174/index.html")
        wait = WebDriverWait(driver, 20)
        wait.until(lambda browser: "APEX FORGE" in browser.find_element(By.TAG_NAME, "body").text.upper())
        for number, (label, filename) in enumerate(PAGES, start=1):
            expected = f"http://127.0.0.1:4174/{filename}"
            if driver.current_url != expected:
                link = wait.until(
                    lambda browser: browser.find_element(
                        By.CSS_SELECTOR, f'nav a[href="{filename}"]'
                    )
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(pause)
                link.click()
                wait.until(lambda browser: browser.current_url == expected)
            print(f"Touring {label}: {driver.current_url}")
            scroll_page(driver, pause)
            driver.save_screenshot(str(artifacts / f"{number:02d}-{filename}.png"))
            driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            time.sleep(pause)
        print("PASS: Visited and scrolled every Apex Forge navigation page.")
    finally:
        driver.quit()
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
