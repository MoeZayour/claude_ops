/** @odoo-module **/

/**
 * OPS Theme v2.0 - Interactions Module
 *
 * Adds micro-interactions like ripple effects to buttons and other
 * interactive elements for a more engaging user experience.
 */

// =============================================================================
// RIPPLE EFFECT
// =============================================================================
// Add Material Design-inspired ripple effect to buttons

document.addEventListener('click', (e) => {
    const target = e.target.closest('.btn, button[type="submit"], .o_kanban_button');
    if (!target) return;

    // Skip if disabled
    if (target.disabled || target.classList.contains('disabled')) return;

    // Create ripple element
    const ripple = document.createElement('span');
    ripple.classList.add('ops-ripple-effect');

    const rect = target.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    // Determine ripple color based on button type
    let rippleColor = 'rgba(255, 255, 255, 0.3)';
    if (target.classList.contains('btn-secondary') ||
        target.classList.contains('btn-light') ||
        target.classList.contains('btn-outline-primary') ||
        target.classList.contains('btn-link')) {
        rippleColor = 'rgba(0, 0, 0, 0.1)';
    }

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: ${rippleColor};
        border-radius: 50%;
        transform: scale(0);
        animation: ops-ripple-animation 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;

    // Ensure button has correct positioning
    const computedStyle = window.getComputedStyle(target);
    if (computedStyle.position === 'static') {
        target.style.position = 'relative';
    }
    target.style.overflow = 'hidden';

    target.appendChild(ripple);

    // Clean up after animation
    setTimeout(() => ripple.remove(), 600);
});

// =============================================================================
// INJECT RIPPLE ANIMATION KEYFRAMES
// =============================================================================

const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes ops-ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .ops-ripple-effect {
        will-change: transform, opacity;
    }
`;
document.head.appendChild(styleSheet);

// =============================================================================
// ENHANCED FOCUS STATES
// =============================================================================
// Add focus ring animation for better accessibility feedback

document.addEventListener('focusin', (e) => {
    const target = e.target;
    if (target.matches('input, textarea, select, button, .btn, [tabindex]')) {
        target.classList.add('ops-focus-visible');
    }
});

document.addEventListener('focusout', (e) => {
    const target = e.target;
    target.classList.remove('ops-focus-visible');
});

// =============================================================================
// SCROLL REVEAL (with proper cleanup)
// =============================================================================
// Subtle animation when elements come into view

let scrollObserver = null;
let domObserver = null;
let observerCleanupTimeout = null;

function initScrollReveal() {
    // Only run in web client
    if (!document.querySelector('.o_web_client')) {
        return;
    }

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('ops-visible');
                scrollObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    domObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType !== Node.ELEMENT_NODE) return;

                // Observe kanban cards
                const kanbanCards = node.querySelectorAll ?
                    node.querySelectorAll('.o_kanban_record') : [];
                kanbanCards.forEach(card => {
                    card.classList.add('ops-scroll-reveal');
                    scrollObserver.observe(card);
                });

                // Check if node itself is a kanban card
                if (node.classList && node.classList.contains('o_kanban_record')) {
                    node.classList.add('ops-scroll-reveal');
                    scrollObserver.observe(node);
                }
            });
        });
    });

    domObserver.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Auto-cleanup DOM observer after 60 seconds to prevent memory leaks
    // (page should be fully loaded by then, scroll observer continues working)
    observerCleanupTimeout = setTimeout(() => {
        if (domObserver) {
            domObserver.disconnect();
            domObserver = null;
            console.log('[OPS Theme] DOM observer auto-cleanup after 60s');
        }
    }, 60000);
}

function cleanupScrollReveal() {
    if (observerCleanupTimeout) {
        clearTimeout(observerCleanupTimeout);
        observerCleanupTimeout = null;
    }
    if (scrollObserver) {
        scrollObserver.disconnect();
        scrollObserver = null;
    }
    if (domObserver) {
        domObserver.disconnect();
        domObserver = null;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollReveal);
} else {
    initScrollReveal();
}

// Cleanup on page unload to prevent memory leaks
window.addEventListener('beforeunload', cleanupScrollReveal);

// Add scroll reveal styles
const scrollRevealStyles = document.createElement('style');
scrollRevealStyles.textContent = `
    .ops-scroll-reveal {
        opacity: 0;
        transform: translateY(10px);
        transition: opacity 0.3s ease, transform 0.3s ease;
    }

    .ops-scroll-reveal.ops-visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Reduce motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        .ops-scroll-reveal {
            opacity: 1;
            transform: none;
            transition: none;
        }
    }
`;
document.head.appendChild(scrollRevealStyles);

// =============================================================================
// TOOLTIP ENHANCEMENT
// =============================================================================
// Add subtle animation to tooltips

const tooltipStyles = document.createElement('style');
tooltipStyles.textContent = `
    .tooltip {
        animation: ops-tooltip-in 0.15s ease;
    }

    @keyframes ops-tooltip-in {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(tooltipStyles);

// =============================================================================
// BUTTON LOADING STATE HELPER
// =============================================================================
// Utility to add loading state to buttons

window.OPSTheme = window.OPSTheme || {};
window.OPSTheme.setButtonLoading = function(button, loading = true) {
    if (loading) {
        button.classList.add('ops-loading');
        button.dataset.originalText = button.textContent;
        button.disabled = true;
    } else {
        button.classList.remove('ops-loading');
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
            delete button.dataset.originalText;
        }
        button.disabled = false;
    }
};

console.log('[OPS Theme] Interactions module loaded');
