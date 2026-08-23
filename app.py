import streamlit as st

import pandas as pd

from data_engine import load_csv, prepare_data, validate_data

import strategy_engine

from backtest_engine import BacktestEngine

# =========================================================

# STRATEGY COMPATIBILITY LAYER

# =========================================================

import streamlit as st

import pandas as pd

from data_engine import load_csv, prepare_data, validate_data

from strategy_engine import (

    STRATEGY_REGISTRY,

    create_strategy,

)

from backtest_engine import BacktestEngine
    """

    Compatible strategy factory.

    Uses create_strategy() if available in strategy_engine.

    Falls back to STRATEGY_REGISTRY for compatibility.

    """

    if hasattr(strategy_engine, "create_strategy"):

        return strategy_engine.create_strategy(name, **params)

    if name not in STRATEGY_REGISTRY:

        available = ", ".join(STRATEGY_REGISTRY.keys())

        raise ValueError(

            f"Unknown strategy: {name}. "

            f"Available strategies: {available}"

        )

    return STRATEGY_REGISTRY[name](**params)

# =========================================================

# PAGE CONFIG

# =========================================================

st.set_page_config(

    page_title="Forex Backtester",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded",

)

# =========================================================

# CUSTOM CSS

# =========================================================

st.markdown(

    """

    <style>

    .stApp {

        background: #f7f8fc;

    }

    .main .block-container {

        max-width: 1500px;

        padding-top: 2rem;

        padding-bottom: 3rem;

    }

    .hero {

        background: linear-gradient(135deg, #111827, #1f2937);

        padding: 28px 32px;

        border-radius: 18px;

        margin-bottom: 24px;

        color: white;

        box-shadow: 0 8px 24px rgba(0,0,0,0.12);

    }

    .hero h1 {

        margin: 0;

        font-size: 34px;

        font-weight: 700;

    }

    .hero p {

        margin-top: 8px;

        margin-bottom: 0;

        opacity: 0.8;

        font-size: 16px;

    }

    .section-title {

        font-size: 22px;

        font-weight: 700;

        margin-top: 20px;

        margin-bottom: 10px;

    }

    .metric-card {

        background: white;

        padding: 18px;

        border-radius: 14px;

        border: 1px solid #e5e7eb;

        box-shadow: 0 3px 10px rgba(0,0,0,0.04);

    }

    .metric-label {

        color: #6b7280;

        font-size: 13px;

        margin-bottom: 6px;

    }

    .metric-value {

        font-size: 25px;

        font-weight: 700;

        color: #111827;

    }

    [data-testid="stSidebar"] {

        background-color: #ffffff;

        border-right: 1px solid #e5e7eb;

    }

    .sidebar-section {

        font-size: 18px;

        font-weight: 700;

        margin-top: 10px;

        margin-bottom: 8px;

    }

    .status-box {

        background: #ecfdf5;

        border: 1px solid #a7f3d0;

        padding: 12px 16px;

        border-radius: 10px;

        margin-bottom: 15px;

    }

    </style>

    """,

    unsafe_allow_html=True,

)

# =========================================================

# LANGUAGES

# English first

# Arabic last

# =========================================================

LANGUAGES = [

    ("English", "en"),

    ("हिन्दी", "hi"),

    ("Français", "fr"),

    ("中文", "zh"),

    ("日本語", "ja"),

    ("Русский", "ru"),

    ("العربية", "ar"),

]

# =========================================================

# TRANSLATIONS

# =========================================================

