// Shared helpers for the KaNun Monitoring auth pages.
// Depends on assets/config.js having run first (it declares the global `sb`
// client and also exposes it as window.sb).

// ---- Message banner ----
function showMsg(el, text, kind = 'error') {
  el.textContent = text
  el.className = `msg show ${kind}`
}
function clearMsg(el) {
  el.className = 'msg'
  el.textContent = ''
}

// ---- Friendly error text ----
function friendlyError(err) {
  const m = (err && err.message) || String(err)
  if (/invalid login credentials/i.test(m)) return 'That email or password is incorrect.'
  if (/email not confirmed/i.test(m)) return 'Please confirm your email address first, then sign in.'
  if (/rate limit|too many requests/i.test(m)) return 'Too many attempts. Please wait a minute and try again.'
  if (/user already registered/i.test(m)) return 'An account with this email already exists. Try signing in instead.'
  if (/provider is not enabled|unsupported provider/i.test(m)) return 'This sign-in method is not enabled yet.'
  if (/otp.*expired|expired|invalid.*token/i.test(m)) return 'This link has expired or already been used. Please request a new one.'
  return m
}

// ---- Button busy state ----
function setBusy(btn, busy, busyLabel = 'Working…') {
  if (busy) {
    btn.dataset.label = btn.innerHTML
    btn.disabled = true
    btn.innerHTML = `<span class="spin"></span> ${busyLabel}`
  } else {
    btn.disabled = false
    if (btn.dataset.label) btn.innerHTML = btn.dataset.label
  }
}

// ---- Social auth (Google / Facebook) ----
// Wired to Supabase OAuth. signInWithOAuth builds the redirect URL client-side
// and won't tell us a provider is disabled, so we first ask GoTrue which
// providers are actually enabled (public /settings endpoint). Once the OAuth
// apps are connected in Supabase, these buttons start working with no code change.
let _providerSettings = null
async function enabledProviders() {
  if (_providerSettings) return _providerSettings
  try {
    const r = await fetch(SUPABASE_URL + '/auth/v1/settings', { headers: { apikey: SUPABASE_ANON_KEY } })
    const j = await r.json()
    _providerSettings = j.external || {}
  } catch { _providerSettings = {} }
  return _providerSettings
}
async function socialSignIn(provider, msgEl) {
  clearMsg(msgEl)
  const label = provider.charAt(0).toUpperCase() + provider.slice(1)
  const providers = await enabledProviders()
  if (!providers[provider]) {
    showMsg(msgEl, `${label} sign-in isn't available yet — it will be enabled once the ${label} app is connected.`, 'error')
    return
  }
  const { error } = await sb.auth.signInWithOAuth({
    provider,
    options: { redirectTo: window.location.origin + window.APP_REDIRECT },
  })
  if (error) showMsg(msgEl, friendlyError(error))
}

// ---- Redirect if already signed in (for login/signup pages) ----
async function redirectIfAuthed() {
  const { data } = await sb.auth.getSession()
  if (data.session) window.location.replace(window.APP_REDIRECT)
}

// ---- Require a session (for protected pages); redirect to login if none ----
async function requireSession() {
  let { data } = await sb.auth.getSession()
  // Magic-link / OAuth redirects land here with tokens in the URL hash; give
  // detectSessionInUrl a beat to exchange them before deciding there's no session.
  if (!data.session && /access_token=|[?&]code=/.test(window.location.href)) {
    await new Promise(r => setTimeout(r, 600))
    ;({ data } = await sb.auth.getSession())
    // Clean the tokens out of the address bar once consumed.
    if (data.session) history.replaceState(null, '', window.location.pathname)
  }
  if (!data.session) {
    window.location.replace('/login.html')
    return null
  }
  return data.session
}

// ---- Brand pane markup (shared across auth pages) ----
function brandPane() {
  return `
    <div class="brand-pane">
      <a href="/" class="wordmark">
        <span class="mark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </span>
        KaNun Monitoring
      </a>
      <div class="brand-hero">
        <h1>Supervised visitation,<br/>professionally managed.</h1>
        <p>Secure scheduling, clear documentation, and court-ready reports — for agencies, monitors, parents, and counsel.</p>
        <div class="brand-ticks">
          <span>Role-based access</span>
          <span>Court-ready reports</span>
          <span>Private &amp; encrypted</span>
        </div>
      </div>
      <div class="brand-foot">KaNun Monitoring · Demo environment</div>
    </div>`
}

// Google / Facebook brand SVGs for social buttons.
const GOOGLE_SVG = `<svg viewBox="0 0 24 24"><path fill="#4285F4" d="M22.5 12.27c0-.79-.07-1.54-.2-2.27H12v4.51h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.21-4.74 3.21-8.33z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.26 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1A11 11 0 0 0 2.18 7.06l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z"/></svg>`
const FACEBOOK_SVG = `<svg viewBox="0 0 24 24"><path fill="#1877F2" d="M24 12c0-6.63-5.37-12-12-12S0 5.37 0 12c0 5.99 4.39 10.95 10.13 11.85v-8.38H7.08V12h3.05V9.36c0-3 1.79-4.67 4.53-4.67 1.31 0 2.68.24 2.68.24v2.95h-1.51c-1.49 0-1.96.93-1.96 1.87V12h3.33l-.53 3.47h-2.8v8.38C19.61 22.95 24 17.99 24 12z"/></svg>`
