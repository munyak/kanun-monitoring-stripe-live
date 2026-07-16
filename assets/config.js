// Supabase client configuration for KaNun Monitoring.
// Uses the @supabase/supabase-js v2 UMD build loaded from the CDN (window.supabase).
const SUPABASE_URL = 'https://ubwmitylgqjlqpcsoezv.supabase.co'
const SUPABASE_ANON_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVid21pdHlsZ3FqbHFwY3NvZXp2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgxMjA1MTEsImV4cCI6MjA5MzY5NjUxMX0.F8bPIKktfG3LBuSb_Haxd1oLEh8l8BdGtsjbHmkNXeE'

// Where the app sends people after a successful sign-in.
const APP_REDIRECT = '/dashboard.html'

// The supabase-js UMD bundle exposes a global `supabase` object with createClient.
// We create our client and re-expose it as `sb` to avoid shadowing that global.
const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
})

window.sb = sb
window.APP_REDIRECT = APP_REDIRECT
