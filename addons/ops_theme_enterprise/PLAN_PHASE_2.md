# 📋 OPS Enterprise Theme - Phase 2 Roadmap

**Status:** Ready for Execution (Waiting for Phase 1 Logic Fix)
**Target:** "Gilded" Polish + App Grid
**Key Decision:** Stick to Top Bar Navigation (No Sidebar).

---

## 🚀 Priority 1: The App Grid (Launchpad)
**Objective:** Replace the default "List Menu" on the home screen with a modern "App Grid" (Icons).
* **Current Behavior:** Odoo CE defaults to a text list for the main menu.
* **Target Behavior:** When clicking the "Home" logo, show a grid of colorful App Icons (Sales, Inventory, Accounting) similar to Enterprise Edition.
* **Technical Path:**
    * Override `web.webclient` templates.
    * CSS Grid layout for `.o_apps` container.
    * Ensure icons are centered and use the "Card" aesthetic (White background, Shadow).

## 🎨 Priority 2: Login Screen Branding
**Objective:** "Split Screen" Professional Login.
* **Design:**
    * **Left Half:** High-quality abstract brand image (Deep Navy/Blue geometry).
    * **Right Half:** Clean login form with OPS Logo.
* **Code:** Inherit `web.login` template. Remove Odoo footer branding.

## 📄 Priority 3: PDF Report Styling
**Objective:** Professional "Gilded" Documents.
* **Fonts:** Enforce clean Sans-Serif (Inter/Roboto) on PDFs.
* **Header:** Deep Navy Background (`#0f172a`) with White Text.
* **Tables:** Zebra striping (Grey/White) for line items.
* **Footer:** Minimalist legal text.

## 🛑 Out of Scope
* **Left Sidebar:** We are sticking to the Top Bar for stability and mobile compatibility.