# OPS Theme Complete Enhancement Specification

## Overview

This specification outlines the implementation of 6 major features to enhance OPS Theme with advanced UI/UX capabilities while maintaining its superior branding and corporate identity strengths.

## Target Features

1. **Sidebar/AppsBar** — Collapsible navigation with app icons
2. **Applications Home Screen** — Enhanced grid layout for app selection  
3. **Dialog Enhancements** — Fullscreen toggle for all dialogs
4. **Enhanced Chatter** — External/Internal buttons, recipients list
5. **Group Controls** — Expand/Collapse All in list/kanban views
6. **Auto-Refresh** — Configurable view refresh with countdown

## Architecture Principles

- **Single Module Approach**: Keep all features within `ops_theme` module
- **OPS Branding First**: Integrate with existing OPS color system and theme skins
- **Dark Mode Compatible**: All features must work in both light and dark modes
- **User Preferences**: Leverage existing OPS user preference system
- **Settings Integration**: Add controls to existing OPS Settings page

---

## Implementation Summary

### Database Schema Changes

**New Fields in `res.users`**:
```python
# Sidebar preferences
ops_sidebar_type = fields.Selection([
    ('invisible', 'Hidden'),
    ('small', 'Small Icons'), 
    ('large', 'Large Icons')
], default='large')

ops_sidebar_position = fields.Selection([
    ('left', 'Left Side'),
    ('right', 'Right Side')
], default='left')

# Dialog preferences
ops_dialog_size = fields.Selection([
    ('normal', 'Normal'),
    ('fullscreen', 'Fullscreen')
], default='normal')

# Home menu preferences
ops_home_view_mode = fields.Selection([
    ('grid', 'Grid View'),
    ('list', 'List View'), 
    ('tiles', 'Tile View')
], default='grid')
```

**New Fields in `res.company`**:
```python
# Sidebar branding
ops_sidebar_logo = fields.Binary(
    string='Sidebar Footer Logo',
    attachment=True,
    help='Logo displayed at bottom of sidebar (120x40px recommended)'
)

# Feature toggles
ops_sidebar_enabled = fields.Boolean(default=True)
ops_home_menu_enhanced = fields.Boolean(default=True)
ops_dialog_enhancements = fields.Boolean(default=True)
ops_chatter_enhanced = fields.Boolean(default=True)
ops_group_controls_enabled = fields.Boolean(default=True)
ops_auto_refresh_enabled = fields.Boolean(default=False)
```

### File Structure

```
addons/ops_theme/
├── static/src/
│   ├── js/
│   │   ├── ops_sidebar.js                    # Sidebar component
│   │   ├── ops_webclient_patch.js           # WebClient integration
│   │   ├── ops_home_menu.js                 # Enhanced home menu
│   │   ├── ops_dialog_patch.js              # Dialog fullscreen toggle
│   │   ├── ops_chatter_patch.js             # Enhanced chatter
│   │   ├── ops_group_controls.js            # Group expand/collapse
│   │   ├── ops_group_controls_component.js  # Group controls component
│   │   └── ops_auto_refresh.js              # Auto-refresh functionality
│   ├── scss/
│   │   ├── _ops_sidebar.scss                # Sidebar styling
│   │   ├── _ops_sidebar.dark.scss           # Sidebar dark mode
│   │   ├── _ops_home_menu.scss              # Home menu styling
│   │   ├── _ops_home_menu.dark.scss         # Home menu dark mode
│   │   ├── _ops_dialog.scss                 # Dialog enhancements
│   │   ├── _ops_dialog.dark.scss            # Dialog dark mode
│   │   ├── _ops_chatter.scss                # Chatter enhancements
│   │   ├── _ops_chatter.dark.scss           # Chatter dark mode
│   │   ├── _ops_auto_refresh.scss           # Auto-refresh styling
│   │   └── _ops_auto_refresh.dark.scss      # Auto-refresh dark mode
│   └── xml/
│       ├── ops_sidebar.xml                  # Sidebar templates
│       ├── ops_home_menu.xml                # Home menu templates
│       ├── ops_dialog.xml                   # Dialog templates
│       ├── ops_chatter.xml                  # Chatter templates
│       ├── ops_group_controls.xml           # Group controls templates
│       └── ops_auto_refresh.xml             # Auto-refresh templates
```

