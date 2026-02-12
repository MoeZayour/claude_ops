/** @odoo-module **/
/**
 * OPS Theme - Enhanced Chatter Patch (v1.0.0)
 * ============================================
 * Adds enhanced UX to the Odoo 19 Chatter component:
 *
 * 1. Message Type Quick-Selector — visual icon buttons for Note / Comment / Email
 * 2. Resizable Side Chatter — drag handle for adjusting width when chatter is aside
 * 3. Enhanced Visual Hierarchy — subtle backgrounds and controls
 *
 * Architecture:
 * - Patches Chatter.prototype (from @mail/chatter/web_portal/chatter)
 * - Works alongside chatter_position_patch.js (no conflicts)
 * - State stored in component + localStorage for resize persistence
 *
 * Odoo 19 Chatter has two composerType modes:
 *   'message' = external (Send message, shows recipients)
 *   'note'    = internal (Log note, no recipients)
 *
 * OPS adds a third visual concept:
 *   'note'    = Internal note (sticky note icon)   — maps to Odoo 'note'
 *   'comment' = Comment mode (comment icon)         — maps to Odoo 'note'
 *   'email'   = External email (envelope icon)      — maps to Odoo 'message'
 *
 * Sync Strategy:
 * - Odoo's toggleComposer() is async internally, so we cannot read
 *   state.composerType synchronously after calling super.
 * - Instead, opsChatterState drives the UI, and we use a computed getter
 *   (opsActiveMessageType) that the template reads reactively.
 * - When Odoo's native "Send message" / "Log note" buttons are clicked,
 *   they call toggleComposer() which we intercept to update our state.
 */

import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { useState, onMounted, onWillUnmount } from "@odoo/owl";
import { session } from "@web/session";

