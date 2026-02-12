/** @odoo-module **/
/**
 * OPS Auto-Refresh Systray Component
 *
 * Adds a configurable auto-refresh timer to the systray (top-right navbar).
 *
 * Features:
 *  - Configurable intervals: Off, 10s, 30s, 1m, 5m, 10m
 *  - Visual countdown badge showing seconds until next refresh
 *  - Pause/resume by clicking the countdown
 *  - Smart refresh: only fires when browser tab is visible
 *  - Persists interval per-action to localStorage
 *  - Refresh uses Odoo's action.restore() for a clean soft-reload
 */

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useDropdownState } from "@web/core/dropdown/dropdown_hooks";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { router } from "@web/core/browser/router";
import { session } from "@web/session";

const STORAGE_PREFIX = "ops_auto_refresh_";

const INTERVAL_OPTIONS = [
    { label: "Off", value: 0 },
    { label: "10 seconds", value: 10 },
    { label: "30 seconds", value: 30 },
    { label: "1 minute", value: 60 },
    { label: "5 minutes", value: 300 },
    { label: "10 minutes", value: 600 },
];

export class OpsAutoRefresh extends Component {
    static template = "ops_theme.OpsAutoRefresh";
    static components = { Dropdown };
    static props = [];

    setup() {
        this.actionService = useService("action");
        this.dropdown = useDropdownState();

        this.state = useState({
            interval: 0,       // 0 = off, else seconds
            countdown: 0,      // seconds remaining
            isPaused: false,   // user paused
            isActive: false,   // countdown actively running
        });

        this.intervalOptions = INTERVAL_OPTIONS;
        this._tickTimer = null;
        this._tabHidden = false;

        // Visibility API handler
        this._onVisibilityChange = this._onVisibilityChange.bind(this);

        onMounted(() => {
            this._restoreFromStorage();
            document.addEventListener("visibilitychange", this._onVisibilityChange);
        });

        onWillUnmount(() => {
            this._clearTick();
            document.removeEventListener("visibilitychange", this._onVisibilityChange);
        });
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    /**
     * Whether auto-refresh is enabled at company level.
     */
    get isEnabled() {
        return session.ops_auto_refresh_enabled !== false;
    }

    /**
     * Build a storage key based on the current action.
     * Falls back to a generic key if no action is identifiable.
     */
    get _storageKey() {
        const current = router.current;
        const actionId = current.action || current.actionId || "global";
        return `${STORAGE_PREFIX}${actionId}`;
    }

    /**
     * Format the countdown for display.
     * Shows MM:SS for values >= 60, otherwise just the number.
     */
    get countdownDisplay() {
        const s = this.state.countdown;
        if (s >= 60) {
            const min = Math.floor(s / 60);
            const sec = s % 60;
            return `${min}:${String(sec).padStart(2, "0")}`;
        }
        return String(s);
    }

    /**
     * Human-readable label for the currently active interval.
     */
    get activeLabel() {
        const opt = this.intervalOptions.find((o) => o.value === this.state.interval);
        return opt ? opt.label : "Off";
    }

    // -------------------------------------------------------------------------
    // Actions
    // -------------------------------------------------------------------------

    /**
     * Called when user selects an interval from the dropdown.
     */
    onSelectInterval(value) {
        this.state.interval = value;
        this.state.isPaused = false;

        if (value === 0) {
            this._stop();
        } else {
            this._start(value);
        }

        this._saveToStorage();
        this.dropdown.close();
    }

    /**
     * Toggle pause/resume on the countdown.
     */
    onTogglePause(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        if (!this.state.isActive) return;

        this.state.isPaused = !this.state.isPaused;
        if (this.state.isPaused) {
            this._clearTick();
        } else {
            this._startTick();
        }
    }

    /**
     * Manual immediate refresh button.
     */
    onManualRefresh(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this._doRefresh();
    }

    // -------------------------------------------------------------------------
    // Internal: Timer management
    // -------------------------------------------------------------------------

    _start(seconds) {
        this._clearTick();
        this.state.countdown = seconds;
        this.state.isActive = true;
        this.state.isPaused = false;
        this._startTick();
    }

    _stop() {
        this._clearTick();
        this.state.countdown = 0;
        this.state.isActive = false;
        this.state.isPaused = false;
    }

    _startTick() {
        this._clearTick();
        this._tickTimer = setInterval(() => this._tick(), 1000);
    }

    _clearTick() {
        if (this._tickTimer) {
            clearInterval(this._tickTimer);
            this._tickTimer = null;
        }
    }

    _tick() {
        if (this.state.isPaused || this._tabHidden) {
            return;
        }

        this.state.countdown -= 1;

        if (this.state.countdown <= 0) {
            this._doRefresh();
            // Reset countdown for the next cycle
            this.state.countdown = this.state.interval;
        }
    }

    // -------------------------------------------------------------------------
    // Internal: Refresh logic
    // -------------------------------------------------------------------------

    /**
     * Perform a soft reload of the current action.
     * Uses Odoo's action service restore() which re-renders the current
     * controller without a full page reload.
     */
    async _doRefresh() {
        try {
            const controller = this.actionService.currentController;
            if (controller) {
                await this.actionService.restore(controller.jsId);
            }
        } catch (e) {
            // Silently ignore refresh errors (e.g., if user navigated away).
            // The timer will continue and try again next cycle.
            console.warn("[OPS Auto-Refresh] Refresh failed:", e.message);
        }
    }

    // -------------------------------------------------------------------------
    // Internal: Visibility API
    // -------------------------------------------------------------------------

    _onVisibilityChange() {
        this._tabHidden = document.hidden;
        // When tab becomes visible again and timer is active + not paused,
        // ensure the tick is running.
        if (!this._tabHidden && this.state.isActive && !this.state.isPaused) {
            if (!this._tickTimer) {
                this._startTick();
            }
        }
    }

    // -------------------------------------------------------------------------
    // Internal: localStorage persistence
    // -------------------------------------------------------------------------

    _saveToStorage() {
        try {
            const key = this._storageKey;
            if (this.state.interval === 0) {
                localStorage.removeItem(key);
            } else {
                localStorage.setItem(key, JSON.stringify({
                    interval: this.state.interval,
                }));
            }
        } catch {
            // localStorage may be unavailable; silently ignore.
        }
    }

    _restoreFromStorage() {
        try {
            const key = this._storageKey;
            const raw = localStorage.getItem(key);
            if (raw) {
                const data = JSON.parse(raw);
                if (data.interval && data.interval > 0) {
                    this.state.interval = data.interval;
                    this._start(data.interval);
                }
            }
        } catch {
            // Corrupted or unavailable storage; start with defaults.
        }
    }
}

registry
    .category("systray")
    .add("ops_theme.auto_refresh", { Component: OpsAutoRefresh }, { sequence: 5 });