T = {

    # =====================================================

    # ENGLISH

    # =====================================================

    "en": {

        "title": "Forex Backtester",

        "subtitle": "Test your trading strategies with realistic execution and transparent trading costs.",

        "market": "Market Data",

        "upload": "Upload OHLC CSV",

        "load": "Load Data",

        "loaded": "Loaded {n:,} valid candles",

        "gaps": "Detected {n} possible time gaps.",

        "strategy": "Strategy",

        "strategy_name": "Select Strategy",

        "rr": "Risk / Reward",

        "fast": "Fast EMA",

        "slow": "Slow EMA",

        "execution": "Risk & Execution",

        "balance": "Initial Balance",

        "risk": "Risk Per Trade (%)",

        "spread": "Spread (Pips)",

        "slippage": "Slippage (Pips)",

        "commission": "Commission Per Lot / Side",

        "pip": "Pip Size",

        "model": "Same-Candle SL/TP Model",

        "conservative": "Conservative",

        "optimistic": "Optimistic",

        "run": "▶ Run Backtest",

        "no_data": "Upload and load a CSV file containing Open, High, Low and Close columns to begin.",

        "data": "Market Overview",

        "candles": "Candles",

        "first": "First Candle",

        "last": "Last Candle",

        "preview": "Data Preview",

        "preparing": "Preparing backtest...",

        "running": "Running backtest... {done:,}/{total:,}",

        "completed": "Completed",

        "success": "Backtest completed successfully.",

        "results": "Backtest Results",

        "final": "Final Balance",

        "profit": "Net Profit",

        "trades": "Trades",

        "win": "Win Rate",

        "pf": "Profit Factor",

        "dd": "Max Drawdown",

        "equity": "Equity Curve",

        "trade_log": "Trade Log",

        "no_trades": "No trades were generated by this strategy on this dataset.",

        "download": "Download Trades CSV",

        "error": "Error",

        "lang": "Language",

        "strategy_error": "No strategies are currently available.",

        "ready": "Ready to test",

        "loaded_data": "Market data loaded successfully.",

    },

    # =====================================================

    # HINDI

    # =====================================================

    "hi": {

        "title": "फॉरेक्स बैकटेस्टर",

        "subtitle": "वास्तविक निष्पादन और स्पष्ट ट्रेडिंग लागत के साथ अपनी रणनीतियों का परीक्षण करें।",

        "market": "मार्केट डेटा",

        "upload": "OHLC CSV अपलोड करें",

        "load": "डेटा लोड करें",

        "loaded": "{n:,} वैध कैंडल लोड हुईं",

        "gaps": "{n} संभावित समय अंतराल मिले।",

        "strategy": "रणनीति",

        "strategy_name": "रणनीति चुनें",

        "rr": "रिस्क / रिवॉर्ड",

        "fast": "फास्ट EMA",

        "slow": "स्लो EMA",

        "execution": "रिस्क और निष्पादन",

        "balance": "प्रारंभिक बैलेंस",

        "risk": "प्रति ट्रेड रिस्क (%)",

        "spread": "स्प्रेड (पिप्स)",

        "slippage": "स्लिपेज (पिप्स)",

        "commission": "प्रति लॉट / प्रति साइड कमीशन",

        "pip": "पिप साइज",

        "model": "एक ही कैंडल SL/TP मॉडल",

        "conservative": "कंज़र्वेटिव",

        "optimistic": "ऑप्टिमिस्टिक",

        "run": "▶ बैकटेस्ट चलाएं",

        "no_data": "शुरू करने के लिए Open, High, Low और Close वाला CSV अपलोड करें।",

        "data": "मार्केट ओवरव्यू",

        "candles": "कैंडल्स",

        "first": "पहली कैंडल",

        "last": "अंतिम कैंडल",

        "preview": "डेटा प्रीव्यू",

        "preparing": "बैकटेस्ट तैयार हो रहा है...",

        "running": "बैकटेस्ट चल रहा है... {done:,}/{total:,}",

        "completed": "पूर्ण",

        "success": "बैकटेस्ट सफलतापूर्वक पूरा हुआ।",

        "results": "बैकटेस्ट परिणाम",

        "final": "अंतिम बैलेंस",

        "profit": "नेट प्रॉफिट",

        "trades": "ट्रेड्स",

        "win": "विन रेट",

        "pf": "प्रॉफिट फैक्टर",

        "dd": "अधिकतम ड्रॉडाउन",

        "equity": "इक्विटी कर्व",

        "trade_log": "ट्रेड लॉग",

        "no_trades": "इस डेटा पर कोई ट्रेड नहीं बना।",

        "download": "ट्रेड्स CSV डाउनलोड करें",

        "error": "त्रुटि",

        "lang": "भाषा",

        "strategy_error": "कोई रणनीति उपलब्ध नहीं है।",

        "ready": "टेस्ट के लिए तैयार",

        "loaded_data": "मार्केट डेटा सफलतापूर्वक लोड हुआ।",

    },

    # =====================================================

    # FRENCH

    # =====================================================

    "fr": {

        "title": "Forex Backtester",

        "subtitle": "Testez vos stratégies avec une exécution réaliste et des coûts transparents.",

        "market": "Données de Marché",

        "upload": "Importer un CSV OHLC",

        "load": "Charger les Données",

        "loaded": "{n:,} bougies valides chargées",

        "gaps": "{n} écarts temporels possibles détectés.",

        "strategy": "Stratégie",

        "strategy_name": "Choisir une Stratégie",

        "rr": "Risque / Rendement",

        "fast": "EMA Rapide",

        "slow": "EMA Lente",

        "execution": "Risque et Exécution",

        "balance": "Solde Initial",

        "risk": "Risque par Trade (%)",

        "spread": "Spread (Pips)",

        "slippage": "Slippage (Pips)",

        "commission": "Commission par Lot / Côté",

        "pip": "Taille du Pip",

        "model": "Modèle SL/TP Même Bougie",

        "conservative": "Conservateur",

        "optimistic": "Optimiste",

        "run": "▶ Lancer le Backtest",

        "no_data": "Importez un CSV contenant Open, High, Low et Close.",

        "data": "Vue du Marché",

        "candles": "Bougies",

        "first": "Première Bougie",

        "last": "Dernière Bougie",

        "preview": "Aperçu des Données",

        "preparing": "Préparation du backtest...",

        "running": "Backtest en cours... {done:,}/{total:,}",

        "completed": "Terminé",

        "success": "Backtest terminé avec succès.",

        "results": "Résultats du Backtest",

        "final": "Solde Final",

        "profit": "Profit Net",

        "trades": "Trades",

        "win": "Taux de Réussite",

        "pf": "Facteur de Profit",

        "dd": "Drawdown Maximum",

        "equity": "Courbe d'Équité",

        "trade_log": "Journal des Trades",

        "no_trades": "Aucun trade généré sur ces données.",

        "download": "Télécharger les Trades CSV",

        "error": "Erreur",

        "lang": "Langue",

        "strategy_error": "Aucune stratégie disponible.",

        "ready": "Prêt à tester",

        "loaded_data": "Données de marché chargées.",

    },

    # =====================================================

    # CHINESE

    # =====================================================

    "zh": {

        "title": "外汇回测器",

        "subtitle": "使用真实执行方式和透明交易成本测试您的策略。",

        "market": "市场数据",

        "upload": "上传 OHLC CSV",

        "load": "加载数据",

        "loaded": "已加载 {n:,} 根有效K线",

        "gaps": "检测到 {n} 个可能的时间缺口。",

        "strategy": "策略",

        "strategy_name": "选择策略",

        "rr": "风险 / 回报",

        "fast": "快速 EMA",

        "slow": "慢速 EMA",

        "execution": "风险与执行",

        "balance": "初始余额",

        "risk": "每笔风险 (%)",

        "spread": "点差 (Pips)",

        "slippage": "滑点 (Pips)",

        "commission": "每手 / 每边佣金",

        "pip": "Pip 大小",

        "model": "同K线 SL/TP 模型",

        "conservative": "保守",

        "optimistic": "乐观",

        "run": "▶ 运行回测",

        "no_data": "上传包含 Open、High、Low 和 Close 的 CSV 文件。",

        "data": "市场概览",

        "candles": "K线",

        "first": "第一根K线",

        "last": "最后一根K线",

        "preview": "数据预览",

        "preparing": "正在准备回测...",

        "running": "正在运行回测... {done:,}/{total:,}",

        "completed": "完成",

        "success": "回测成功完成。",

        "results": "回测结果",

        "final": "最终余额",

        "profit": "净利润",

        "trades": "交易",

        "win": "胜率",

        "pf": "盈利因子",

        "dd": "最大回撤",

        "equity": "资金曲线",

        "trade_log": "交易记录",

        "no_trades": "该策略没有生成交易。",

        "download": "下载交易 CSV",

        "error": "错误",

        "lang": "语言",

        "strategy_error": "当前没有可用策略。",

        "ready": "准备测试",

        "loaded_data": "市场数据加载成功。",

    },

    # =====================================================

    # JAPANESE

    # =====================================================

    "ja": {

        "title": "Forex Backtester",

        "subtitle": "リアルな約定と明確な取引コストで戦略をテストします。",

        "market": "マーケットデータ",

        "upload": "OHLC CSV をアップロード",

        "load": "データを読み込む",

        "loaded": "{n:,} 本の有効な足を読み込みました",

        "gaps": "{n} 件の時間ギャップの可能性を検出しました。",

        "strategy": "ストラテジー",

        "strategy_name": "ストラテジーを選択",

        "rr": "リスク / リワード",

        "fast": "高速 EMA",

        "slow": "低速 EMA",

        "execution": "リスクと執行",

        "balance": "初期残高",

        "risk": "1取引あたりのリスク (%)",

        "spread": "スプレッド (Pips)",

        "slippage": "スリッページ (Pips)",

        "commission": "1ロット / 片側あたりの手数料",

        "pip": "Pip サイズ",

        "model": "同一足 SL/TP モデル",

        "conservative": "保守的",

        "optimistic": "楽観的",

        "run": "▶ バックテスト実行",

        "no_data": "Open、High、Low、Close を含む CSV をアップロードしてください。",

        "data": "マーケット概要",

        "candles": "足",

        "first": "最初の足",

        "last": "最後の足",

        "preview": "データプレビュー",

        "preparing": "バックテストを準備中...",

        "running": "バックテスト実行中... {done:,}/{total:,}",

        "completed": "完了",

        "success": "バックテストが完了しました。",

        "results": "バックテスト結果",

        "final": "最終残高",

        "profit": "純利益",

        "trades": "トレード",

        "win": "勝率",

        "pf": "プロフィットファクター",

        "dd": "最大ドローダウン",

        "equity": "エクイティカーブ",

        "trade_log": "トレード履歴",

        "no_trades": "このデータでは取引が生成されませんでした。",

        "download": "取引 CSV をダウンロード",

        "error": "エラー",

        "lang": "言語",

        "strategy_error": "利用可能な戦略がありません。",

        "ready": "テスト準備完了",

        "loaded_data": "マーケットデータを読み込みました。",

    },

    # =====================================================

    # RUSSIAN

    # =====================================================

    "ru": {

        "title": "Forex Backtester",

        "subtitle": "Тестируйте стратегии с реалистичным исполнением и прозрачными торговыми издержками.",

        "market": "Рыночные Данные",

        "upload": "Загрузить OHLC CSV",

        "load": "Загрузить Данные",

        "loaded": "Загружено {n:,} корректных свечей",

        "gaps": "Обнаружено возможных временных разрывов: {n}.",

        "strategy": "Стратегия",

        "strategy_name": "Выбрать Стратегию",

        "rr": "Риск / Доходность",

        "fast": "Быстрая EMA",

        "slow": "Медленная EMA",

        "execution": "Риск и Исполнение",

        "balance": "Начальный Баланс",

        "risk": "Риск на Сделку (%)",

        "spread": "Спред (Pips)",

        "slippage": "Проскальзывание (Pips)",

        "commission": "Комиссия за Лот / Сторону",

        "pip": "Размер Pip",

        "model": "Модель SL/TP в Одной Свече",

        "conservative": "Консервативная",

        "optimistic": "Оптимистичная",

        "run": "▶ Запустить Бэктест",

        "no_data": "Загрузите CSV с Open, High, Low и Close.",

        "data": "Обзор Рынка",

        "candles": "Свечи",

        "first": "Первая Свеча",

        "last": "Последняя Свеча",

        "preview": "Предпросмотр Данных",

        "preparing": "Подготовка бэктеста...",

        "running": "Выполняется бэктест... {done:,}/{total:,}",

        "completed": "Готово",

        "success": "Бэктест успешно завершён.",

        "results": "Результаты Бэктеста",

        "final": "Итоговый Баланс",

        "profit": "Чистая Прибыль",

        "trades": "Сделки",

        "win": "Процент Выигрышей",

        "pf": "Фактор Прибыли",

        "dd": "Макс. Просадка",

        "equity": "Кривая Капитала",

        "trade_log": "Журнал Сделок",

        "no_trades": "На этих данных стратегия не открыла сделок.",

        "download": "Скачать Сделки CSV",

        "error": "Ошибка",

        "lang": "Язык",

        "strategy_error": "Нет доступных стратегий.",

        "ready": "Готов к тестированию",

        "loaded_data": "Рыночные данные успешно загружены.",

    },

    # =====================================================

    # ARABIC - LAST LANGUAGE

    # =====================================================

    "ar": {

        "title": "اختبار استراتيجيات الفوركس",

        "subtitle": "اختبر استراتيجيات التداول بتنفيذ واقعي واحتساب واضح لتكاليف التداول.",

        "market": "بيانات السوق",

        "upload": "ارفع ملف OHLC CSV",

        "load": "تحميل البيانات",

        "loaded": "تم تحميل {n:,} شمعة صالحة",

        "gaps": "تم اكتشاف {n} فجوات زمنية محتملة.",

        "strategy": "الاستراتيجية",

        "strategy_name": "اختر الاستراتيجية",

        "rr": "العائد / المخاطرة",

        "fast": "EMA السريع",

        "slow": "EMA البطيء",

        "execution": "المخاطرة والتنفيذ",

        "balance": "الرصيد الابتدائي",

        "risk": "المخاطرة لكل صفقة (%)",

        "spread": "السبريد (نقطة)",

        "slippage": "الانزلاق السعري (نقطة)",

        "commission": "العمولة لكل لوت / لكل جانب",

        "pip": "حجم النقطة",

        "model": "نموذج SL/TP داخل نفس الشمعة",

        "conservative": "محافظ",

        "optimistic": "متفائل",

        "run": "▶ تشغيل الباك تست",

        "no_data": "ارفع ثم حمّل ملف CSV يحتوي على Open و High و Low و Close للبدء.",

        "data": "نظرة عامة على السوق",

        "candles": "الشموع",

        "first": "أول شمعة",

        "last": "آخر شمعة",

        "preview": "معاينة البيانات",

        "preparing": "جارٍ تجهيز الباك تست...",

        "running": "جارٍ تشغيل الباك تست... {done:,}/{total:,}",

        "completed": "اكتمل",

        "success": "اكتمل الباك تست بنجاح.",

        "results": "نتائج الباك تست",

        "final": "الرصيد النهائي",

        "profit": "صافي الربح",

        "trades": "الصفقات",

        "win": "نسبة الفوز",

        "pf": "معامل الربح",

        "dd": "أقصى تراجع",

        "equity": "منحنى رأس المال",

        "trade_log": "سجل الصفقات",

        "no_trades": "لم يتم توليد أي صفقات بهذه الاستراتيجية على هذه البيانات.",

        "download": "تحميل الصفقات CSV",

        "error": "خطأ",

        "lang": "اللغة",

        "strategy_error": "لا توجد استراتيجيات متاحة حاليًا.",

        "ready": "جاهز للاختبار",

        "loaded_data": "تم تحميل بيانات السوق بنجاح.",

    },

}

