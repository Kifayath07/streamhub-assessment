"""
Standalone demo proving BROKEN_3_WRONG_ID and BROKEN_5_CLASS_NAME
actually fail against the live app, and that their healed counterparts
pass. Not part of the main suite (pytest.ini only points at features/) -
run explicitly with:

    pytest self_healing/test_broken_locators_demo.py -v
"""

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from self_healing.broken_locators import (
    BROKEN_3_WRONG_ID,
    BROKEN_5_CLASS_NAME,
)


@pytest.mark.self_healing_demo
def test_broken_locator_fails_to_find_calculate_button(page, base_url):
    page.goto(f"{base_url}/index.html")
    with pytest.raises(PlaywrightTimeoutError):
        page.locator(BROKEN_3_WRONG_ID).click(timeout=2000)


@pytest.mark.self_healing_demo
def test_healed_locator_finds_calculate_button(page, base_url):
    page.goto(f"{base_url}/index.html")
    page.get_by_test_id("calculate-btn").click(timeout=2000)  # no exception

@pytest.mark.self_healing_demo
def test_broken_locator_matches_ambiguously(page, base_url):
    """
    Discovered during a real local run: this locator doesn't fail with
    "not found" like BROKEN_3 does - CSS :nth-of-type counts position
    among same-tag siblings regardless of class, and every .stat-value
    div genuinely is the 2nd <div> child in its .stat block. So this
    matches all 4 stat values at once, and Playwright's strict mode
    rejects the ambiguity outright.
    """
    page.goto(f"{base_url}/index.html")
    page.get_by_test_id("loan-amount-input").fill("500000")
    page.get_by_test_id("interest-rate-input").fill("8")
    page.get_by_test_id("tenure-input").fill("10")
    page.get_by_test_id("calculate-btn").click()

    count = page.locator(BROKEN_5_CLASS_NAME).count()
    assert count != 1, (
        f"Expected the brittle selector to be ambiguous (not exactly 1 "
        f"match), but got {count}. A locator that isn't pinned to exactly "
        f"one element is broken even when it doesn't throw immediately."
    )
# @pytest.mark.self_healing_demo
# def test_broken_locator_fails_to_find_total_interest(page, base_url):
#     page.goto(f"{base_url}/index.html")
#     page.get_by_test_id("loan-amount-input").fill("500000")
#     page.get_by_test_id("interest-rate-input").fill("8")
#     page.get_by_test_id("tenure-input").fill("10")
#     page.get_by_test_id("calculate-btn").click()

#     with pytest.raises(PlaywrightTimeoutError):
#         page.locator(BROKEN_5_CLASS_NAME).wait_for(state="visible", timeout=2000)


@pytest.mark.self_healing_demo
def test_healed_locator_finds_total_interest(page, base_url):
    page.goto(f"{base_url}/index.html")
    page.get_by_test_id("loan-amount-input").fill("500000")
    page.get_by_test_id("interest-rate-input").fill("8")
    page.get_by_test_id("tenure-input").fill("10")
    page.get_by_test_id("calculate-btn").click()

    page.get_by_test_id("total-interest-result").wait_for(state="visible", timeout=2000)
