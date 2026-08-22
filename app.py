import streamlit as st

import pandas as pd

from data_engine import load_csv, prepare_data, validate_data

from backtest_engine import BacktestEngine

from strategy_engine import ExamplePriceActionStrategy, ZigZagStrategy

# =========================================================

# FOREX BACKTESTER

# APP V4 + BACKTEST ENGINE

# =========================================================

st.set_page_config(

    page_title="Forex Backtester",

    page_icon="📊",

    layout="wide"

)

# =========================================================

# LANGUAGE SYSTEM

# =========================================================

LANGUAGES = {

    "English": "en",

    "हिन्दी": "hi",

    "Français": "fr",

    "中文": "zh",

    "日本語": "ja",

    "Русский": "ru",

    "العربية": "ar"

}

TEXT = {

    "ar": {

        "title": "Forex Backtester",

        "subtitle": "منصة اختبار الاستراتيجيات",

        "dashboard": "لوحة التحكم",

        "strategies": "الاستراتيجيات",

        "backtest": "الباك تيست",

        "reports": "التقارير",

        "strategy": "الاستراتيجية",

        "strategy_builder": "منشئ الاستراتيجيات",

        "run": "تشغيل الاختبار",

        "results": "نتائج الاختبار",

        "trades": "عدد الصفقات",

        "win_rate": "نسبة الفوز",

        "profit_factor": "معامل الربحية",

        "net_r": "صافي الربح",

        "max_dd": "أقصى تراجع",

        "data_engine": "محرك البيانات",

        "strategy_engine": "محرك الاستراتيجية",

        "risk_engine": "إدارة المخاطر",

        "report_engine": "محرك التقارير",

        "price_action": "Price Action",

        "indicators": "المؤشرات",

        "zigzag": "ZigZag",

        "retest": "إعادة الاختبار",

        "trailing": "Trailing Stop",

        "data_source": "مصدر البيانات",

        "upload_csv": "📁 رفع CSV",

        "online_data": "🌐 بيانات Online",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "ارفع ملف بيانات السوق",

        "load_data": "تحميل البيانات",

        "data_loaded": "تم تحميل البيانات بنجاح",

        "candles": "عدد الشموع",

        "first_candle": "أول شمعة",

        "last_candle": "آخر شمعة",

        "missing_bars": "الشموع الناقصة",

        "duplicates": "الشموع المكررة",

        "invalid_ohlc": "شموع OHLC غير صحيحة",

        "data_preview": "معاينة البيانات",

        "price_chart": "الرسم البياني",

        "close_price": "سعر الإغلاق",

        "coming_soon": "Coming Soon",

        "valid": "البيانات صالحة",

        "invalid": "البيانات غير صالحة",

        "ready": "البرنامج جاهز لاختبار الاستراتيجيات."

    },

    "en": {

        "title": "Forex Backtester",

        "subtitle": "Strategy Testing Platform",

        "dashboard": "Dashboard",

        "strategies": "Strategies",

        "backtest": "Backtest",

        "reports": "Reports",

        "strategy": "Strategy",

        "strategy_builder": "Strategy Builder",

        "run": "Run Backtest",

        "results": "Backtest Results",

        "trades": "Total Trades",

        "win_rate": "Win Rate",

        "profit_factor": "Profit Factor",

        "net_r": "Net Profit",

        "max_dd": "Max Drawdown",

        "data_engine": "Data Engine",

        "strategy_engine": "Strategy Engine",

        "risk_engine": "Risk Engine",

        "report_engine": "Report Engine",

        "price_action": "Price Action",

        "indicators": "Indicators",

        "zigzag": "ZigZag",

        "retest": "Retest",

        "trailing": "Trailing Stop",

        "data_source": "Data Source",

        "upload_csv": "📁 Upload CSV",

        "online_data": "🌐 Online Data",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "Upload your market data file",

        "load_data": "Load Data",

        "data_loaded": "Data loaded successfully",

        "candles": "Candles",

        "first_candle": "First Candle",

        "last_candle": "Last Candle",

        "missing_bars": "Missing Bars",

        "duplicates": "Duplicate Candles",

        "invalid_ohlc": "Invalid OHLC Candles",

        "data_preview": "Data Preview",

        "price_chart": "Price Chart",

        "close_price": "Close Price",

        "coming_soon": "Coming Soon",

        "valid": "Data is valid",

        "invalid": "Data is invalid",

        "ready": "The platform is ready to test strategies."

    },

    "hi": {

        "title": "Forex Backtester",

        "subtitle": "रणनीति परीक्षण प्लेटफ़ॉर्म",

        "dashboard": "डैशबोर्ड",

        "strategies": "रणनीतियाँ",

        "backtest": "बैकटेस्ट",

        "reports": "रिपोर्ट",

        "strategy": "रणनीति",

        "strategy_builder": "रणनीति बिल्डर",

        "run": "बैकटेस्ट चलाएँ",

        "results": "बैकटेस्ट परिणाम",

        "trades": "कुल ट्रेड",

        "win_rate": "विन रेट",

        "profit_factor": "प्रॉफिट फैक्टर",

        "net_r": "नेट प्रॉफिट",

        "max_dd": "अधिकतम ड्रॉडाउन",

        "data_engine": "डेटा इंजन",

        "strategy_engine": "रणनीति इंजन",

        "risk_engine": "रिस्क इंजन",

        "report_engine": "रिपोर्ट इंजन",

        "price_action": "Price Action",

        "indicators": "Indicators",

        "zigzag": "ZigZag",

        "retest": "Retest",

        "trailing": "Trailing Stop",

        "data_source": "डेटा स्रोत",

        "upload_csv": "📁 CSV अपलोड",

        "online_data": "🌐 ऑनलाइन डेटा",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "मार्केट डेटा फ़ाइल अपलोड करें",

        "load_data": "डेटा लोड करें",

        "data_loaded": "डेटा सफलतापूर्वक लोड हुआ",

        "candles": "कैंडल्स",

        "first_candle": "पहली कैंडल",

        "last_candle": "अंतिम कैंडल",

        "missing_bars": "गुम बार",

        "duplicates": "डुप्लिकेट कैंडल्स",

        "invalid_ohlc": "अमान्य OHLC कैंडल्स",

        "data_preview": "डेटा प्रीव्यू",

        "price_chart": "प्राइस चार्ट",

        "close_price": "क्लोज़ प्राइस",

        "coming_soon": "Coming Soon",

        "valid": "डेटा मान्य है",

        "invalid": "डेटा अमान्य है",

        "ready": "प्लेटफ़ॉर्म रणनीतियों के परीक्षण के लिए तैयार है."

    },

    "fr": {

        "title": "Forex Backtester",

        "subtitle": "Plateforme de test de stratégies",

        "dashboard": "Tableau de bord",

        "strategies": "Stratégies",

        "backtest": "Backtest",

        "reports": "Rapports",

        "strategy": "Stratégie",

        "strategy_builder": "Constructeur de stratégies",

        "run": "Lancer le backtest",

        "results": "Résultats",

        "trades": "Nombre de trades",

        "win_rate": "Taux de réussite",

        "profit_factor": "Profit Factor",

        "net_r": "Profit net",

        "max_dd": "Drawdown maximum",

        "data_engine": "Moteur de données",

        "strategy_engine": "Moteur de stratégie",

        "risk_engine": "Gestion du risque",

        "report_engine": "Moteur de rapports",

        "price_action": "Price Action",

        "indicators": "Indicateurs",

        "zigzag": "ZigZag",

        "retest": "Retest",

        "trailing": "Trailing Stop",

        "data_source": "Source des données",

        "upload_csv": "📁 Importer CSV",

        "online_data": "🌐 Données Online",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "Importer votre fichier de données",

        "load_data": "Charger les données",

        "data_loaded": "Données chargées avec succès",

        "candles": "Bougies",

        "first_candle": "Première bougie",

        "last_candle": "Dernière bougie",

        "missing_bars": "Barres manquantes",

        "duplicates": "Bougies en double",

        "invalid_ohlc": "Bougies OHLC invalides",

        "data_preview": "Aperçu des données",

        "price_chart": "Graphique des prix",

        "close_price": "Prix de clôture",

        "coming_soon": "Coming Soon",

        "valid": "Données valides",

        "invalid": "Données invalides",

        "ready": "La plateforme est prête à tester les stratégies."

    },

    "zh": {

        "title": "Forex Backtester",

        "subtitle": "策略回测平台",

        "dashboard": "控制面板",

        "strategies": "策略",

        "backtest": "回测",

        "reports": "报告",

        "strategy": "策略",

        "strategy_builder": "策略构建器",

        "run": "运行回测",

        "results": "回测结果",

        "trades": "交易数量",

        "win_rate": "胜率",

        "profit_factor": "盈利因子",

        "net_r": "净利润",

        "max_dd": "最大回撤",

        "data_engine": "数据引擎",

        "strategy_engine": "策略引擎",

        "risk_engine": "风险管理",

        "report_engine": "报告引擎",

        "price_action": "Price Action",

        "indicators": "指标",

        "zigzag": "ZigZag",

        "retest": "Retest",

        "trailing": "Trailing Stop",

        "data_source": "数据来源",

        "upload_csv": "📁 上传 CSV",

        "online_data": "🌐 在线数据",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "上传市场数据文件",

        "load_data": "加载数据",

        "data_loaded": "数据加载成功",

        "candles": "K线数量",

        "first_candle": "第一根K线",

        "last_candle": "最后一根K线",

        "missing_bars": "缺失K线",

        "duplicates": "重复K线",

        "invalid_ohlc": "无效 OHLC",

        "data_preview": "数据预览",

        "price_chart": "价格图表",

        "close_price": "收盘价",

        "coming_soon": "Coming Soon",

        "valid": "数据有效",

        "invalid": "数据无效",

        "ready": "平台已准备好测试策略。"

    },

    "ja": {

        "title": "Forex Backtester",

        "subtitle": "戦略バックテストプラットフォーム",

        "dashboard": "ダッシュボード",

        "strategies": "戦略",

        "backtest": "バックテスト",

        "reports": "レポート",

        "strategy": "戦略",

        "strategy_builder": "ストラテジービルダー",

        "run": "バックテスト実行",

        "results": "バックテスト結果",

        "trades": "取引数",

        "win_rate": "勝率",

        "profit_factor": "プロフィットファクター",

        "net_r": "純利益",

        "max_dd": "最大ドローダウン",

        "data_engine": "データエンジン",

        "strategy_engine": "戦略エンジン",

        "risk_engine": "リスク管理",

        "report_engine": "レポートエンジン",

        "price_action": "Price Action",

        "indicators": "インジケーター",

        "zigzag": "ZigZag",

        "retest": "Retest",

        "trailing": "Trailing Stop",

        "data_source": "データソース",

        "upload_csv": "📁 CSVアップロード",

        "online_data": "🌐 オンラインデータ",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "市場データファイルをアップロード",

        "load_data": "データを読み込む",

        "data_loaded": "データの読み込みに成功しました",

        "candles": "ローソク足数",

        "first_candle": "最初のローソク足",

        "last_candle": "最後のローソク足",

        "missing_bars": "欠損バー",

        "duplicates": "重複ローソク足",

        "invalid_ohlc": "無効なOHLC",

        "data_preview": "データプレビュー",

        "price_chart": "価格チャート",

        "close_price": "終値",

        "coming_soon": "Coming Soon",

        "valid": "データは有効です",

        "invalid": "データが無効です",

        "ready": "プラットフォームは戦略テストの準備ができています。"

    },

    "ru": {

        "title": "Forex Backtester",

        "subtitle": "Платформа тестирования стратегий",

        "dashboard": "Панель управления",

        "strategies": "Стратегии",

        "backtest": "Бэктест",

        "reports": "Отчёты",

        "strategy": "Стратегия",

        "strategy_builder": "Конструктор стратегий",

        "run": "Запустить бэктест",

        "results": "Результаты",

        "trades": "Количество сделок",

        "win_rate": "Процент побед",

        "profit_factor": "Profit Factor",

        "net_r": "Чистая прибыль",

        "max_dd": "Максимальная просадка",

        "data_engine": "Движок данных",

        "strategy_engine": "Движок стратегий",

        "risk_engine": "Управление рисками",

        "report_engine": "Движок отчётов",

        "price_action": "Price Action",

        "indicators": "Индикаторы",

        "zigzag": "ZigZag",

        "retest": "Retest",

        "trailing": "Trailing Stop",

        "data_source": "Источник данных",

        "upload_csv": "📁 Загрузить CSV",

        "online_data": "🌐 Онлайн-данные",

        "mt5": "🔌 MetaTrader 5",

        "upload_file": "Загрузите файл рыночных данных",

        "load_data": "Загрузить данные",

        "data_loaded": "Данные успешно загружены",

        "candles": "Количество свечей",

        "first_candle": "Первая свеча",

        "last_candle": "Последняя свеча",

        "missing_bars": "Пропущенные бары",

        "duplicates": "Дубликаты свечей",

        "invalid_ohlc": "Некорректные OHLC",

        "data_preview": "Предпросмотр данных",

        "price_chart": "График цены",

        "close_price": "Цена закрытия",

        "coming_soon": "Coming Soon",

        "valid": "Данные корректны",

        "invalid": "Данные некорректны",

        "ready": "Платформа готова к тестированию стратегий."

    }

}

