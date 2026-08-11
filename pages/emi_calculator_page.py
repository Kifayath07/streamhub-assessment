"""
Page Object for LoanLens (the EMI Calculator app built for A1).

Locator strategy: every locator here is either a data-testid or a
role/label lookup. Nothing positional (no nth-child, no absolute XPath) -
those live only in self_healing/broken_locators.py as the intentionally
broken examples the assessment asks for.
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class EMICalculatorPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # --- Form locators ---
        self.loan_amount_input = page.get_by_test_id("loan-amount-input")
        self.interest_rate_input = page.get_by_test_id("interest-rate-input")
        self.tenure_input = page.get_by_test_id("tenure-input")
        self.calculate_button = page.get_by_test_id("calculate-btn")
        self.emi_form = page.get_by_test_id("emi-form")

        # --- Report / result locators ---
        self.report_view = page.get_by_test_id("report-view")
        self.empty_state = page.get_by_test_id("empty-state")
        self.emi_result = page.get_by_test_id("emi-result")
        self.principal_result = page.get_by_test_id("principal-result")
        self.total_interest_result = page.get_by_test_id("total-interest-result")
        self.total_payment_result = page.get_by_test_id("total-payment-result")
        self.num_emis_result = page.get_by_test_id("num-emis-result")
        self.breakdown_chart = page.get_by_test_id("breakdown-chart")

    def open(self):
        self.goto("/index.html")

    def fill_loan_details(self, amount: float, rate: float, tenure_years: int):
        self.loan_amount_input.fill(str(amount))
        self.interest_rate_input.fill(str(rate))
        self.tenure_input.fill(str(tenure_years))

    def calculate(self):
        self.calculate_button.click()
        expect(self.emi_result).to_be_visible()

    def get_emi_text(self) -> str:
        return self.emi_result.inner_text()

    def get_total_interest_text(self) -> str:
        return self.total_interest_result.inner_text()

    def get_chart_dataset(self) -> list:
        """
        Pulls the live Chart.js dataset straight out of the page's JS
        context rather than trying to read pixels off the canvas.
        `chartInstance` is a top-level `let` in index.html's script,
        which stays reachable from page.evaluate() since it runs in the
        same page realm.
        """
        return self.page.evaluate("() => chartInstance.data.datasets[0].data")
