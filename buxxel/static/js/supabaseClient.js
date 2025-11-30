// A custom storage adapter that uses cookies for server-side rendering (SSR)
// and falls back to localStorage for client-side operations.
const cookieStorageAdapter = {
    getItem: (key) => {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(key + '=')) {
                return cookie.substring(key.length + 1);
            }
        }
        // Fallback to localStorage if cookie is not found
        return localStorage.getItem(key);
    },
    setItem: (key, value) => {
        // Set in both cookie and localStorage
        const expirationDate = new Date();
        expirationDate.setFullYear(expirationDate.getFullYear() + 1); // 1 year expiration
        document.cookie = `${key}=${value};path=/;expires=${expirationDate.toUTCString()};SameSite=Lax`;
        localStorage.setItem(key, value);
    },
    removeItem: (key) => {
        // Remove from both cookie and localStorage
        document.cookie = `${key}=;path=/;expires=Thu, 01 Jan 1970 00:00:00 GMT;SameSite=Lax`;
        localStorage.removeItem(key);
    },
};

// Initialize the Supabase client
const supabaseUrl = '{{ supabase_url }}';
const supabaseKey = '{{ supabase_key }}';

const supabase = supabase.createClient(supabaseUrl, supabaseKey, {
    auth: {
        storage: cookieStorageAdapter,
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
    },
});

// Make the client available globally
window.supabaseClient = supabase;