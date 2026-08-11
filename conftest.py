"""
Shared fixtures.

Design choice worth explaining in an interview: BASE_URL is never
hardcoded into test files. If it's set in .env, tests point at that
(e.g. a deployed/staging build). If it's NOT set, this file spins up a
throwaway local static server for the webapp/ folder built in A1, so the
suite is runnable out-of-the-box with zero manual setup.
"""

import os
import sys
import threading
import http.server
import functools

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "..", "webapp")


@pytest.fixture(scope="session")
def base_url():
    env_url = os.getenv("BASE_URL")
    if env_url:
        yield env_url.rstrip("/")
        return

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=WEBAPP_DIR
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    server.server_close()


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser_name = os.getenv("BROWSER", "chromium")
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser_type = getattr(playwright_instance, browser_name)
    browser = browser_type.launch(headless=headless)
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
