# Test Findings - What's Actually Happening

## Issue 1: Always Light Mode

**Observation**: Theme is always in light mode, toggle doesn't work.

**Hypothesis**:
1. Cookie is not being set on initial page load from database
2. Toggle function is not setting the cookie properly
3. Odoo's cookie reading happens BEFORE our JS runs

**Need to check**:
- Is `color_scheme` cookie present in browser? (Check DevTools)
- Does toggle actually set the cookie?
- Does page reload read the cookie?

## Issue 2: Chatter Only Moves Based on Screen Size

**Observation**: Chatter moves to bottom only when NOT fullscreen (automatic behavior).

**Hypothesis**:
1. Our `mailLayout()` patch is not being applied
2. Or patch is applied but falling through to `super.mailLayout()`
3. Or patch runs after form is already compiled

**Need to check**:
- Is `chatter_position_patch.js` loading?
- Is the patch actually modifying `FormRenderer.prototype.mailLayout`?
- What does `session.ops_chatter_position` contain?

## Critical Realization

Odoo 19 might NOT have a built-in cookie system for color_scheme at all!

The references I found (`cookie.get("color_scheme")`) might just be checking IF a cookie exists, but Odoo doesn't SET it automatically.

This means:
- We need to SET the cookie ourselves on every page load
- We need to SET it from the template (server-side) OR from JS init
- The toggle needs to SET the cookie AND save to database