# =========================================================

# SESSION STATE

# =========================================================

DEFAULT_STATE = {

    "data": None,

    "result": None,

    "language": "en",

}

for key, value in DEFAULT_STATE.items():

    st.session_state.setdefault(key, value)

# =========================================================

# SIDEBAR - LANGUAGE

# =========================================================

with st.sidebar:

    st.markdown("### 🌐 Language")

    lang_labels = [name for name, _ in LANGUAGES]

    current_index = next(

        (

            i

            for i, (_, code) in enumerate(LANGUAGES)

            if code == st.session_state.language

        ),

        0,

    )

    selected = st.selectbox(

        "Language",

        lang_labels,

        index=current_index,

        key="language_selector",

    )

    st.session_state.language = dict(LANGUAGES)[selected]

# =========================================================

# CURRENT LANGUAGE

# =========================================================

lang = st.session_state.language

t = T[lang]

# =========================================================

# RTL SUPPORT

# =========================================================

if lang == "ar":

    st.markdown(

        """

        <style>

        html,

        body,

        [data-testid="stAppViewContainer"] {

            direction: rtl;

            text-align: right;

        }

        </style>

        """,

        unsafe_allow_html=True,

    )

# =========================================================

# HERO

# =========================================================

st.markdown(

    f"""

    <div class="hero">

        <h1>📊 {t["title"]}</h1>

        <p>{t["subtitle"]}</p>

    </div>

    """,

    unsafe_allow_html=True,

)