---

## Feature Specifications

### 1. Sidebar/AppsBar

**Core Functionality**:
- Collapsible sidebar with app icons and labels
- Three size modes: Large (200px), Small (60px), Hidden (0px)
- User preference persistence
- Company logo in footer
- Active app highlighting
- Mobile responsive (overlay on small screens)

**Key Components**:
- `OpsSidebar` component with app navigation
- CSS Grid layout for main content adjustment
- Toggle button with smooth animations
- Integration with existing OPS color system

### 2. Applications Home Screen

**Core Functionality**:
- Enhanced app grid with search functionality
- Three view modes: Grid, List, Tiles
- Category filtering (if app categories defined)
- Responsive layouts for all screen sizes
- Integration with existing HomeMenu

**Key Features**:
- Search bar with real-time filtering
- View mode toggle buttons
- Category dropdown filter
- Enhanced app cards with descriptions
- Smooth hover animations

### 3. Dialog Enhancements

**Core Functionality**:
- Fullscreen toggle button in dialog header
- User preference for default dialog size
- Smooth transition animations
- Works with all dialog types (forms, wizards, etc.)

**Key Features**:
- Expand/compress icon toggle
- Keyboard shortcut support (F11)
- Automatic preference saving
- Mobile-friendly fullscreen mode

### 4. Enhanced Chatter

**Core Functionality**:
- Message type selector (Note, Comment, Email)
- Recipients panel for email messages
- Resizable side chatter
- Enhanced UI with better visual hierarchy

**Key Features**:
- External/Internal/Email message buttons
- Recipients list with badges
- Drag-to-resize functionality
- Integration with existing position toggle

### 5. Group Controls

**Core Functionality**:
- Expand All / Collapse All buttons in cog menu
- Works with both List and Kanban views
- Handles nested groups recursively
- Only visible when view is grouped

**Key Features**:
- Added to existing cog menu
- Batch operations for performance
- Visual feedback during operations
- Keyboard shortcuts (Ctrl+E, Ctrl+C)

### 6. Auto-Refresh

**Core Functionality**:
- Configurable auto-refresh intervals
- Visual countdown timer
- Per-view preference persistence
- Manual refresh override

**Key Features**:
- Interval selector (10s, 30s, 1m, 5m, 10m)
- Pause/resume functionality
- Visual pulse animation when active
- Smart refresh (only when view is visible)

---

## Settings Integration

### New Settings Section: "User Interface Enhancements"

```xml
<group string="User Interface Enhancements" name="ui_enhancements">
    <!-- Sidebar Settings -->
    <field name="ops_sidebar_enabled"/>
    <field name="ops_sidebar_default_type" 
           attrs="{'invisible': [('ops_sidebar_enabled', '=', False)]}"/>
    <field name="ops_sidebar_position" 
           attrs="{'invisible': [('ops_sidebar_enabled', '=', False)]}"/>
    
    <!-- Home Menu Settings -->
    <field name="ops_home_menu_enhanced"/>
    <field name="ops_home_menu_default_view" 
           attrs="{'invisible': [('ops_home_menu_enhanced', '=', False)]}"/>
    
    <!-- Dialog Settings -->
    <field name="ops_dialog_enhancements"/>
    <field name="ops_dialog_default_size" 
           attrs="{'invisible': [('ops_dialog_enhancements', '=', False)]}"/>
    
    <!-- Chatter Settings -->
    <field name="ops_chatter_enhanced"/>
    <field name="ops_chatter_show_recipients" 
           attrs="{'invisible': [('ops_chatter_enhanced', '=', False)]}"/>
    
    <!-- Group Controls -->
    <field name="ops_group_controls_enabled"/>
    
    <!-- Auto-Refresh -->
    <field name="ops_auto_refresh_enabled"/>
    <field name="ops_auto_refresh_default_interval" 
           attrs="{'invisible': [('ops_auto_refresh_enabled', '=', False)]}"/>
</group>
```

