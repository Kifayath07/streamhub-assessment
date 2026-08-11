"""
Step definitions for emi_calculator.feature.

pytest-bdd's `scenarios()` call auto-generates a pytest test function for
every Scenario in the feature file, then matches each Gherkin line below
to the given/when/then step that parses it.
"""

import re
from playwright.sync_api import expect
from pytest_bdd import scenarios, given, when, then, parsers

from pages.emi_calculator_page import EMICalculatorPage

scenarios("../features/emi_calculator.feature")


@given("I am on the EMI calculator page", target_fixture="emi_page")
def navigate_to_calculator(page, base_url):
    emi_page = EMICalculatorPage(page, base_url)
    emi_page.open()
    return emi_page


@when(
    parsers.parse(
        "I enter a loan amount of {amount:d}, interest rate of {rate:g}, and tenure of {years:d} years"
    )
)
def enter_loan_details(emi_page, amount, rate, years):
    emi_page.fill_loan_details(amount, rate, years)


@when("I click the calculate button")
def click_calculate(emi_page):
    emi_page.calculate()


@then("the loan details form should be visible")
def form_is_visible(emi_page):
    expect(emi_page.emi_form).to_be_visible()
    expect(emi_page.loan_amount_input).to_be_visible()
    expect(emi_page.calculate_button).to_be_visible()


@then("the report panel should show its empty state")
def report_shows_empty_state(emi_page):
    expect(emi_page.report_view).to_be_visible()
    expect(emi_page.empty_state).to_be_visible()


@then(parsers.parse('the EMI should be displayed as "{expected_value}"'))
def emi_matches_expected(emi_page, expected_value):
    actual = emi_page.get_emi_text()
    assert actual == expected_value, f"Expected EMI {expected_value!r}, got {actual!r}"


@then(parsers.parse('the total interest should be displayed as "{expected_value}"'))
def total_interest_matches_expected(emi_page, expected_value):
    actual = emi_page.get_total_interest_text()
    assert actual == expected_value, f"Expected total interest {expected_value!r}, got {actual!r}"


@then("the breakdown chart should be visible")
def chart_is_visible(emi_page):
    expect(emi_page.breakdown_chart).to_be_visible()
    box = emi_page.breakdown_chart.bounding_box()
    assert box is not None and box["width"] > 0 and box["height"] > 0, (
        "Chart canvas has zero dimensions - it's not actually rendering"
    )


@then("the chart should show two non-zero data segments")
def chart_has_valid_data(emi_page):
    data = emi_page.get_chart_dataset()
    assert len(data) == 2, f"Expected 2 chart segments (principal, interest), got {len(data)}"
    assert all(value > 0 for value in data), f"Chart contains a zero/invalid segment: {data}"