# =========================================================

# SIDEBAR SETTINGS

# =========================================================

with st.sidebar:

    # -----------------------------------------------------

    # MARKET DATA

    # -----------------------------------------------------

    st.divider()

    st.markdown(

        f'<div class="sidebar-section">📁 {t["market"]}</div>',

        unsafe_allow_html=True,

    )

    uploaded = st.file_uploader(

        t["upload"],

        type=["csv"],

    )

    if uploaded is not None:

        if st.button(

            t["load"],

            width="stretch",

        ):

            try:

                raw = load_csv(uploaded)

                data = prepare_data(raw)

                report = validate_data(data)

                st.session_state.data = data

                st.session_state.result = None

                st.success(

                    t["loaded"].format(

                        n=len(data)

                    )

                )

                if report.get("missing_bars", 0):

                    st.warning(

                        t["gaps"].format(

                            n=report["missing_bars"]

                        )

                    )

            except Exception as exc:

                st.error(

                    f"{t['error']}: {exc}"

                )

    # -----------------------------------------------------

    # STRATEGY

    # -----------------------------------------------------

    st.divider()

    st.markdown(

        f'<div class="sidebar-section">🎯 {t["strategy"]}</div>',

        unsafe_allow_html=True,

    )

    strategy_names = list(

        STRATEGY_REGISTRY.keys()

    )

    if not strategy_names:

        st.error(

            t["strategy_error"]

        )

        strategy_name = None

        params = {}

    else:

        strategy_name = st.selectbox(

            t["strategy_name"],

            strategy_names,

        )

        params = {}

        if strategy_name == "Price Action Reversal":

            params["risk_reward"] = st.number_input(

                t["rr"],

                min_value=0.1,

                max_value=20.0,

                value=2.0,

                step=0.1,

            )

        else:

            params["fast_period"] = st.number_input(

                t["fast"],

                min_value=2,

                max_value=500,

                value=20,

                step=1,

            )

            params["slow_period"] = st.number_input(

                t["slow"],

                min_value=3,

                max_value=1000,

                value=200,

                step=1,

            )

            params["risk_reward"] = st.number_input(

                t["rr"],

                min_value=0.1,

                max_value=20.0,

                value=2.0,

                step=0.1,

            )

    # -----------------------------------------------------

    # EXECUTION

    # -----------------------------------------------------

    st.divider()

    st.markdown(

        f'<div class="sidebar-section">⚙️ {t["execution"]}</div>',

        unsafe_allow_html=True,

    )

    initial_balance = st.number_input(

        t["balance"],

        min_value=100.0,

        max_value=10_000_000.0,

        value=10_000.0,

        step=100.0,

    )

    risk_percent = st.number_input(

        t["risk"],

        min_value=0.01,

        max_value=10.0,

        value=1.0,

        step=0.01,

    )

    spread_pips = st.number_input(

        t["spread"],

        min_value=0.0,

        max_value=100.0,

        value=1.0,

        step=0.1,

    )

    slippage_pips = st.number_input(

        t["slippage"],

        min_value=0.0,

        max_value=100.0,

        value=0.0,

        step=0.1,

    )

    commission = st.number_input(

        t["commission"],

        min_value=0.0,

        max_value=100.0,

        value=0.0,

        step=0.1,

    )

    pip_size = st.number_input(

        t["pip"],

        min_value=0.000001,

        max_value=1.0,

        value=0.0001,

        format="%.6f",

    )

    model_label = st.selectbox(

        t["model"],

        [

            t["conservative"],

            t["optimistic"],

        ],

    )

    intrabar_model = (

        "conservative"

        if model_label == t["conservative"]

        else "optimistic"

    )

    # -----------------------------------------------------

    # RUN BUTTON

    # -----------------------------------------------------

    st.divider()

    run = st.button(

        t["run"],

        type="primary",

        width="stretch",

        disabled=(

            st.session_state.data is None

            or strategy_name is None

        ),

    )

