/**
 * CSRF Protection Helper
 *
 * This script automatically adds CSRF tokens to all AJAX requests.
 * Include this script in all HTML pages that make API calls.
 */

(function() {
    'use strict';

    /**
     * Get CSRF token from meta tag
     */
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }

        // Fallback: try to get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return decodeURIComponent(value);
            }
        }

        return null;
    }

    /**
     * Wrap the original fetch to automatically include CSRF token
     */
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Only add CSRF token for same-origin requests
        const isSameOrigin = !url.startsWith('http') || url.startsWith(window.location.origin);

        if (isSameOrigin) {
            // Add CSRF token for methods that modify data
            const method = (options.method || 'GET').toUpperCase();
            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
                const csrfToken = getCSRFToken();

                if (csrfToken) {
                    // Ensure headers object exists
                    options.headers = options.headers || {};

                    // Convert headers to object if it's a Headers instance
                    if (options.headers instanceof Headers) {
                        const headersObj = {};
                        options.headers.forEach((value, key) => {
                            headersObj[key] = value;
                        });
                        options.headers = headersObj;
                    }

                    // Add CSRF token header
                    options.headers['X-CSRFToken'] = csrfToken;

                    // For JSON requests, also add to header (Flask-WTF checks both)
                    if (options.headers['Content-Type'] &&
                        options.headers['Content-Type'].includes('application/json')) {
                        options.headers['X-CSRF-Token'] = csrfToken;
                    }
                }
            }
        }

        return originalFetch(url, options);
    };

    /**
     * Helper function to manually get CSRF token (for custom use cases)
     */
    window.getCSRFToken = getCSRFToken;

    console.log('CSRF protection initialized');
})();
