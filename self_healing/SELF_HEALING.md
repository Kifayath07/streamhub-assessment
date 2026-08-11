# Self-healing locators

Five brittle/incorrect locators are intentionally left broken in
[`broken_locators.py`](./broken_locators.py), each paired with the resilient
locator actually used in `pages/emi_calculator_page.py`. Two of them
(`BROKEN_3_WRONG_ID`, `BROKEN_5_CLASS_NAME`) are proven to fail live against
the app in [`test_broken_locators_demo.py`](./test_broken_locators_demo.py) -
this isn't just a written exercise, the failures are real and reproducible.

## The loop

**1. Detection**
A locator doesn't fail because the element vanished - almost always
something *around* it shifted: a wrapper `<div>` got added during a
styling pass, a class name changed after a CSS refactor, or the DOM
depth changed. The signal is a Playwright `TimeoutError` on
`locator.wait_for()` or `.click()`. The important discipline here: don't
treat every timeout as "heal this" - a genuinely down environment or a
slow network also throws a `TimeoutError`. Only escalate to healing after
confirming the *page itself* loaded fine and the target region of the DOM
is present, just not matching the old selector.

**2. Prompt approach**
Once a real break is confirmed, three things go into the prompt - not
just "here's the DOM, fix it":
- The **broken locator string** itself
- The **element's intent** in plain English (what it's *for*, not how it
  was found) - e.g. "the button that calculates and displays the EMI"
- A **scoped DOM snapshot** of the relevant region (not the whole page -
  keeps the model focused and the token cost down)

The model is instructed to respond only with role/label/`data-testid`
based locators (matching this project's existing convention) and to
return structured JSON (`suggested_locator` + one-line `reasoning`), so
the output is directly machine-parseable instead of prose you'd have to
manually interpret.

**3. Validation before applying**
This is the step that's easy to skip and shouldn't be. The AI's
suggestion is *never* written directly into a test file. Instead:
- The suggested locator is tried against the **live page**
- It must resolve to **exactly one** element (not zero, not several)
- It must actually be **visible**

Only if all three hold does the suggestion get treated as viable - and
even then, the intended workflow is to open it as a PR diff for a human
to review, not to auto-commit it. An AI-suggested locator that happens to
match one element isn't proof it's the *correct* element; a reviewer
still needs to eyeball that the reasoning matches intent.

## Worked example (see `self_heal_poc.py` for the runnable version)

| | |
|---|---|
| Broken | `#submit-loan-btn` |
| Detected | `TimeoutError` waiting for visibility |
| Intent given to model | "The button that calculates and displays the EMI after the loan form is filled in" |
| Suggested fix | `page.get_by_test_id("calculate-btn")` |
| Validation | Resolves to 1 element, visible → **accepted** |

## What I'd actually change before trusting this in a real CI pipeline

- Rate-limit/cache healing attempts per locator so a genuinely broken
  build doesn't burn API calls retrying the same failure on every run
- Require the PR-diff step to be non-optional - never let a healed
  locator land without a human approving the semantic match, only the
  structural validity
- Track how often a "healed" locator breaks *again* soon after - a
  locator that keeps needing healing is usually a sign the app's markup
  itself is unstable and that's worth raising with dev, not just
  patching around forever

  ## A real correction from running this locally

`BROKEN_5_CLASS_NAME` (`.stat-value:nth-of-type(2)`) was originally
written expecting it to fail with "element not found." Running the
suite for real showed something different: it matched **4 elements**
instead of 0, because CSS `:nth-of-type` counts position among
same-tag siblings regardless of class - and every `.stat-value` div
happens to be the 2nd `<div>` child inside its `.stat` block. Playwright's
strict mode caught the ambiguity and threw instead of silently picking
one. The demo test was rewritten to assert on `locator.count() != 1`
rather than assuming a specific exception type.