---

## Dark Mode Compatibility

All new features include dedicated `.dark.scss` files following the established pattern:

- `_ops_sidebar.dark.scss` — Dark sidebar colors and hover states
- `_ops_home_menu.dark.scss` — Dark app cards and search controls
- `_ops_dialog.dark.scss` — Dark dialog button styling
- `_ops_chatter.dark.scss` — Dark chatter controls and panels
- `_ops_auto_refresh.dark.scss` — Dark refresh button states

**Dark Mode Principles**:
- Use CSS custom properties where possible (`var(--body-bg)`, `var(--body-color)`)
- No `!important` declarations in dark files
- Maintain visual hierarchy in dark theme
- Test all interactive states (hover, active, focus)

---

## Manifest Updates

### Asset Bundle Changes

```python
'web.assets_backend': [
    # Existing files...
    
    # New SCSS files
    'ops_theme/static/src/scss/_ops_sidebar.scss',
    'ops_theme/static/src/scss/_ops_home_menu.scss', 
    'ops_theme/static/src/scss/_ops_dialog.scss',
    'ops_theme/static/src/scss/_ops_chatter.scss',
    'ops_theme/static/src/scss/_ops_auto_refresh.scss',
    
    # Exclude dark files from backend bundle
    ('remove', 'ops_theme/static/src/scss/_ops_sidebar.dark.scss'),
    ('remove', 'ops_theme/static/src/scss/_ops_home_menu.dark.scss'),
    ('remove', 'ops_theme/static/src/scss/_ops_dialog.dark.scss'),
    ('remove', 'ops_theme/static/src/scss/_ops_chatter.dark.scss'),
    ('remove', 'ops_theme/static/src/scss/_ops_auto_refresh.dark.scss'),
    
    # New JavaScript files
    'ops_theme/static/src/js/ops_sidebar.js',
    'ops_theme/static/src/js/ops_webclient_patch.js',
    'ops_theme/static/src/js/ops_home_menu.js',
    'ops_theme/static/src/js/ops_dialog_patch.js',
    'ops_theme/static/src/js/ops_chatter_patch.js',
    'ops_theme/static/src/js/ops_group_controls.js',
    'ops_theme/static/src/js/ops_group_controls_component.js',
    'ops_theme/static/src/js/ops_auto_refresh.js',
    
    # New XML templates
    'ops_theme/static/src/xml/ops_sidebar.xml',
    'ops_theme/static/src/xml/ops_home_menu.xml',
    'ops_theme/static/src/xml/ops_dialog.xml',
    'ops_theme/static/src/xml/ops_chatter.xml',
    'ops_theme/static/src/xml/ops_group_controls.xml',
    'ops_theme/static/src/xml/ops_auto_refresh.xml',
],

'web.assets_web_dark': [
    # Existing dark files...
    
    # New dark mode files
    'ops_theme/static/src/scss/_ops_sidebar.dark.scss',
    'ops_theme/static/src/scss/_ops_home_menu.dark.scss',
    'ops_theme/static/src/scss/_ops_dialog.dark.scss', 
    'ops_theme/static/src/scss/_ops_chatter.dark.scss',
    'ops_theme/static/src/scss/_ops_auto_refresh.dark.scss',
],
```

### Version Update

```python
'version': '19.0.17.0.0',  # Updated from 19.0.16.0.0
```

---

## Implementation Phases

### Phase A: Foundation (Week 1)
- [ ] Update database schema (user and company fields)
- [ ] Create base JavaScript components structure
- [ ] Set up SCSS file structure with dark mode files
- [ ] Update manifest.py with new assets

