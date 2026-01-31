/** @odoo-module **/

import { useState, useEffect, onWillStart } from '@odoo/owl';
import { browser } from '@web/core/browser/browser';
import { patch } from '@web/core/utils/patch';
import { ControlPanel } from '@web/search/control_panel/control_panel';

/**
 * OPS Theme - Control Panel Auto-Refresh
 *
 * Adds an auto-refresh feature to list and kanban views.
 * Users can toggle auto-refresh which will periodically refresh the view.
 */
patch(ControlPanel.prototype, {
    setup() {
        super.setup(...arguments);

        this.autoRefreshState = useState({
            active: false,
            counter: 0,
            interval: 30, // seconds
        });

        onWillStart(() => {
            if (this._checkAutoRefreshAvailable() && this._getStoredAutoRefresh()) {
                this.autoRefreshState.active = true;
            }
        });

        useEffect(
            () => {
                if (!this.autoRefreshState.active) {
                    return;
                }

                this.autoRefreshState.counter = this.autoRefreshState.interval;

                const intervalId = browser.setInterval(() => {
                    this.autoRefreshState.counter--;

                    if (this.autoRefreshState.counter <= 0) {
                        this.autoRefreshState.counter = this.autoRefreshState.interval;
                        this._triggerRefresh();
                    }
                }, 1000);

                return () => browser.clearInterval(intervalId);
            },
            () => [this.autoRefreshState.active]
        );
    },

    /**
     * Check if auto-refresh is available for current view type
     */
    _checkAutoRefreshAvailable() {
        const viewType = this.env.config?.viewType;
        return ['kanban', 'list'].includes(viewType);
    },

    /**
     * Get unique storage key for current action/view combination
     */
    _getStorageKey() {
        const keys = [
            this.env.config?.actionId ?? '',
            this.env.config?.viewType ?? '',
        ];
        return `ops_auto_refresh:${keys.join(',')}`;
    },

    /**
     * Get stored auto-refresh preference
     */
    _getStoredAutoRefresh() {
        return browser.localStorage.getItem(this._getStorageKey()) === 'true';
    },

    /**
     * Store auto-refresh preference
     */
    _setStoredAutoRefresh(value) {
        if (value) {
            browser.localStorage.setItem(this._getStorageKey(), 'true');
        } else {
            browser.localStorage.removeItem(this._getStorageKey());
        }
    },

    /**
     * Trigger a refresh of the current view
     */
    _triggerRefresh() {
        // Try different methods to refresh the view
        if (this.pagerProps?.onUpdate) {
            this.pagerProps.onUpdate({
                offset: this.pagerProps.offset,
                limit: this.pagerProps.limit,
            });
        } else if (this.env.searchModel?.search) {
            this.env.searchModel.search();
        }
    },

    /**
     * Toggle auto-refresh on/off
     */
    toggleAutoRefresh() {
        this.autoRefreshState.active = !this.autoRefreshState.active;
        this._setStoredAutoRefresh(this.autoRefreshState.active);
    },
});