# =========================================================

# SESSION STATE

# =========================================================

if "language" not in st.session_state:

    st.session_state.language = "en"

if "market_data" not in st.session_state:

    st.session_state.market_data = None

if "data_info" not in st.session_state:

    st.session_state.data_info = None

if "backtest_results" not in st.session_state:

    st.session_state.backtest_results = None

current_language = st.session_state.language

t = TEXT[current_language]

# =========================================================

# RTL

# =========================================================

if current_language == "ar":

    st.markdown(

        """

        <style>

        .main {

            direction: rtl;

        }

        h1, h2, h3, p, label {

            text-align: right;

        }

        </style>

        """,

        unsafe_allow_html=True

    )

# =========================================================

# TOP BAR

# =========================================================

top_left, top_right = st.columns([8, 1])

with top_left:

    st.title("📊 " + t["title"])

    st.caption(t["subtitle"])

with top_right:

    selected_language = st.selectbox(

        "🌐",

        list(LANGUAGES.keys()),

        index=list(LANGUAGES.values()).index(

            current_language

        ),

        label_visibility="collapsed"

    )

    new_language = LANGUAGES[selected_language]

    if new_language != current_language:

        st.session_state.language = new_language

        st.rerun()

# =========================================================

# NAVIGATION

# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(

    [

        t["dashboard"],

        t["strategies"],

        t["backtest"],

        t["reports"]

    ]

)

