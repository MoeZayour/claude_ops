# Clear Browser Cache - Quick Fix

If localStorage quota warnings persist after reload:

## Option 1: Clear Browser LocalStorage (RECOMMENDED)

**Chrome/Edge:**
1. Press `F12` to open Developer Tools
2. Go to **Application** tab
3. Expand **Local Storage** in left sidebar
4. Click on `http://localhost:8089`
5. Right-click → **Clear**
6. Refresh page (`F5`)

**Firefox:**
1. Press `F12` to open Developer Tools  
2. Go to **Storage** tab
3. Expand **Local Storage**
4. Right-click on `http://localhost:8089`
5. Select **Delete All**
6. Refresh page (`F5`)

## Option 2: Hard Refresh (Bypass Cache)

- **Windows/Linux:** `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`

## Option 3: Incognito/Private Window

Open Odoo in a new incognito/private browsing window:
- **Chrome:** `Ctrl + Shift + N`
- **Firefox:** `Ctrl + Shift + P`  
- **Edge:** `Ctrl + Shift + N`

Navigate to: http://localhost:8089

## Verify Fix

After clearing cache, you should see:
```
✓ OPS Matrix Storage Guard initialized
```

WITHOUT the quota exceeded warning.

## Why This Happens

- Base Odoo 19 + OPS Matrix Core + OPS Matrix Accounting = ~40+ menu items
- Browser localStorage limit: typically 5-10MB
- Odoo's menu cache can exceed this on complex installations
- Storage guard automatically manages this, but first load may require manual clear

## Prevention

The storage guard will prevent future issues automatically. This manual clear is typically only needed once after initial installation of multiple modules.