# =========================================================

# DATA OVERVIEW

# =========================================================

if st.session_state.data is None:

    st.info(

        t["no_data"]

    )

else:

    data = st.session_state.data

    st.markdown(

        f'<div class="section-title">📈 {t["data"]}</div>',

        unsafe_allow_html=True,

    )

    col1, col2, col3 = st.columns(3)

    first_time = (

        str(data["time"].iloc[0])

        if "time" in data.columns

        else "N/A"

    )

    last_time = (

        str(data["time"].iloc[-1])

        if "time" in data.columns

        else "N/A"

    )

    col1.metric(

        t["candles"],

        f"{len(data):,}",

    )

    col2.metric(

        t["first"],

        first_time,

    )

    col3.metric(

        t["last"],

        last_time,

    )

    st.write("")

    if "time" in data.columns:

        chart_data = (

            data

            .set_index("time")["close"]

        )

    else:

        chart_data = data["close"]

    st.line_chart(

        chart_data,

        width="stretch",

    )

    with st.expander(

        t["preview"]

    ):

        st.dataframe(

            data.head(100),

            width="stretch",

        )

# =========================================================

# RUN BACKTEST

# =========================================================

if run:

    try:

        if st.session_state.data is None:

            raise ValueError(

                t["no_data"]

            )

        if strategy_name is None:

            raise ValueError(

                t["strategy_error"]

            )

        strategy = create_strategy(

            strategy_name,

            **params,

        )

        engine = BacktestEngine(

            initial_balance=initial_balance,

            risk_percent=risk_percent,

            spread_pips=spread_pips,

            slippage_pips=slippage_pips,

            commission_per_lot=commission,

            pip_size=pip_size,

            intrabar_model=intrabar_model,

        )

        progress = st.progress(

            0,

            text=t["preparing"],

        )

        def callback(done, total):

            if total <= 0:

                percent = 0

            else:

                percent = min(

                    100,

                    int(done / total * 100),

                )

            progress.progress(

                percent,

                text=t["running"].format(

                    done=done,

                    total=total,

                ),

            )

        result = engine.run(

            st.session_state.data,

            strategy,

            callback,

        )

        st.session_state.result = result

        progress.progress(

            100,

            text=t["completed"],

        )

        st.success(

            t["success"]

        )

    except Exception as exc:

        st.session_state.result = None

        st.error(

            f"{t['error']}: {exc}"

        )

        st.exception(

            exc

        )