# =========================================================

# DASHBOARD

# =========================================================

with tab1:

    st.header(t["dashboard"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(t["data_engine"], "Ready")

    c2.metric(t["strategy_engine"], "Ready")

    c3.metric(t["risk_engine"], "Ready")

    c4.metric(t["report_engine"], "Ready")

    st.divider()

    st.info(t["ready"])

# =========================================================

# STRATEGIES

# =========================================================

with tab2:

    st.header(t["strategies"])

    st.subheader(t["strategy_builder"])

    # Strategy selection

selected_strategy = st.radio(

    "Choose Strategy",

    [

        "🧠 " + t["price_action"],

        "📊 " + t["indicators"],

        "〽️ " + t["zigzag"],

        "🔄 " + t["retest"],

        "📈 " + t["trailing"],

    ],

    key="selected_strategy"

)

st.divider()

if selected_strategy.startswith("🧠"):

    st.subheader("🧠 " + t["price_action"])

    st.info("Price Action strategy builder")

elif selected_strategy.startswith("📊"):

    st.subheader("📊 " + t["indicators"])

    st.info("Indicators strategy builder")

elif selected_strategy.startswith("〽️"):

    st.subheader("〽️ " + t["zigzag"])

    st.info("ZigZag strategy builder")

elif selected_strategy.startswith("🔄"):

    st.subheader("🔄 " + t["retest"])

    st.info("Retest strategy builder")

elif selected_strategy.startswith("📈"):

    st.subheader("📈 " + t["trailing"])

    st.info("Trailing Stop strategy builder")

# =========================================================

# BACKTEST

# =========================================================

with tab3:

    st.header(t["backtest"])

    # =====================================================

    # MARKET DATA

    # =====================================================

    st.subheader("📊 Market Data")

    source = st.selectbox(

        t["data_source"],

        [

            t["upload_csv"],

            t["online_data"],

            t["mt5"]

        ]

    )

    # =====================================================

    # CSV

    # =====================================================

    if source == t["upload_csv"]:

        uploaded_file = st.file_uploader(

            t["upload_file"],

            type=["csv"]

        )

        if uploaded_file is not None:

            if st.button(

                "📥 " + t["load_data"],

                use_container_width=True

            ):

                df, error = load_csv(

                    uploaded_file

                )

                if error:

                    st.error(error)

                else:

                    prepared_df, info = prepare_data(

                        df

                    )

                    if prepared_df is None:

                        st.error(

                            info.get(

                                "message",

                                "Invalid data"

                            )

                        )

                    else:

                        valid, message = validate_data(

                            prepared_df

                        )

                        if valid:

                            st.session_state.market_data = (

                                prepared_df

                            )

                            st.session_state.data_info = (

                                info

                            )

                            st.session_state.backtest_results = None

                            st.success(

                                "✓ " + t["data_loaded"]

                            )

                        else:

                            st.error(message)

    # =====================================================

    # ONLINE

    # =====================================================

    elif source == t["online_data"]:

        st.info(

            "🌐 " + t["coming_soon"]

        )

    # =====================================================

    # MT5

    # =====================================================

    elif source == t["mt5"]:

        st.info(

            "🔌 MetaTrader 5 — "

            + t["coming_soon"]

        )

    # =====================================================

    # DATA RESULTS

    # =====================================================

    if st.session_state.market_data is not None:

        df = st.session_state.market_data

        info = st.session_state.data_info

        st.divider()

        st.subheader(

            "✓ " + t["data_loaded"]

        )

        c1, c2, c3 = st.columns(3)

        c1.metric(

            t["candles"],

            f'{info["candles"]:,}'

        )

        c2.metric(

            t["missing_bars"],

            f'{info["missing_bars"]:,}'

        )

        c3.metric(

            t["duplicates"],

            f'{info["duplicates_removed"]:,}'

        )

        c4, c5 = st.columns(2)

        c4.metric(

            t["first_candle"],

            info["first_candle"]

        )

        c5.metric(

            t["last_candle"],

            info["last_candle"]

        )

        st.divider()

        if info["invalid_ohlc"] == 0:

            st.success(

                "✓ " + t["valid"]

            )

        else:

            st.warning(

                f'{t["invalid_ohlc"]}: '

                f'{info["invalid_ohlc"]}'

            )

        # =================================================

        # DATA PREVIEW

        # =================================================

        st.subheader(

            t["data_preview"]

        )

        st.dataframe(

            df.head(20),

            use_container_width=True

        )

        # =================================================

        # PRICE CHART

        # =================================================

        if "close" in df.columns:

            st.subheader(

                t["price_chart"]

            )

            chart_data = df[

                ["datetime", "close"]

            ].copy()

            chart_data = chart_data.set_index(

                "datetime"

            )

            st.line_chart(

                chart_data,

                y="close"

            )

    # =====================================================

    # STRATEGY

    # =====================================================

    st.divider()

    st.subheader(t["strategy"])

    strategy_name = st.selectbox(

        t["strategy"],

        [

            "Example Price Action Strategy"

        ]

    )

    # =====================================================

    # BACKTEST SETTINGS

    # =====================================================

    st.divider()

    st.subheader("⚙️ Backtest Settings")

    c1, c2, c3 = st.columns(3)

    with c1:

        initial_balance = st.number_input(

            "Initial Balance",

            min_value=100.0,

            value=10000.0,

            step=100.0

        )

    with c2:

        risk_percent = st.number_input(

            "Risk Per Trade (%)",

            min_value=0.01,

            max_value=100.0,

            value=1.0,

            step=0.1

        )

    with c3:

        commission = st.number_input(

            "Commission",

            min_value=0.0,

            value=0.0,

            step=0.0001,

            format="%.6f"

        )

    slippage = st.number_input(

        "Slippage",

        min_value=0.0,

        value=0.0,

        step=0.00001,

        format="%.5f"

    )

    # =====================================================

    # RUN BACKTEST

    # =====================================================

    if st.button(

        "🚀 " + t["run"],

        use_container_width=True

    ):

        if st.session_state.market_data is None:

            st.warning(

                "⚠️ Please load market data first."

            )

        else:

            try:

                market_df = (

                    st.session_state.market_data.copy()

                )

                # -----------------------------------------

                # Create strategy

                # -----------------------------------------

                if selected_strategy.startswith("〽️"):

                     strategy = ZigZagStrategy()

                else:

                      strategy = ExamplePriceActionStrategy()

                # -----------------------------------------

                # Prepare indicators

                # -----------------------------------------

                prepared_df = strategy.prepare(

                    market_df

                )

                # -----------------------------------------

                # Create backtest engine

                # -----------------------------------------

                engine = BacktestEngine(

                    initial_balance=initial_balance,

                    risk_percent=risk_percent,

                    commission_per_lot_side=commission,

                    spread_pips=0.0,

                    slippage_pips=slippage,

                    allow_long=True,

                    allow_short=True,

                    one_position_only=True

                )

                # -----------------------------------------

                # Run backtest

                # -----------------------------------------

                results = engine.run(

                    prepared_df,

                    strategy

                )

                # -----------------------------------------

                # Store results

                # -----------------------------------------

                st.session_state.backtest_results = (

                    results

                )

                st.success(

                    "✅ Backtest completed successfully."

                )

                # -----------------------------------------

                # Show quick result

                # -----------------------------------------

                st.info(

                    f"Trades: {results['total_trades']} | "

                    f"Win Rate: {results['win_rate']:.2f}% | "

                    f"Profit Factor: "

                    f"{results['profit_factor']:.2f}"

                    if results["profit_factor"] != float("inf")

                    else

                    f"Trades: {results['total_trades']} | "

                    f"Win Rate: {results['win_rate']:.2f}% | "

                    f"Profit Factor: ∞"

                )

            except Exception as e:

                st.error(

                    "❌ Backtest Error"

                )

                st.exception(e)

# =========================================================

# REPORTS

# =========================================================

with tab4:

    st.header(t["reports"])

    results = st.session_state.backtest_results

    # =====================================================

    # NO RESULTS

    # =====================================================

    if results is None:

        st.info(

            "Run a backtest first to view the results."

        )

    # =====================================================

    # RESULTS

    # =====================================================

    else:

        # -------------------------------------------------

        # MAIN METRICS

        # -------------------------------------------------

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(

            t["trades"],

            results["total_trades"]

        )

        c2.metric(

            t["win_rate"],

            f'{results["win_rate"]:.2f}%'

        )

        profit_factor = results["profit_factor"]

        if profit_factor == float("inf"):

            pf_display = "∞"

        else:

            pf_display = f"{profit_factor:.2f}"

        c3.metric(

            t["profit_factor"],

            pf_display

        )

        c4.metric(

            t["net_r"],

            f'${results["net_profit"]:.2f}'

        )

        c5.metric(

            t["max_dd"],

            f'{results["max_drawdown"]:.2f}%'

        )

        # -------------------------------------------------

        # BALANCE

        # -------------------------------------------------

        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric(

            "Initial Balance",

            f'${results["initial_balance"]:,.2f}'

        )

        c2.metric(

            "Final Balance",

            f'${results["final_balance"]:,.2f}'

        )

        c3.metric(

            "Net Profit",

            f'${results["net_profit"]:,.2f}'

        )

        # -------------------------------------------------

        # WIN / LOSS

        # -------------------------------------------------

        st.divider()

        c1, c2 = st.columns(2)

        c1.metric(

            "Winning Trades",

            results["winning_trades"]

        )

        c2.metric(

            "Losing Trades",

            results["losing_trades"]

        )

        # -------------------------------------------------

        # EQUITY CURVE

        # -------------------------------------------------

        st.divider()

        st.subheader("📈 Equity Curve")

        equity_df = results["equity_curve"]

        if (

            equity_df is not None

            and not equity_df.empty

        ):

            chart = equity_df[

                ["datetime", "equity"]

            ].copy()

            chart = chart.set_index(

                "datetime"

            )

            st.line_chart(

                chart,

                y="equity"

            )

        # -------------------------------------------------

        # TRADES

        # -------------------------------------------------

        st.divider()

        st.subheader("📋 Trades")

        trades_df = results["trades"]

        if (

            trades_df is not None

            and not trades_df.empty

        ):

            st.dataframe(

                trades_df,

                use_container_width=True

            )

        else:

            st.info(

                "No trades were generated."

            )
