/**
 * Star Office UI - Lightweight i18n Module
 * No build step, no external dependencies.
 */
(function () {
  'use strict';

  const SUPPORTED_LOCALES = ['zh', 'ja'];
  const DEFAULT_LOCALE = 'zh';
  const STORAGE_KEY = 'star-office-lang';

  // Detect locale: ?lang= > localStorage > navigator.language
  function detectLocale() {
    const params = new URLSearchParams(window.location.search);
    const paramLang = params.get('lang');
    if (paramLang && SUPPORTED_LOCALES.includes(paramLang)) return paramLang;

    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED_LOCALES.includes(stored)) return stored;

    const nav = (navigator.language || '').toLowerCase();
    if (nav.startsWith('ja')) return 'ja';
    return DEFAULT_LOCALE;
  }

  let currentLocale = detectLocale();
  let messages = {};

  // Load locale JSON synchronously (blocking on purpose - runs before DOM content)
  function loadLocale(locale) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/static/locales/' + locale + '.json?t=' + Date.now(), false); // sync
    xhr.send();
    if (xhr.status === 200) {
      try {
        return JSON.parse(xhr.responseText);
      } catch (e) {
        console.error('[i18n] Failed to parse locale file:', e);
        return {};
      }
    }
    console.error('[i18n] Failed to load locale:', locale, xhr.status);
    return {};
  }

  messages = loadLocale(currentLocale);

  // Deep get by dot-separated key path: t('states.idle') -> messages.states.idle
  function getByPath(obj, path) {
    const parts = path.split('.');
    let cur = obj;
    for (const p of parts) {
      if (cur == null || typeof cur !== 'object') return undefined;
      cur = cur[p];
    }
    return cur;
  }

  /**
   * Translate function.
   * @param {string} keyPath - dot-separated key (e.g. 'common.loading')
   * @param {Object} [params] - template variables (e.g. {name: 'Star'})
   * @returns {*} translated string, array, or object; falls back to keyPath if not found
   */
  function t(keyPath, params) {
    let val = getByPath(messages, keyPath);
    if (val === undefined) return keyPath;
    if (typeof val === 'string' && params) {
      Object.keys(params).forEach(function (k) {
        val = val.replace(new RegExp('\\{' + k + '\\}', 'g'), params[k]);
      });
    }
    return val;
  }

  // Apply data-i18n and data-i18n-placeholder attributes to DOM elements
  function applyI18nAttributes() {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var val = t(key);
      if (typeof val === 'string') {
        el.textContent = val;
      }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-placeholder');
      var val = t(key);
      if (typeof val === 'string') {
        el.placeholder = val;
      }
    });
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      var val = t(key);
      if (typeof val === 'string') {
        el.innerHTML = val;
      }
    });
  }

  // Switch font based on locale
  function applyFont() {
    var fontStyle = document.getElementById('i18n-font-face');
    if (!fontStyle) {
      fontStyle = document.createElement('style');
      fontStyle.id = 'i18n-font-face';
      document.head.appendChild(fontStyle);
    }
    if (currentLocale === 'ja') {
      fontStyle.textContent = "@font-face { font-family: 'ArkPixel'; src: url('/static/fonts/ark-pixel-12px-proportional-ja.ttf.woff2') format('woff2'); font-weight: normal; font-style: normal; }";
    } else {
      fontStyle.textContent = "@font-face { font-family: 'ArkPixel'; src: url('/static/fonts/ark-pixel-12px-proportional-zh_cn.ttf.woff2') format('woff2'); font-weight: normal; font-style: normal; }";
    }
  }

  // Set locale, persist, and reload
  function setLocale(lang) {
    if (!SUPPORTED_LOCALES.includes(lang)) return;
    localStorage.setItem(STORAGE_KEY, lang);
    // Update URL param for server-side awareness
    var url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
  }

  // Auto-apply on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      applyFont();
      applyI18nAttributes();
    });
  } else {
    applyFont();
    applyI18nAttributes();
  }

  // Expose global API
  window.I18N = {
    locale: currentLocale,
    setLocale: setLocale,
    t: t,
    applyI18nAttributes: applyI18nAttributes
  };
  // Global shorthand
  window.t = t;
})();
