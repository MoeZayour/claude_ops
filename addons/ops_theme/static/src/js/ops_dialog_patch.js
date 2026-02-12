/** @odoo-module **/
/**
 * OPS Theme - Dialog Fullscreen Toggle
 * =====================================
 * Adds an expand/compress toggle button to every Dialog header.
 * Clicking it switches the dialog between normal and fullscreen mode
 * (100vw x 100vh, no margin, no border-radius).
 *
 * Architecture:
 * - Patches Dialog.prototype to add reactive fullscreen state
 * - State persisted in localStorage (key: 'ops_dialog_fullscreen')
 * - F11 keyboard shortcut toggles fullscreen when a dialog is open
 * - Adds 'ops-dialog-fullscreen' CSS class to the .modal element
 * - Does NOT interfere with Odoo's native isFullscreen/o_modal_full
 *   (which is driven by props.fullscreen or env.isSmall for mobile)
 *
 * Odoo 19 Dialog structure:
 *   .o_dialog > .modal[.o_technical_modal][.o_modal_full] > .modal-dialog > .modal-content
 *   - isFullscreen getter: props.fullscreen || env.isSmall
 *   - When isFullscreen: header shows back-arrow, hides close button
 *   - We do NOT want that behavior — we keep the normal header
 */

import { patch } from "@web/core/utils/patch";
import { Dialog } from "@web/core/dialog/dialog";
import { useState, onMounted, onWillUnmount } from "@odoo/owl";
import { session } from "@web/session";

const OPS_FS_KEY = "ops_dialog_fullscreen";

patch(Dialog.prototype, {
    setup() {
        super.setup(...arguments);

        // Company-level feature toggle
        if (session.ops_dialog_enhancements === false) {
            this.opsFullscreen = useState({ active: false });
            return;
        }

        // Reactive fullscreen state, persisted via localStorage
        this.opsFullscreen = useState({
            active: localStorage.getItem(OPS_FS_KEY) === "true",
        });

        // F11 keyboard handler — scoped to this dialog instance
        this._opsHandleKeydown = (ev) => {
            // Only respond when THIS dialog is the active one
            if (!this.data.isActive) {
                return;
            }
            if (ev.key === "F11") {
                ev.preventDefault();
                ev.stopPropagation();
                this.toggleOpsFullscreen();
            }
        };

        onMounted(() => {
            document.addEventListener("keydown", this._opsHandleKeydown, true);
        });

        onWillUnmount(() => {
            document.removeEventListener("keydown", this._opsHandleKeydown, true);
        });
    },

    /**
     * Toggle the OPS fullscreen state and persist to localStorage.
     * Also resets the drag position to prevent offset glitches when
     * switching between normal and fullscreen modes.
     */
    toggleOpsFullscreen() {
        this.opsFullscreen.active = !this.opsFullscreen.active;
        localStorage.setItem(OPS_FS_KEY, this.opsFullscreen.active ? "true" : "false");
        // Reset drag position to avoid offset when toggling modes
        if (this.position) {
            this.position.left = 0;
            this.position.top = 0;
        }
    },

    /**
     * Icon class for the toggle button.
     */
    get opsFullscreenIcon() {
        return this.opsFullscreen.active ? "fa-compress" : "fa-expand";
    },

    /**
     * Tooltip text for the toggle button.
     */
    get opsFullscreenTitle() {
        return this.opsFullscreen.active ? "Exit Fullscreen" : "Toggle Fullscreen";
    },

    /**
     * Whether the dialog enhancement feature is enabled.
     */
    get opsDialogEnabled() {
        return session.ops_dialog_enhancements !== false;
    },
});
