/* ============================================================
   auth.js — Shared authentication utilities + Toast system
   ============================================================ */

const API = "";   // same origin

/* ── Token helpers ──────────────────────────────────────────── */
function getToken()          { return localStorage.getItem("sbis_token"); }
function getUser()           { try { return JSON.parse(localStorage.getItem("sbis_user")); } catch { return null; } }
function setAuth(token, user){ localStorage.setItem("sbis_token", token); localStorage.setItem("sbis_user", JSON.stringify(user)); }
function clearAuth()         { localStorage.removeItem("sbis_token"); localStorage.removeItem("sbis_user"); }

function authHeaders() {
  return { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` };
}

/* ── Redirect guards ────────────────────────────────────────── */
function requireLogin(role) {
  const user = getUser();
  if (!user || !getToken()) { window.location.href = "/"; return null; }
  if (role === "admin" && user.role !== "admin") {
    showToast("Admin access required.", "error");
    setTimeout(() => window.location.href = "/status", 1000);
    return null;
  }
  return user;
}

function redirectIfLoggedIn() {
  const user = getUser();
  if (user && getToken()) {
    window.location.href = user.role === "admin" ? "/admin" : "/status";
  }
}

/* ── Logout ─────────────────────────────────────────────────── */
function logout() {
  clearAuth();
  window.location.replace("/");
}

/* ── API helper ─────────────────────────────────────────────── */
async function apiCall(method, url, body = null) {
  try {
    const opts = { method, headers: authHeaders() };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    return { ok: false, status: 0, data: { error: "Network error — is the server running?" } };
  }
}

/* ══════════════════════════════════════════════════════════════
   Toast Notification System
   ══════════════════════════════════════════════════════════════ */
function ensureToastContainer() {
  let el = document.getElementById("toast-container");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast-container";
    document.body.appendChild(el);
  }
  return el;
}

/**
 * Show a toast notification.
 * @param {string} message
 * @param {'success'|'error'|'info'|'warn'} type
 * @param {number} duration  ms before auto-dismiss (0 = sticky)
 */
function showToast(message, type = "info", duration = 4000) {
  const icons = { success: "✅", error: "❌", warn: "⚠️", info: "ℹ️" };
  const container = ensureToastContainer();

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || "ℹ️"}</span>
    <span>${message}</span>
    <button class="toast-close" onclick="dismissToast(this.parentElement)">✕</button>
  `;

  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => dismissToast(toast), duration);
  }
  return toast;
}

function dismissToast(toast) {
  if (!toast || !toast.parentElement) return;
  toast.classList.add("removing");
  setTimeout(() => toast.remove(), 350);
}

/* ── Animated number counter ────────────────────────────────── */
function animateCount(el, target, duration = 900) {
  const start = 0;
  const startTime = performance.now();
  const isFloat = String(target).includes(".");

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = start + (target - start) * eased;
    el.textContent = isFloat ? current.toFixed(1) : Math.round(current);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── Favicon (emoji) ────────────────────────────────────────── */
function setEmojiFavicon(emoji) {
  const canvas = document.createElement("canvas");
  canvas.width = 32; canvas.height = 32;
  const ctx = canvas.getContext("2d");
  ctx.font = "28px serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(emoji, 16, 18);
  const link = document.querySelector("link[rel~='icon']") || document.createElement("link");
  link.rel = "icon";
  link.href = canvas.toDataURL();
  document.head.appendChild(link);
}

/* ── Navbar dynamic render ──────────────────────────────────── */
function renderNavbar() {
  const nav = document.getElementById("nav-actions");
  if (!nav) return;
  const user = getUser();
  if (user) {
    const isAdmin = user.role === "admin";
    nav.innerHTML = `
      <span class="topbar-badge" style="background:#EFF6FF;border-color:#DBEAFE;color:#1E40AF">
        ${isAdmin ? "🔑" : "👤"} <strong>${user.name}</strong>
      </span>
      ${isAdmin
        ? `<a href="/admin" class="btn btn-ghost btn-sm">Dashboard</a>
           <a href="/analytics" class="btn btn-ghost btn-sm">Analytics</a>`
        : `<a href="/status" class="btn btn-ghost btn-sm">My Status</a>
           <a href="/analytics" class="btn btn-ghost btn-sm">Analytics</a>`
      }
      <button onclick="logout()" class="btn btn-outline btn-sm">Logout</button>
    `;
  } else {
    nav.innerHTML = `
      <a href="/" class="btn btn-ghost btn-sm">Sign In</a>
      <a href="/register" class="btn btn-primary btn-sm">Register</a>
    `;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderNavbar();
  setEmojiFavicon("🏛️");
});