### Phase B: Sidebar Implementation (Week 1-2)
- [ ] Implement OpsSidebar component
- [ ] Create sidebar templates and styling
- [ ] Add WebClient integration
- [ ] Implement user preferences
- [ ] Test responsive behavior

### Phase C: Home Menu Enhancement (Week 2)
- [ ] Patch HomeMenu component
- [ ] Add search and filtering functionality
- [ ] Implement view mode toggles
- [ ] Create responsive grid layouts
- [ ] Test with various app configurations

### Phase D: Dialog Enhancements (Week 3)
- [ ] Patch Dialog component
- [ ] Add fullscreen toggle button
- [ ] Implement smooth transitions
- [ ] Add user preference saving
- [ ] Test with all dialog types

### Phase E: Chatter Enhancement (Week 3-4)
- [ ] Patch Chatter component
- [ ] Add message type selector
- [ ] Implement recipients panel
- [ ] Add resize functionality
- [ ] Integrate with existing position toggle

### Phase F: Group Controls (Week 4)
- [ ] Patch List and Kanban controllers
- [ ] Create group control components
- [ ] Add to cog menu registry
- [ ] Implement batch operations
- [ ] Test with nested groups

### Phase G: Auto-Refresh (Week 4-5)
- [ ] Patch ControlPanel component
- [ ] Implement timer functionality
- [ ] Add interval configuration UI
- [ ] Create countdown display
- [ ] Add localStorage persistence

### Phase H: Settings Integration (Week 5)
- [ ] Add all settings fields to res.config.settings
- [ ] Update settings view with new sections
- [ ] Implement settings validation
- [ ] Add help text and tooltips
- [ ] Test settings persistence

### Phase I: Testing & Polish (Week 5-6)
- [ ] Comprehensive feature testing
- [ ] Dark mode compatibility verification
- [ ] Mobile responsiveness testing
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Documentation updates

---

## Success Criteria

### Functional Requirements
- ✅ All 6 features implemented and working
- ✅ User preferences properly saved and restored
- ✅ Settings page integration complete
- ✅ Dark mode fully compatible
- ✅ Mobile responsive design
- ✅ No conflicts with existing OPS features

### Performance Requirements
- ✅ Page load time increase < 100ms
- ✅ Memory usage increase < 50MB
- ✅ Smooth animations (60fps)
- ✅ No JavaScript errors in console

### Quality Requirements
- ✅ Code follows OPS Theme patterns
- ✅ All features configurable via Settings
- ✅ Comprehensive error handling
- ✅ Accessibility compliance (WCAG 2.1)
- ✅ Cross-browser compatibility

---

## Risk Mitigation

### Technical Risks
1. **Odoo Core Changes**: Use `patch()` instead of overrides to minimize breaking changes
2. **Performance Impact**: Implement lazy loading and efficient DOM manipulation
3. **Mobile Compatibility**: Test on actual devices, not just browser dev tools
4. **Dark Mode Issues**: Create comprehensive dark mode test suite

### User Experience Risks
1. **Feature Overload**: Make all features optional with sensible defaults
2. **Learning Curve**: Provide clear visual cues and help text
3. **Preference Conflicts**: Implement preference validation and fallbacks

### Deployment Risks
1. **Database Migration**: Test upgrade path thoroughly
2. **Asset Conflicts**: Use precise asset ordering with `('after', ...)` directives
3. **Cache Issues**: Implement proper cache busting for new assets

---

## Estimated Timeline: 5-6 weeks
## Estimated Effort: 120-150 hours  
## Target Version: 19.0.17.0.0

## Next Steps

1. **Review and Approve Specification** — Stakeholder sign-off
2. **Set Up Development Environment** — Create feature branch
3. **Begin Phase A Implementation** — Database schema and foundation
4. **Weekly Progress Reviews** — Track against timeline
5. **User Testing Sessions** — Gather feedback during development
6. **Final Integration Testing** — Comprehensive QA before release

This specification provides a complete roadmap for transforming OPS Theme into a comprehensive, modern Odoo theme that rivals the best commercial themes while maintaining its unique corporate branding strengths.