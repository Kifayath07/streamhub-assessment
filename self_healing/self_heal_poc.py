"""
Working POC for the self-healing exercise.

Loop implemented here, matching SELF_HEALING.md:
  1. DETECT   - try the broken locator, catch the timeout
  2. SNAPSHOT - grab the relevant DOM region so the model has real context
  3. PROMPT   - ask an LLM for a resilient replacement + its reasoning
  4. VALIDATE - actually try the suggested locator against the live page
               before ever writing it back into a test file
  5. REPORT   - print a diff-style suggestion for a human to review/approve

Run with:
    ANTHROPIC_API_KEY=sk-... python self_healing/self_heal_poc.py

Requires the local server + a broken locator - this script starts its
own throwaway server so it can run standalone, outside of pytest.
"""

import os
import sys
import json
import functools
import http.server
import threading

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "webapp")
BROKEN_LOCATOR = "#submit-loan-btn"  # BROKEN_3_WRONG_ID from broken_locators.py
INTENT = "The button that calculates and displays the EMI after the loan form is filled in."


def start_local_server():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=WEBAPP_DIR)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{port}"


def detect_failure(page, broken_locator: str) -> bool:
    """Step 1: confirm the locator is actually broken (not a flake)."""
    try:
        page.locator(broken_locator).wait_for(state="visible", timeout=2000)
        return False  # it worked, nothing to heal
    except PlaywrightTimeoutError:
        return True


def snapshot_relevant_dom(page) -> str:
    """Step 2: grab a scoped DOM region, not the whole page, to keep the
    prompt small and the model's attention on what matters."""
    return page.evaluate('() => document.querySelector("main").outerHTML')


def ask_ai_for_fix(broken_locator: str, intent: str, dom_snapshot: str) -> dict:
    """Step 3: prompt an LLM for a resilient replacement + reasoning.
    Forces JSON so the result is directly parseable, not free text."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[skip] ANTHROPIC_API_KEY not set - showing the prompt that would be sent:\n")
        print(build_prompt(broken_locator, intent, dom_snapshot))
        sys.exit(0)

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": build_prompt(broken_locator, intent, dom_snapshot)}],
        },
        timeout=30,
    )
    response.raise_for_status()
    text = response.json()["content"][0]["text"]
    return json.loads(text)


def build_prompt(broken_locator: str, intent: str, dom_snapshot: str) -> str:
    return f"""A Playwright locator broke: {broken_locator}
Its intent: {intent}

Current DOM of the relevant region:
{dom_snapshot}

Suggest a replacement locator using Playwright's role/label/data-testid
strategies only - never positional CSS or absolute XPath. Respond with
ONLY a JSON object, no markdown fences, no preamble:
{{"suggested_locator": "page.get_by_test_id(\\"...\\")", "reasoning": "one sentence"}}
"""


def validate_fix(page, suggested_locator_code: str) -> bool:
    """Step 4: never trust the suggestion blindly - actually try it
    against the live page, and require it resolve to exactly one
    element, before it's allowed anywhere near the real test files."""
    try:
        locator = eval(suggested_locator_code, {"page": page})
        count = locator.count()
        if count != 1:
            print(f"[reject] Suggested locator matched {count} elements, expected exactly 1.")
            return False
        locator.wait_for(state="visible", timeout=2000)
        return True
    except Exception as e:
        print(f"[reject] Suggested locator failed validation: {e}")
        return False


def main():
    server, base_url = start_local_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{base_url}/index.html")

            if not detect_failure(page, BROKEN_LOCATOR):
                print("Locator still works - nothing to heal.")
                return

            print(f"[detected] '{BROKEN_LOCATOR}' does not resolve to any element.\n")

            dom_snapshot = snapshot_relevant_dom(page)
            fix = ask_ai_for_fix(BROKEN_LOCATOR, INTENT, dom_snapshot)

            print(f"[suggested] {fix['suggested_locator']}")
            print(f"[reasoning] {fix['reasoning']}\n")

            if validate_fix(page, fix["suggested_locator"]):
                print("[validated] Suggested locator resolves to exactly 1 visible element.")
                print("[action] Would open a PR replacing the broken locator - NOT auto-committing.")
            else:
                print("[rejected] Suggestion did not pass validation - would flag for manual review.")

            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