# =========================================================

# RESULTS

# =========================================================

if st.session_state.result is not None:

    result = st.session_state.result

    metrics = result.get(

        "metrics",

        {}

    )

    st.divider()

    st.markdown(

        f'<div class="section-title">🏆 {t["results"]}</div>',

        unsafe_allow_html=True,

    )

    # -----------------------------------------------------

    # METRICS

    # -----------------------------------------------------

    cols = st.columns(6)

    final_balance = metrics.get(

        "final_balance",

        0.0,

    )

    net_profit = metrics.get(

        "net_profit",

        0.0,

    )

    total_trades = metrics.get(

        "total_trades",

        0,

    )

    win_rate = metrics.get(

        "win_rate",

        0.0,

    )

    profit_factor = metrics.get(

        "profit_factor",

        0.0,

    )

    max_drawdown = metrics.get(

        "max_drawdown",

        0.0,

    )

    metric_values = [

        (

            t["final"],

            f"${final_balance:,.2f}",

        ),

        (

            t["profit"],

            f"${net_profit:,.2f}",

        ),

        (

            t["trades"],

            f"{total_trades:,}",

        ),

        (

            t["win"],

            f"{win_rate:.1f}%",

        ),

        (

            t["pf"],

            (

                "∞"

                if profit_factor == float("inf")

                else f"{profit_factor:.2f}"

            ),

        ),

        (

            t["dd"],

            f"{max_drawdown:.2f}%",

        ),

    ]

    for col, (label, value) in zip(

        cols,

        metric_values,

    ):

        col.metric(

            label,

            value,

        )

    # -----------------------------------------------------

    # EQUITY CURVE

    # -----------------------------------------------------

    equity_curve = result.get(

        "equity_curve",

        pd.DataFrame(),

    )

    if (

        equity_curve is not None

        and not equity_curve.empty

    ):

        st.write("")

        st.markdown(

            f'<div class="section-title">📈 {t["equity"]}</div>',

            unsafe_allow_html=True,

        )

        if (

            "time" in equity_curve.columns

            and "equity" in equity_curve.columns

        ):

            equity_chart = (

                equity_curve

                .set_index("time")["equity"]

            )

        elif "equity" in equity_curve.columns:

            equity_chart = equity_curve["equity"]

        else:

            equity_chart = None

        if equity_chart is not None:

            st.line_chart(

                equity_chart,

                width="stretch",

            )

    # -----------------------------------------------------

    # TRADE LOG

    # -----------------------------------------------------

    trades = result.get(

        "trades",

        pd.DataFrame(),

    )

    st.write("")

    st.markdown(

        f'<div class="section-title">📋 {t["trade_log"]}</div>',

        unsafe_allow_html=True,

    )

    if (

        trades is None

        or trades.empty

    ):

        st.warning(

            t["no_trades"]

        )

    else:

        st.dataframe(

            trades,

            width="stretch",

        )

        csv_data = (

            trades

            .to_csv(index=False)

            .encode("utf-8")

        )

        st.download_button(

            label=t["download"],

            data=csv_data,

            file_name="backtest_trades.csv",

            mime="text/csv",

            width="stretch",

        )
