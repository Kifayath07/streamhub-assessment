"""
INTENTIONALLY BROKEN LOCATORS - do not import these into the real suite.

Per the assessment brief: 3-5 brittle/incorrect locators, left broken on
purpose, used as the worked examples in SELF_HEALING.md. Each one is
paired with the resilient locator actually used in
pages/emi_calculator_page.py, so you can see exactly what "healing"
looks like in this codebase, not a generic example.
"""

# 1. Positional CSS - breaks the instant a new field is inserted above it,
#    or the grid layout is reordered. No semantic meaning at all.
BROKEN_1_POSITIONAL_CSS = "main > section:nth-child(1) > form > div:nth-child(1) > input"
HEALED_1 = 'page.get_by_test_id("loan-amount-input")'

# 2. Absolute XPath - tied to exact DOM depth. Wrapping the button in a
#    new <div> for styling (very likely during a redesign) silently
#    breaks this with zero warning.
BROKEN_2_ABSOLUTE_XPATH = "/html/body/main/section[1]/form/button"
HEALED_2 = 'page.get_by_test_id("calculate-btn")'

# 3. Guessed ID that doesn't exist in the DOM at all - a common failure
#    mode when a locator is hand-typed from memory/assumption instead of
#    the real markup.
BROKEN_3_WRONG_ID = "#submit-loan-btn"
HEALED_3 = 'page.get_by_test_id("calculate-btn")'

# 4. Text-based locator that's too brittle - breaks the moment copy
#    changes (e.g. "Calculate EMI" -> "Get my EMI"), even though the
#    button's function hasn't changed.
BROKEN_4_BRITTLE_TEXT = 'page.get_by_text("Calculate EMI")'
HEALED_4 = 'page.get_by_test_id("calculate-btn")'

# 5. Class-name locator - Tailwind/utility-class-style names or bundler
#    hashes change on every rebuild, so this fails after almost any CSS
#    refactor even though the element itself never moved.
BROKEN_5_CLASS_NAME = ".stat-value:nth-of-type(2)"
HEALED_5 = 'page.get_by_test_id("total-interest-result")'
