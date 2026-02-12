# OPS Skin Design Guide v1.0
## For Designers & Brand Teams

### What is a Skin?
A skin is a set of 10 hex colors + 1 navbar style that completely re-themes
the entire Odoo ERP interface. When applied, every button, border, background,
sidebar, navbar, form, list, and status indicator updates to match.

### The 10 Colors You Need to Provide

#### Group 1: Identity (2 colors)
These define your brand presence across the application.

| # | Name             | Purpose                              | Contrast Requirement           |
|---|------------------|--------------------------------------|--------------------------------|
| 1 | **Brand Color**  | Navbar background, sidebar,          | Must have 4.5:1 ratio with     |
|   | (`primary_color`)| headings accent                      | white text (#ffffff)            |
| 2 | **Action Color** | All interactive elements: buttons,   | Must have 4.5:1 ratio with     |
|   | (`secondary_color`)| links, focus rings, selected items,| white text AND be visually      |
|   |                  | toggle switches, progress bars       | distinct from Brand Color       |

#### Group 2: Semantic Status (4 colors)
Universal meaning — users learn these once. Change hue, not meaning.

| # | Name      | Meaning                    | Where It Appears                   |
|---|-----------|----------------------------|------------------------------------|
| 3 | **Success** | Positive / confirmed / done | checkmarks, approved badges,     |
|   |           |                            | .btn-success, profit indicators    |
| 4 | **Warning** | Caution / needs attention   | alerts, pending states,            |
|   |           |                            | .btn-warning, overdue badges       |
| 5 | **Danger**  | Error / destructive / loss  | delete buttons, error messages,    |
|   |           |                            | .btn-danger, loss indicators       |
| 6 | **Info**    | Informational / neutral     | tooltips, help text, .btn-info,    |
|   |           |                            | count badges                       |

#### Group 3: Canvas (4 colors)
These define the physical space — like walls, floors, and furniture.

| # | Name        | Purpose                          | Constraint                       |
|---|-------------|----------------------------------|----------------------------------|
| 7 | **Background** | Page bg behind everything     | Must contrast with Surface       |
|   | (`bg_color`)  |                               | (min 2:1 visible difference)     |
| 8 | **Surface**    | Cards, forms, modals, panels  | Usually white or near-white.     |
|   | (`surface_color`)|                              | Must contrast with Background    |
| 9 | **Text**       | All body text and labels      | Must have 7:1 ratio with Surface |
|   | (`text_color`) |                               | (WCAG AAA for readability)       |
|10 | **Border**     | Dividers, table lines, inputs | Subtle — between Background      |
|   | (`border_color`)|                              | and Text in lightness            |

#### Navbar Style (1 setting)
| Option    | Visual Effect                              | Best For                    |
|-----------|--------------------------------------------|-----------------------------|
| `dark`    | Brand Color bg + white text                | Dark brand colors (#1e293b) |
| `light`   | White bg + dark text + bottom border       | When brand is too light     |
| `primary` | Action Color bg + white text               | Bold, colorful headers      |

### Skin Template (Copy & Fill)

```xml
<record id="skin_YOUR_NAME" model="ops.theme.skin">
    <field name="name">Your Skin Name</field>
    <field name="tag">Category Tag</field>
    <field name="sequence">50</field>
    <!-- Identity -->
    <field name="primary_color">#______</field>   <!-- Brand Color -->
    <field name="secondary_color">#______</field>  <!-- Action Color -->
    <!-- Semantic -->
    <field name="success_color">#______</field>
    <field name="warning_color">#______</field>
    <field name="danger_color">#______</field>
    <field name="info_color">#______</field>
    <!-- Canvas -->
    <field name="bg_color">#______</field>
    <field name="surface_color">#______</field>
    <field name="text_color">#______</field>
    <field name="border_color">#______</field>
    <!-- Structure -->
    <field name="navbar_style">dark</field>
</record>
```

### Color Derivation Chain

Your 10 colors cascade into 50+ Bootstrap/Odoo variables automatically:

```
Brand Color (#1e293b)
  -> $o-brand-odoo (replaces Odoo purple)
  -> $o-navbar-background (navbar bar color)
  -> $ops_sidebar_bg (sidebar background)
  -> $ops_headings_color (h1-h6 color)
  -> $o-community-color, $o-enterprise-color

Action Color (#3b82f6)
  -> $o-brand-primary (THE primary color for Bootstrap)
  -> $o-action (all interactive states)
  -> $o-main-link-color (all <a> links)
  -> $o-input-border-required (required field borders)
  -> .btn-primary background
  -> .o_kanban_record active border
  -> .o_searchview focus ring
  -> All focus-visible outlines

Background (#f1f5f9)
  -> $body-bg
  -> $o-webclient-background-color
  -> $o-gray-100 (lightest gray)

Surface (#ffffff)
  -> $o-view-background-color
  -> card backgrounds, modal backgrounds
  -> form sheet backgrounds

Text (#1e293b)
  -> $body-color
  -> $o-main-text-color
  -> $o-gray-900 (darkest gray)
  -> All intermediate grays auto-calculated

Border (#e2e8f0)
  -> $border-color (Bootstrap global)
  -> $o-gray-200
  -> table borders, input borders, dividers
```

### Design Rules for Good Skins

1. **Brand Color must support white text.** Test at https://webaim.org/resources/contrastchecker/ — Brand as bg, #ffffff as foreground. Must pass AA (4.5:1).

2. **Action Color must be vivid.** It's the "do something" color. Saturated blues, teals, greens work. Avoid grays or dark colors — they'll make buttons invisible.

3. **Semantic colors should be universally recognizable.** Green=good, yellow/orange=caution, red=bad, blue/teal=info. Don't make success red or danger green.

4. **Background and Surface need visible difference.** If bg=#ffffff and surface=#ffffff, cards vanish. Typical gap: bg is 3-5% darker than surface.

5. **Text must be dark on light surface.** WCAG AAA requires 7:1 ratio. #1e293b on #ffffff = 14.5:1. #94a3b8 on #ffffff = 3.0:1 (fails).

6. **Border should be subtle.** It's the lightest structural element. Typically 10-15% darker than background.

### Existing Skins as Reference

| Skin               | Brand    | Action   | Bg       | Surface  | Navbar |
|---------------------|----------|----------|----------|----------|--------|
| Corporate Blue      | #1e293b  | #3b82f6  | #f1f5f9  | #ffffff  | dark   |
| Clean Light         | #334155  | #0ea5e9  | #ffffff  | #f8fafc  | light  |
| Enterprise Navy     | #0f172a  | #2563eb  | #f8fafc  | #ffffff  | dark   |
| Warm Professional   | #292524  | #d97706  | #fafaf9  | #ffffff  | dark   |

### Field Name to SCSS Variable Mapping

| Model Field       | SCSS Variable       | Odoo Variable Mapped To             |
|-------------------|---------------------|-------------------------------------|
| `primary_color`   | `$ops_color_brand`  | `$o-brand-odoo`, navbar bg          |
| `secondary_color` | `$ops_color_primary`| `$o-brand-primary`, `$o-action`     |
| `success_color`   | `$ops_color_success`| `$o-success`                        |
| `warning_color`   | `$ops_color_warning`| `$o-warning`                        |
| `danger_color`    | `$ops_color_danger` | `$o-danger`                         |
| `info_color`      | `$ops_color_info`   | `$o-info`                           |
| `bg_color`        | `$ops_color_bg`     | `$o-webclient-background-color`     |
| `surface_color`   | `$ops_color_surface`| `$o-view-background-color`          |
| `text_color`      | `$ops_color_text`   | `$o-main-text-color`, `$o-gray-900` |
| `border_color`    | `$ops_color_border` | `$o-gray-200`, `$border-color`      |

Note: `primary_color` maps to **brand** (not Odoo's primary). `secondary_color` maps to Odoo's **primary/action** color. This naming was chosen because from the user's perspective, the navbar/brand color IS the "primary" identity color.
