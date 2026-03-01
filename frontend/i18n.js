(function () {
  const resources = {
    en: {
      translation: {
        index: {
          title: "Star's Pixel Office",
          loading: "Loading Star's Pixel Office...",
          memoTitle: "— YESTERDAY NOTES —",
          memoLoading: "Loading...",
          memoNone: "No notes found for yesterday",
          memoError: "Failed to load",
          statusTitle: "Star Status",
          btnStandby: "Standby",
          btnWork: "Work",
          btnSync: "Sync",
          btnAlert: "Alert",
          guestsTitle: "— GUESTS —",
          guestsLoading: "Loading guests...",
          guestsEmpty: "No guests",
          statusLoading: "Loading...",
          coordsShow: "Show Coords",
          coordsHide: "Hide Coords",
          panView: "Pan View",
          lockView: "Lock View",
          guestStatusApproved: "Approved",
          guestStatusPending: "Pending",
          guestStatusRejected: "Rejected",
          guestStatusOffline: "Offline",
          guestStateIdle: "Standby",
          guestStateWriting: "Working",
          guestStateResearching: "Research",
          guestStateExecuting: "Execute",
          guestStateSyncing: "Sync",
          guestStateError: "Alert",
          btnSwapSkill: "Swap Skill",
          btnRemove: "Remove",
          removed: "removed",
          removedDemo: "removed (demo)",
          leaveFailed: "Leave failed: ",
          approveOk: "Guest approved",
          approveFailed: "Approve failed: ",
          rejectOk: "Guest rejected",
          rejectFailed: "Reject failed: ",
          requestFailed: "Request failed: ",
          unknownError: "unknown error",
          guestFetchFailed: "Failed to fetch guest list:",
          connRetry: "Connection failed, retrying...",
          stateIdle: "Standby",
          stateWriting: "Writing",
          stateResearching: "Researching",
          stateExecuting: "Executing",
          stateSyncing: "Syncing",
          stateError: "Error"
        },
        join: {
          title: "Join Star's Pixel Office",
          heading: "⭐ Join Star's Pixel Office",
          nameLabel: "Your name (shown in the office)",
          namePlaceholder: "e.g. Coding Assistant",
          keyLabel: "One-time agent join key",
          keyPlaceholder: "Enter your join key",
          joinBtn: "Join Office",
          leaveBtn: "Leave Office",
          note1: "⚠️ Note: this page only needs your name + one-time join key",
          note2: "Status and details are pushed automatically by the agent",
          inviteLabel: "📌 Invite instructions:",
          errName: "Please enter your name first",
          errKey: "Please enter the agent join key first",
          joinOk: "Joined successfully! Refresh the office to see your agent ✨",
          joinFail: "Join failed",
          netErr: "Network error, please try again",
          leaveNeedName: "Please enter the name to remove",
          leaveOk: "Left the office 👋",
          leaveFail: "Leave failed"
        },
        invite: {
          title: "Star Office - Join Invite",
          heading: "✨ Star Office · Join Invite",
          welcome: "Welcome to the Star Office pixel dashboard!",
          stepsTitle: "Join in 3 steps",
          step1Title: "Confirm your info",
          step1Body: "You should already have two things:",
          inviteLinkLabel: "Invite link:",
          joinKeyLabel: "One-time join key:",
          step2Title: "Send the invite details to your OpenClaw",
          step2Body: "Send the invite link + join key and say “help me join Star Office.”",
          step3Title: "Approve on your side",
          step3Body: "Your OpenClaw will ask for approval in chat. Once approved, it will auto-push status updates to the office dashboard.",
          privacyTitle: "⚠️ Privacy note",
          privacyBody: "Only status is pushed (idle/writing/researching/executing/syncing/error), no private content. You can stop anytime.",
          back: "← Back to Star Office",
          footer1: "Star Studio · Pixel Office Dashboard",
          footer2: "Need help? Ask Star 😊"
        },
        common: {
          language: "Language",
          english: "English",
          chinese: "中文"
        }
      }
    },
    zh: {
      translation: {
        index: {
          title: "Star 的像素办公室",
          loading: "正在加载 Star 的像素办公室...",
          memoTitle: "— 昨 日 小 记 —",
          memoLoading: "加载中...",
          memoNone: "暂无昨日日记",
          memoError: "加载失败",
          statusTitle: "Star 状态",
          btnStandby: "待命",
          btnWork: "工作",
          btnSync: "同步",
          btnAlert: "报警",
          guestsTitle: "— 访 客 列 表 —",
          guestsLoading: "正在加载访客...",
          guestsEmpty: "暂无访客",
          statusLoading: "加载中...",
          coordsShow: "显示坐标",
          coordsHide: "隐藏坐标",
          panView: "移动视野",
          lockView: "锁定视野",
          guestStatusApproved: "已授权",
          guestStatusPending: "待授权",
          guestStatusRejected: "已拒绝",
          guestStatusOffline: "离线",
          guestStateIdle: "待命",
          guestStateWriting: "工作",
          guestStateResearching: "调研",
          guestStateExecuting: "执行",
          guestStateSyncing: "同步",
          guestStateError: "报警",
          btnSwapSkill: "交换技能",
          btnRemove: "离开房间",
          removed: "已离开",
          removedDemo: "已离开（demo）",
          leaveFailed: "离开失败：",
          approveOk: "已批准该访客接入",
          approveFailed: "批准失败：",
          rejectOk: "已拒绝该访客",
          rejectFailed: "拒绝失败：",
          requestFailed: "请求失败：",
          unknownError: "未知错误",
          guestFetchFailed: "拉取访客列表失败:",
          connRetry: "连接失败，正在重试...",
          stateIdle: "待命",
          stateWriting: "整理文档",
          stateResearching: "搜索信息",
          stateExecuting: "执行任务",
          stateSyncing: "同步备份",
          stateError: "出错了"
        },
        join: {
          title: "加入 Star 的像素办公室",
          heading: "⭐ 加入 Star 的像素办公室",
          nameLabel: "你的名字（会显示在办公室）",
          namePlaceholder: "例如：小龙虾助手",
          keyLabel: "Agent 接入密钥（一次性）",
          keyPlaceholder: "请输入你拿到的 join key",
          joinBtn: "加入办公室",
          leaveBtn: "离开办公室",
          note1: "⚠️ 注意：join 页面仅需要名字 + 一次性 join key",
          note2: "状态与状态细节会由 agent 后续自动推送同步",
          inviteLabel: "📌 邀请说明：",
          errName: "请先输入你的名字～",
          errKey: "请先输入 Agent 接入密钥～",
          joinOk: "加入成功！刷新办公室就能看到你啦 ✨",
          joinFail: "加入失败",
          netErr: "网络出错，请重试",
          leaveNeedName: "请先输入你要离开的名字～",
          leaveOk: "已离开办公室 👋",
          leaveFail: "离开失败"
        },
        invite: {
          title: "海辛办公室 - 加入邀请",
          heading: "✨ 海辛办公室 · 加入邀请",
          welcome: "欢迎加入海辛的像素办公室看板！",
          stepsTitle: "加入步骤（一共 3 步）",
          step1Title: "确认信息",
          step1Body: "你应该已经收到两样东西：",
          inviteLinkLabel: "邀请链接：",
          joinKeyLabel: "一次性接入密钥（join key）：",
          step2Title: "把邀请信息丢给你的 OpenClaw",
          step2Body: "把邀请链接 + join key 一起发给你的 OpenClaw，并说“帮我加入海辛办公室”。",
          step3Title: "在你这边授权",
          step3Body: "你的 OpenClaw 会在对话里向你要授权；同意后，它就会开始自动把工作状态推送到海辛办公室看板啦！",
          privacyTitle: "⚠️ 隐私说明",
          privacyBody: "只推送状态（idle/writing/researching/executing/syncing/error），不含任何具体内容/隐私；随时可停。",
          back: "← 回到海辛办公室",
          footer1: "海辛工作室 · 像素办公室看板",
          footer2: "有问题找海辛 😊"
        },
        common: {
          language: "语言",
          english: "English",
          chinese: "中文"
        }
      }
    }
  };

  function normalizeLang(raw) {
    const s = (raw || '').toLowerCase();
    return s.startsWith('zh') ? 'zh' : 'en';
  }

  function setQueryLang(lang) {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.replace(url.toString());
  }

  function injectLanguageSwitcher(scope) {
    if (document.getElementById('lang-switcher')) return;

    const wrap = document.createElement('div');
    wrap.id = 'lang-switcher';

    const select = document.createElement('select');
    select.id = 'lang-select';

    const optZh = document.createElement('option');
    optZh.value = 'zh';
    optZh.textContent = `🌐 ${(window.__t && window.__t('common.chinese', '中文')) || '中文'}`;

    const optEn = document.createElement('option');
    optEn.value = 'en';
    optEn.textContent = `🌐 ${(window.__t && window.__t('common.english', 'English')) || 'English'}`;

    select.appendChild(optZh);
    select.appendChild(optEn);
    select.value = window.__lang || 'zh';

    select.addEventListener('change', (e) => {
      const next = normalizeLang(e.target.value);
      localStorage.setItem('staroffice.lang', next);
      setQueryLang(next);
    });

    // Match button style used in the dashboard control panel.
    const applyButtonStyle = (compact) => {
      const base = [
        'background:#3a3f4f',
        'color:#fff',
        'border:2px solid #555',
        'border-radius:4px',
        'cursor:pointer',
        'font-family:ArkPixel, monospace',
        'font-size:12px'
      ];
      if (compact) {
        base.push('height:52px', 'width:100%', 'padding:8px 10px');
      } else {
        base.push('padding:8px 10px');
      }
      select.style.cssText = base.join(';') + ';';

      select.addEventListener('mouseenter', () => {
        select.style.background = '#4a4f5f';
        select.style.borderColor = '#e94560';
      });
      select.addEventListener('mouseleave', () => {
        select.style.background = '#3a3f4f';
        select.style.borderColor = '#555';
      });
    };

    // On main dashboard, place language menu in the same button grid.
    if (scope === 'index') {
      const controlButtons = document.getElementById('control-buttons');
      if (controlButtons) {
        wrap.style.cssText = 'grid-column:1 / -1;';
        applyButtonStyle(true);
        wrap.appendChild(select);
        controlButtons.appendChild(wrap);
        return;
      }
    }

    // Fallback for join/invite pages.
    wrap.style.cssText = 'position:fixed;top:calc(env(safe-area-inset-top, 0px) + 12px);right:12px;z-index:999999;display:flex;align-items:center;gap:8px;';
    applyButtonStyle(false);

    const label = document.createElement('span');
    label.textContent = (window.__t && window.__t('common.language', 'Language')) || 'Language';
    label.style.cssText = 'color:#fff;background:rgba(0,0,0,0.55);border-radius:4px;padding:4px 6px;font:12px ArkPixel, monospace;';

    wrap.appendChild(label);
    wrap.appendChild(select);
    document.body.appendChild(wrap);
  }

  function applyTranslations(scope) {
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      const full = key.includes('.') ? key : `${scope}.${key}`;
      const value = window.__t(full, null);
      if (value && value !== full) el.textContent = value;
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      const full = key.includes('.') ? key : `${scope}.${key}`;
      const value = window.__t(full, null);
      if (value && value !== full) el.setAttribute('placeholder', value);
    });

    const title = window.__t(`${scope}.title`, null);
    if (title && title !== `${scope}.title`) {
      document.title = title;
    }
  }

  window.__initI18n = async function __initI18n(scope) {
    if (!window.i18next) {
      window.__lang = 'en';
      window.__t = function (k, fallback) { return fallback || k; };
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const forced = params.get('lang');
    const saved = localStorage.getItem('staroffice.lang');
    const lang = normalizeLang(forced || saved || 'zh');

    localStorage.setItem('staroffice.lang', lang);

    await window.i18next.init({
      lng: lang,
      fallbackLng: 'en',
      resources,
      interpolation: { escapeValue: false }
    });

    window.__lang = lang;
    window.__t = function (key, fallback, options) {
      const val = window.i18next.t(key, options || {});
      return val === key ? (fallback || key) : val;
    };

    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    applyTranslations(scope);
    injectLanguageSwitcher(scope);

    return {
      lang,
      t: window.__t,
      apply: function () { applyTranslations(scope); }
    };
  };
})();
