/**
 * A Supabase storage adapter that uses cookies for session management,
 * making the session available for server-side rendering (SSR) in Flask.
 */
const supabaseCookieAdapter = {
    getItem: (key) => {
        const match = document.cookie.match(new RegExp('(^| )' + key + '=([^;]+)'));
        if (match) {
            return decodeURIComponent(match[2]);
        }
        return null;
    },
    setItem: (key, value) => {
        // Set the cookie to be accessible from the root path, and make it secure
        // if the site is served over HTTPS. The max-age is set to 1 year.
        document.cookie = `${key}=${encodeURIComponent(value)}; path=/; max-age=31536000; SameSite=Lax; ${window.location.protocol === 'https:' ? 'Secure;' : ''}`;
    },
    removeItem: (key) => {
        // To remove a cookie, we set its expiration date to a past time.
        document.cookie = `${key}=; path=/; max-age=0; SameSite=Lax; ${window.location.protocol === 'https:' ? 'Secure;' : ''}`;
    },
};

// Expose the adapter to the global window object so supabaseClient.js can use it.
window.supabaseCookieAdapter = supabaseCookieAdapter;