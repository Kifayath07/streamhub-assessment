Feature: EMI Calculator
  As a borrower using LoanLens
  I want to calculate my monthly EMI
  So that I can plan my loan repayment with confidence

  Background:
    Given I am on the EMI calculator page

  Scenario: Dashboard loads correctly on first visit
    Then the loan details form should be visible
    And the report panel should show its empty state

  Scenario: Calculating EMI produces the correct value
    When I enter a loan amount of 1000000, interest rate of 9.5, and tenure of 15 years
    And I click the calculate button
    Then the EMI should be displayed as "₹10,442"
    And the total interest should be displayed as "₹8,79,604"

  Scenario: Calculating EMI for a smaller, shorter loan
    When I enter a loan amount of 500000, interest rate of 8, and tenure of 5 years
    And I click the calculate button
    Then the EMI should be displayed as "₹10,138"

  Scenario: Breakdown chart renders with valid, non-zero data
    When I enter a loan amount of 500000, interest rate of 8, and tenure of 10 years
    And I click the calculate button
    Then the breakdown chart should be visible
    And the chart should show two non-zero data segments
