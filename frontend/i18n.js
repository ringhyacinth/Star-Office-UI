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
          chinese: "中文",
          spanish: "Español",
          french: "Français",
          japanese: "日本語",
          portuguese: "Português"
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
          chinese: "中文",
          spanish: "西班牙语",
          french: "法语",
          japanese: "日语",
          portuguese: "葡萄牙语"
        }
      }
    }
  };

  // Lightweight language packs merged over English fallback for minimal code churn.
  const extraTranslations = {
    es: {
      index: {
        title: "Oficina Pixel de Star",
        loading: "Cargando la oficina pixel de Star...",
        memoTitle: "— NOTAS DE AYER —",
        memoLoading: "Cargando...",
        memoNone: "No hay notas de ayer",
        memoError: "No se pudo cargar",
        statusTitle: "Estado de Star",
        btnStandby: "Espera",
        btnWork: "Trabajo",
        btnSync: "Sincronizar",
        btnAlert: "Alerta",
        guestsTitle: "— INVITADOS —",
        guestsLoading: "Cargando invitados...",
        guestsEmpty: "Sin invitados",
        statusLoading: "Cargando...",
        coordsShow: "Mostrar coordenadas",
        coordsHide: "Ocultar coordenadas",
        panView: "Mover vista",
        lockView: "Bloquear vista",
        guestStatusApproved: "Aprobado",
        guestStatusPending: "Pendiente",
        guestStatusRejected: "Rechazado",
        guestStatusOffline: "Desconectado",
        guestStateIdle: "En espera",
        guestStateWriting: "Trabajando",
        guestStateResearching: "Investigando",
        guestStateExecuting: "Ejecutando",
        guestStateSyncing: "Sincronizando",
        guestStateError: "Alerta",
        btnSwapSkill: "Intercambiar skill",
        btnRemove: "Quitar",
        removed: "eliminado",
        removedDemo: "eliminado (demo)",
        leaveFailed: "Error al salir: ",
        approveOk: "Invitado aprobado",
        approveFailed: "Error al aprobar: ",
        rejectOk: "Invitado rechazado",
        rejectFailed: "Error al rechazar: ",
        requestFailed: "Error de solicitud: ",
        unknownError: "error desconocido",
        guestFetchFailed: "Error al cargar invitados:",
        connRetry: "Conexión fallida, reintentando...",
        stateIdle: "En espera",
        stateWriting: "Escribiendo",
        stateResearching: "Investigando",
        stateExecuting: "Ejecutando",
        stateSyncing: "Sincronizando",
        stateError: "Error"
      },
      join: {
        title: "Unirse a la oficina pixel de Star",
        heading: "⭐ Unirse a la oficina pixel de Star",
        nameLabel: "Tu nombre (visible en la oficina)",
        namePlaceholder: "ej. Asistente",
        keyLabel: "Clave de acceso de un solo uso",
        keyPlaceholder: "Ingresa tu clave",
        joinBtn: "Unirse",
        leaveBtn: "Salir",
        note1: "⚠️ Esta página solo necesita tu nombre + clave de un solo uso",
        note2: "El estado se enviará automáticamente por el agente",
        inviteLabel: "📌 Instrucciones:",
        errName: "Ingresa tu nombre",
        errKey: "Ingresa la clave de acceso",
        joinOk: "¡Unido con éxito! Recarga para ver tu agente ✨",
        joinFail: "Error al unirse",
        netErr: "Error de red, inténtalo de nuevo",
        leaveNeedName: "Ingresa el nombre a quitar",
        leaveOk: "Saliste de la oficina 👋",
        leaveFail: "Error al salir"
      },
      invite: {
        title: "Star Office - Invitación",
        heading: "✨ Star Office · Invitación",
        welcome: "¡Bienvenido al panel pixel de Star Office!",
        stepsTitle: "Únete en 3 pasos",
        step1Title: "Confirma tu información",
        step1Body: "Debes tener estos 2 datos:",
        inviteLinkLabel: "Enlace de invitación:",
        joinKeyLabel: "Clave de un solo uso:",
        step2Title: "Envía los datos a OpenClaw",
        step2Body: "Envía el enlace + clave y di “ayúdame a unirme a Star Office”.",
        step3Title: "Aprueba en tu lado",
        step3Body: "OpenClaw pedirá autorización en el chat. Luego enviará estados automáticamente.",
        privacyTitle: "⚠️ Nota de privacidad",
        privacyBody: "Solo se envía estado (idle/writing/researching/executing/syncing/error), nunca contenido privado.",
        back: "← Volver a Star Office",
        footer1: "Star Studio · Panel Pixel Office",
        footer2: "¿Necesitas ayuda? Pregunta a Star 😊"
      },
      common: {
        language: "Idioma",
        english: "Inglés",
        chinese: "Chino",
        spanish: "Español",
        french: "Francés",
        japanese: "Japonés",
        portuguese: "Portugués"
      }
    },
    fr: {
      index: {
        title: "Bureau Pixel de Star",
        loading: "Chargement du bureau pixel de Star...",
        memoTitle: "— NOTES D'HIER —",
        memoLoading: "Chargement...",
        memoNone: "Aucune note d'hier",
        memoError: "Échec du chargement",
        statusTitle: "Statut de Star",
        btnStandby: "Veille",
        btnWork: "Travail",
        btnSync: "Sync",
        btnAlert: "Alerte",
        guestsTitle: "— INVITÉS —",
        guestsLoading: "Chargement des invités...",
        guestsEmpty: "Aucun invité",
        statusLoading: "Chargement...",
        coordsShow: "Afficher coord.",
        coordsHide: "Masquer coord.",
        panView: "Déplacer vue",
        lockView: "Verrouiller vue",
        guestStatusApproved: "Approuvé",
        guestStatusPending: "En attente",
        guestStatusRejected: "Refusé",
        guestStatusOffline: "Hors ligne",
        guestStateIdle: "Veille",
        guestStateWriting: "Travail",
        guestStateResearching: "Recherche",
        guestStateExecuting: "Exécution",
        guestStateSyncing: "Synchronisation",
        guestStateError: "Alerte",
        btnSwapSkill: "Échanger skill",
        btnRemove: "Retirer",
        removed: "retiré",
        removedDemo: "retiré (démo)",
        leaveFailed: "Échec de sortie : ",
        approveOk: "Invité approuvé",
        approveFailed: "Échec approbation : ",
        rejectOk: "Invité rejeté",
        rejectFailed: "Échec rejet : ",
        requestFailed: "Échec requête : ",
        unknownError: "erreur inconnue",
        guestFetchFailed: "Échec chargement invités :",
        connRetry: "Connexion échouée, nouvelle tentative...",
        stateIdle: "Veille",
        stateWriting: "Rédaction",
        stateResearching: "Recherche",
        stateExecuting: "Exécution",
        stateSyncing: "Synchronisation",
        stateError: "Erreur"
      },
      join: {
        title: "Rejoindre le bureau pixel de Star",
        heading: "⭐ Rejoindre le bureau pixel de Star",
        nameLabel: "Votre nom (affiché au bureau)",
        namePlaceholder: "ex. Assistant",
        keyLabel: "Clé d'accès à usage unique",
        keyPlaceholder: "Entrez votre clé",
        joinBtn: "Rejoindre",
        leaveBtn: "Quitter",
        note1: "⚠️ Cette page demande seulement votre nom + clé unique",
        note2: "Le statut est envoyé automatiquement par l'agent",
        inviteLabel: "📌 Instructions :",
        errName: "Veuillez entrer votre nom",
        errKey: "Veuillez entrer la clé",
        joinOk: "Rejoint avec succès ! Rechargez pour voir l'agent ✨",
        joinFail: "Échec de connexion",
        netErr: "Erreur réseau, réessayez",
        leaveNeedName: "Entrez le nom à retirer",
        leaveOk: "Vous avez quitté le bureau 👋",
        leaveFail: "Échec de sortie"
      },
      invite: {
        title: "Star Office - Invitation",
        heading: "✨ Star Office · Invitation",
        welcome: "Bienvenue sur le tableau pixel de Star Office !",
        stepsTitle: "Rejoindre en 3 étapes",
        step1Title: "Vérifiez vos infos",
        step1Body: "Vous devez avoir ces 2 éléments :",
        inviteLinkLabel: "Lien d'invitation :",
        joinKeyLabel: "Clé unique :",
        step2Title: "Envoyez les infos à OpenClaw",
        step2Body: "Envoyez le lien + la clé et dites « aide-moi à rejoindre Star Office ».",
        step3Title: "Approuvez côté utilisateur",
        step3Body: "OpenClaw demandera une autorisation dans le chat, puis poussera les statuts automatiquement.",
        privacyTitle: "⚠️ Confidentialité",
        privacyBody: "Seul le statut est envoyé (idle/writing/researching/executing/syncing/error), jamais de contenu privé.",
        back: "← Retour à Star Office",
        footer1: "Star Studio · Tableau Pixel Office",
        footer2: "Besoin d'aide ? Demandez à Star 😊"
      },
      common: {
        language: "Langue",
        english: "Anglais",
        chinese: "Chinois",
        spanish: "Espagnol",
        french: "Français",
        japanese: "Japonais",
        portuguese: "Portugais"
      }
    },
    ja: {
      index: {
        title: "Starのピクセルオフィス",
        loading: "Starのピクセルオフィスを読み込み中...",
        memoTitle: "— 昨日のメモ —",
        memoLoading: "読み込み中...",
        memoNone: "昨日のメモはありません",
        memoError: "読み込みに失敗しました",
        statusTitle: "Starステータス",
        btnStandby: "待機",
        btnWork: "作業",
        btnSync: "同期",
        btnAlert: "アラート",
        guestsTitle: "— ゲスト一覧 —",
        guestsLoading: "ゲストを読み込み中...",
        guestsEmpty: "ゲストはいません",
        statusLoading: "読み込み中...",
        coordsShow: "座標を表示",
        coordsHide: "座標を非表示",
        panView: "ビュー移動",
        lockView: "ビュー固定",
        guestStatusApproved: "承認済み",
        guestStatusPending: "保留中",
        guestStatusRejected: "拒否",
        guestStatusOffline: "オフライン",
        guestStateIdle: "待機",
        guestStateWriting: "作業中",
        guestStateResearching: "調査",
        guestStateExecuting: "実行",
        guestStateSyncing: "同期",
        guestStateError: "アラート",
        btnSwapSkill: "スキル交換",
        btnRemove: "退出",
        removed: "を退出しました",
        removedDemo: "を退出しました（demo）",
        leaveFailed: "退出失敗: ",
        approveOk: "ゲストを承認しました",
        approveFailed: "承認失敗: ",
        rejectOk: "ゲストを拒否しました",
        rejectFailed: "拒否失敗: ",
        requestFailed: "リクエスト失敗: ",
        unknownError: "不明なエラー",
        guestFetchFailed: "ゲスト取得失敗:",
        connRetry: "接続に失敗。再試行中...",
        stateIdle: "待機",
        stateWriting: "執筆",
        stateResearching: "調査",
        stateExecuting: "実行",
        stateSyncing: "同期",
        stateError: "エラー"
      },
      join: {
        title: "Starのピクセルオフィスに参加",
        heading: "⭐ Starのピクセルオフィスに参加",
        nameLabel: "名前（オフィスに表示）",
        namePlaceholder: "例: アシスタント",
        keyLabel: "ワンタイム参加キー",
        keyPlaceholder: "参加キーを入力",
        joinBtn: "参加",
        leaveBtn: "退出",
        note1: "⚠️ このページでは「名前 + ワンタイムキー」だけ必要です",
        note2: "状態はエージェントが自動で送信します",
        inviteLabel: "📌 招待手順:",
        errName: "名前を入力してください",
        errKey: "参加キーを入力してください",
        joinOk: "参加成功！更新すると表示されます ✨",
        joinFail: "参加失敗",
        netErr: "ネットワークエラー。再試行してください",
        leaveNeedName: "退出する名前を入力してください",
        leaveOk: "オフィスから退出しました 👋",
        leaveFail: "退出失敗"
      },
      invite: {
        title: "Star Office - 招待",
        heading: "✨ Star Office · 招待",
        welcome: "Star Officeのピクセルダッシュボードへようこそ！",
        stepsTitle: "3ステップで参加",
        step1Title: "情報を確認",
        step1Body: "次の2つを用意してください:",
        inviteLinkLabel: "招待リンク:",
        joinKeyLabel: "ワンタイムキー:",
        step2Title: "OpenClawへ情報を送る",
        step2Body: "リンク + キーを送り「Star Officeに参加させて」と伝えてください。",
        step3Title: "あなた側で承認",
        step3Body: "チャットで承認要求が来ます。承認後、状態が自動送信されます。",
        privacyTitle: "⚠️ プライバシー",
        privacyBody: "送信されるのは状態のみ（idle/writing/researching/executing/syncing/error）で、内容は送信されません。",
        back: "← Star Officeへ戻る",
        footer1: "Star Studio · Pixel Office ダッシュボード",
        footer2: "困ったらStarへ 😊"
      },
      common: {
        language: "言語",
        english: "英語",
        chinese: "中国語",
        spanish: "スペイン語",
        french: "フランス語",
        japanese: "日本語",
        portuguese: "ポルトガル語"
      }
    },
    pt: {
      index: {
        title: "Escritório Pixel do Star",
        loading: "Carregando o escritório pixel do Star...",
        memoTitle: "— NOTAS DE ONTEM —",
        memoLoading: "Carregando...",
        memoNone: "Sem notas de ontem",
        memoError: "Falha ao carregar",
        statusTitle: "Status do Star",
        btnStandby: "Em espera",
        btnWork: "Trabalho",
        btnSync: "Sincronizar",
        btnAlert: "Alerta",
        guestsTitle: "— CONVIDADOS —",
        guestsLoading: "Carregando convidados...",
        guestsEmpty: "Sem convidados",
        statusLoading: "Carregando...",
        coordsShow: "Mostrar coords",
        coordsHide: "Ocultar coords",
        panView: "Mover visão",
        lockView: "Travar visão",
        guestStatusApproved: "Aprovado",
        guestStatusPending: "Pendente",
        guestStatusRejected: "Rejeitado",
        guestStatusOffline: "Offline",
        guestStateIdle: "Em espera",
        guestStateWriting: "Trabalhando",
        guestStateResearching: "Pesquisa",
        guestStateExecuting: "Executando",
        guestStateSyncing: "Sincronizando",
        guestStateError: "Alerta",
        btnSwapSkill: "Trocar skill",
        btnRemove: "Remover",
        removed: "removido",
        removedDemo: "removido (demo)",
        leaveFailed: "Falha ao sair: ",
        approveOk: "Convidado aprovado",
        approveFailed: "Falha ao aprovar: ",
        rejectOk: "Convidado rejeitado",
        rejectFailed: "Falha ao rejeitar: ",
        requestFailed: "Falha na solicitação: ",
        unknownError: "erro desconhecido",
        guestFetchFailed: "Falha ao buscar convidados:",
        connRetry: "Falha de conexão, tentando novamente...",
        stateIdle: "Em espera",
        stateWriting: "Escrevendo",
        stateResearching: "Pesquisando",
        stateExecuting: "Executando",
        stateSyncing: "Sincronizando",
        stateError: "Erro"
      },
      join: {
        title: "Entrar no escritório pixel do Star",
        heading: "⭐ Entrar no escritório pixel do Star",
        nameLabel: "Seu nome (aparece no escritório)",
        namePlaceholder: "ex.: Assistente",
        keyLabel: "Chave de acesso única",
        keyPlaceholder: "Digite sua chave",
        joinBtn: "Entrar",
        leaveBtn: "Sair",
        note1: "⚠️ Esta página precisa apenas de nome + chave única",
        note2: "O status será enviado automaticamente pelo agente",
        inviteLabel: "📌 Instruções:",
        errName: "Digite seu nome",
        errKey: "Digite a chave de acesso",
        joinOk: "Entrou com sucesso! Atualize para ver o agente ✨",
        joinFail: "Falha ao entrar",
        netErr: "Erro de rede, tente novamente",
        leaveNeedName: "Digite o nome para remover",
        leaveOk: "Saiu do escritório 👋",
        leaveFail: "Falha ao sair"
      },
      invite: {
        title: "Star Office - Convite",
        heading: "✨ Star Office · Convite",
        welcome: "Bem-vindo ao painel pixel do Star Office!",
        stepsTitle: "Entre em 3 passos",
        step1Title: "Confirme suas informações",
        step1Body: "Você deve ter estes 2 itens:",
        inviteLinkLabel: "Link de convite:",
        joinKeyLabel: "Chave única:",
        step2Title: "Envie os dados para o OpenClaw",
        step2Body: "Envie o link + chave e diga “me ajude a entrar no Star Office”.",
        step3Title: "Aprove no seu lado",
        step3Body: "O OpenClaw pedirá aprovação no chat. Depois disso, enviará status automaticamente.",
        privacyTitle: "⚠️ Privacidade",
        privacyBody: "Apenas status é enviado (idle/writing/researching/executing/syncing/error), sem conteúdo privado.",
        back: "← Voltar ao Star Office",
        footer1: "Star Studio · Painel Pixel Office",
        footer2: "Precisa de ajuda? Pergunte ao Star 😊"
      },
      common: {
        language: "Idioma",
        english: "Inglês",
        chinese: "Chinês",
        spanish: "Espanhol",
        french: "Francês",
        japanese: "Japonês",
        portuguese: "Português"
      }
    }
  };

  function isObject(value) {
    return value && typeof value === 'object' && !Array.isArray(value);
  }

  function deepMerge(base, patch) {
    const out = { ...base };
    Object.keys(patch || {}).forEach((key) => {
      const b = base ? base[key] : undefined;
      const p = patch[key];
      if (isObject(b) && isObject(p)) {
        out[key] = deepMerge(b, p);
      } else {
        out[key] = p;
      }
    });
    return out;
  }

  Object.entries(extraTranslations).forEach(([lang, translationPatch]) => {
    resources[lang] = {
      translation: deepMerge(resources.en.translation, translationPatch)
    };
  });

  const supportedLangs = ['zh', 'en', 'es', 'fr', 'ja', 'pt'];

  function normalizeLang(raw) {
    const s = (raw || '').toLowerCase();
    if (s.startsWith('zh')) return 'zh';
    if (s.startsWith('en')) return 'en';
    if (s.startsWith('es')) return 'es';
    if (s.startsWith('fr')) return 'fr';
    if (s.startsWith('ja')) return 'ja';
    if (s.startsWith('pt')) return 'pt';
    return 'en';
  }

  function htmlLang(lang) {
    if (lang === 'zh') return 'zh-CN';
    if (lang === 'ja') return 'ja';
    if (lang === 'pt') return 'pt-BR';
    if (lang === 'es') return 'es';
    if (lang === 'fr') return 'fr';
    return 'en';
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

    const languageOptions = [
      { code: 'zh', key: 'common.chinese', fallback: '中文' },
      { code: 'en', key: 'common.english', fallback: 'English' },
      { code: 'es', key: 'common.spanish', fallback: 'Español' },
      { code: 'fr', key: 'common.french', fallback: 'Français' },
      { code: 'ja', key: 'common.japanese', fallback: '日本語' },
      { code: 'pt', key: 'common.portuguese', fallback: 'Português' }
    ];

    languageOptions.forEach(({ code, key, fallback }) => {
      const opt = document.createElement('option');
      opt.value = code;
      opt.textContent = `🌐 ${(window.__t && window.__t(key, fallback)) || fallback}`;
      select.appendChild(opt);
    });

    select.value = window.__lang || 'zh';

    select.addEventListener('change', (e) => {
      const next = normalizeLang(e.target.value);
      localStorage.setItem('staroffice.lang', next);
      setQueryLang(next);
    });

    // Match the same style as top action buttons (e.g. "Pan View").
    wrap.style.cssText = 'position:fixed;top:calc(env(safe-area-inset-top, 0px) + 12px);left:50%;transform:translateX(-50%);z-index:999999;';
    select.style.cssText = 'padding:8px 10px;font-family:ArkPixel,monospace;font-size:13px;cursor:pointer;border:2px solid #333;border-radius:5px;background:#333;color:#fff;';

    select.addEventListener('mouseenter', () => {
      select.style.background = '#e94560';
      select.style.borderColor = '#e94560';
    });
    select.addEventListener('mouseleave', () => {
      select.style.background = '#333';
      select.style.borderColor = '#333';
    });

    // Slightly smaller on non-dashboard pages so it doesn't dominate forms.
    if (scope !== 'index') {
      select.style.fontSize = '12px';
      select.style.padding = '6px 8px';
    }

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
      supportedLngs: supportedLangs,
      resources,
      interpolation: { escapeValue: false }
    });

    window.__lang = lang;
    window.__t = function (key, fallback, options) {
      const val = window.i18next.t(key, options || {});
      return val === key ? (fallback || key) : val;
    };

    document.documentElement.lang = htmlLang(lang);
    applyTranslations(scope);
    injectLanguageSwitcher(scope);

    return {
      lang,
      t: window.__t,
      apply: function () { applyTranslations(scope); }
    };
  };
})();