const RESIZE_MIN_WIDTH = 280;
const RESIZE_MAX_WIDTH = 700;
const RESIZE_STORAGE_KEY = 'ops_chatter_side_width';

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);

        // Company-level feature toggle
        this._opsChatterEnabled = session.ops_chatter_enhanced !== false;

        // --- OPS Enhanced Chatter State ---
        this.opsChatterState = useState({
            // Visual message type: 'note', 'comment', 'email'
            // This is the "preferred" type that the OPS selector buttons set.
            // 'comment' and 'note' both map to Odoo 'note' composerType.
            // 'email' maps to Odoo 'message' composerType.
            messageType: 'note',
            // Whether the recipients panel is explicitly expanded
            showRecipients: false,
            // Side chatter width from localStorage
            resizeWidth: this._opsGetStoredResizeWidth(),
            // Whether a resize drag is in progress
            isResizing: false,
        });

        // Bound handlers for resize (need stable references for removeEventListener)
        this._boundOnResizeMove = this._opsOnResizeMove.bind(this);
        this._boundOnResizeEnd = this._opsOnResizeEnd.bind(this);

        if (this._opsChatterEnabled) {
            onMounted(() => {
                this._opsApplyStoredWidth();
            });

            onWillUnmount(() => {
                // Clean up any lingering drag listeners
                document.removeEventListener('mousemove', this._boundOnResizeMove);
                document.removeEventListener('mouseup', this._boundOnResizeEnd);
            });
        }
    },

    // =====================================================================
    // Message Type Management
    // =====================================================================

    /**
     * Maps OPS visual message type to Odoo composerType.
     *   'note'    -> 'note'
     *   'comment' -> 'note'
     *   'email'   -> 'message'
     * @param {string} opsType
     * @returns {string}
     */
    _opsTypeToComposerType(opsType) {
        if (opsType === 'email') {
            return 'message';
        }
        return 'note';
    },

    /**
     * Set the OPS message type and activate the corresponding composer.
     * Called from template button clicks in the OPS type selector.
     *
     * @param {string} type - 'note', 'comment', or 'email'
     */
    setMessageType(type) {
        this.opsChatterState.messageType = type;
        this.opsChatterState.showRecipients = (type === 'email');

        const composerType = this._opsTypeToComposerType(type);

        // Always force the composer to the desired mode.
        // If already in this mode, force:true ensures it stays open.
        this.toggleComposer(composerType, { force: true });
    },

    /**
     * Toggle the recipients panel visibility (only meaningful for email type).
     */
    toggleRecipients() {
        if (this.opsChatterState.messageType === 'email') {
            this.opsChatterState.showRecipients = !this.opsChatterState.showRecipients;
        }
    },

    /**
     * Override toggleComposer to keep OPS state in sync.
     *
     * Since Odoo's toggleComposer is async internally (the actual
     * state.composerType assignment happens in a microtask), we predict
     * the resulting composerType based on the same logic Odoo uses:
     *   - if !force and current === mode: will become false (toggle off)
     *   - otherwise: will become mode
     *
     * This lets us sync opsChatterState without waiting for the async
     * inner function to complete.
     *
     * @param {string|false} mode
     * @param {Object} options
     */
    toggleComposer(mode = false, options = {}) {
        const { force = false } = options;

        // Predict what composerType will be after the async toggle resolves
        let predictedType;
        if (!force && this.state.composerType === mode) {
            predictedType = false; // toggling off
        } else {
            predictedType = mode;
        }

        // Sync OPS state based on prediction
        if (predictedType === 'message') {
            this.opsChatterState.messageType = 'email';
            this.opsChatterState.showRecipients = true;
        } else if (predictedType === 'note') {
            // If coming from 'email', reset to 'note'.
            // If already 'note' or 'comment', keep current selection.
            if (this.opsChatterState.messageType === 'email') {
                this.opsChatterState.messageType = 'note';
            }
            this.opsChatterState.showRecipients = false;
        } else {
            // Composer being closed (predictedType === false)
            this.opsChatterState.showRecipients = false;
        }

        // Call super AFTER updating OPS state so the UI is ready
        super.toggleComposer(mode, options);
    },

    // =====================================================================
    // Resize Handle for Side Chatter
    // =====================================================================

    /**
     * Read stored width from localStorage, with fallback.
     * @returns {number}
     */
    _opsGetStoredResizeWidth() {
        try {
            const stored = localStorage.getItem(RESIZE_STORAGE_KEY);
            if (stored) {
                const val = parseInt(stored, 10);
                if (val >= RESIZE_MIN_WIDTH && val <= RESIZE_MAX_WIDTH) {
                    return val;
                }
            }
        } catch (e) {
            // localStorage not available
        }
        return 360;
    },

    /**
     * Apply the stored width to the chatter DOM element (side mode only).
     */
    _opsApplyStoredWidth() {
        if (!this.props.isChatterAside || !this.rootRef.el) {
            return;
        }
        const width = this.opsChatterState.resizeWidth;
        const el = this.rootRef.el;
        el.style.width = width + 'px';
        el.style.minWidth = width + 'px';
        el.style.maxWidth = width + 'px';
    },

    /**
     * Start a resize drag operation.
     * @param {MouseEvent} ev
     */
    onResizeStart(ev) {
        if (!this.props.isChatterAside) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();

        this.opsChatterState.isResizing = true;
        this._resizeStartX = ev.clientX;
        this._resizeStartWidth = this.opsChatterState.resizeWidth;

        document.addEventListener('mousemove', this._boundOnResizeMove);
        document.addEventListener('mouseup', this._boundOnResizeEnd);

        // Prevent text selection during drag
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';
    },

    /**
     * Handle mouse move during resize.
     * Chatter is on the right side, so dragging LEFT increases its width.
     * @param {MouseEvent} ev
     */
    _opsOnResizeMove(ev) {
        if (!this.opsChatterState.isResizing) {
            return;
        }
        const delta = this._resizeStartX - ev.clientX;
        let newWidth = this._resizeStartWidth + delta;
        newWidth = Math.max(RESIZE_MIN_WIDTH, Math.min(RESIZE_MAX_WIDTH, newWidth));

        this.opsChatterState.resizeWidth = newWidth;

        if (this.rootRef.el) {
            const el = this.rootRef.el;
            el.style.width = newWidth + 'px';
            el.style.minWidth = newWidth + 'px';
            el.style.maxWidth = newWidth + 'px';
        }
    },

    /**
     * End the resize drag and persist the width to localStorage.
     */
    _opsOnResizeEnd() {
        this.opsChatterState.isResizing = false;

        document.removeEventListener('mousemove', this._boundOnResizeMove);
        document.removeEventListener('mouseup', this._boundOnResizeEnd);

        // Restore normal cursor and selection
        document.body.style.userSelect = '';
        document.body.style.cursor = '';

        // Persist to localStorage
        try {
            localStorage.setItem(RESIZE_STORAGE_KEY, String(this.opsChatterState.resizeWidth));
        } catch (e) {
            // localStorage not available
        }
    },
});
