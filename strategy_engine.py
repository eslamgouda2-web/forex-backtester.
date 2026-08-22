import pandas as pd

import numpy as np

# ============================================================

# FOREX BACKTESTER

# STRATEGY ENGINE V1

# ============================================================

class StrategyEngine:

    """

    Universal strategy framework.

    The strategy engine is responsible for:

    - Reading market data

    - Calculating indicators

    - Reading price action

    - Generating LONG / SHORT / EXIT signals

    - Keeping strategy logic separate from the backtest engine

    """

    def __init__(self, name="Custom Strategy", settings=None):

        self.name = name

        self.settings = settings or {}

        self.indicators = {}

        self.state = {}

        self.signal_history = []

    # ========================================================

    # DATA VALIDATION

    # ========================================================

    @staticmethod

    def validate_market_data(data):

        if data is None:

            raise ValueError("No market data supplied.")

        if data.empty:

            raise ValueError("Market data is empty.")

        required = [

            "datetime",

            "open",

            "high",

            "low",

            "close"

        ]

        missing = [

            column

            for column in required

            if column not in data.columns

        ]

        if missing:

            raise ValueError(

                f"Missing required columns: {missing}"

            )

        return True

    # ========================================================

    # PRICE ACTION

    # ========================================================

    @staticmethod

    def candle_body(row):

        return abs(

            float(row["close"])

            - float(row["open"])

        )

    @staticmethod

    def candle_range(row):

        return (

            float(row["high"])

            - float(row["low"])

        )

    @staticmethod

    def is_bullish(row):

        return (

            float(row["close"])

            > float(row["open"])

        )

    @staticmethod

    def is_bearish(row):

        return (

            float(row["close"])

            < float(row["open"])

        )

    @staticmethod

    def upper_wick(row):

        return (

            float(row["high"])

            - max(

                float(row["open"]),

                float(row["close"])

            )

        )

    @staticmethod

    def lower_wick(row):

        return (

            min(

                float(row["open"]),

                float(row["close"])

            )

            - float(row["low"])

        )

    @staticmethod

    def body_ratio(row):

        candle_range = StrategyEngine.candle_range(row)

        if candle_range <= 0:

            return 0.0

        return (

            StrategyEngine.candle_body(row)

            / candle_range

        )

    # ========================================================

    # COMMON PRICE ACTION PATTERNS

    # ========================================================

    @staticmethod

    def bullish_engulfing(data, i):

        if i < 1:

            return False

        previous = data.iloc[i - 1]

        current = data.iloc[i]

        return (

            StrategyEngine.is_bearish(previous)

            and StrategyEngine.is_bullish(current)

            and current["open"] <= previous["close"]

            and current["close"] >= previous["open"]

        )

    @staticmethod

    def bearish_engulfing(data, i):

        if i < 1:

            return False

        previous = data.iloc[i - 1]

        current = data.iloc[i]

        return (

            StrategyEngine.is_bullish(previous)

            and StrategyEngine.is_bearish(current)

            and current["open"] >= previous["close"]

            and current["close"] <= previous["open"]

        )

    @staticmethod

    def bullish_pin_bar(

        data,

        i,

        wick_ratio=2.0

    ):

        if i < 0:

            return False

        row = data.iloc[i]

        body = StrategyEngine.candle_body(row)

        lower_wick = StrategyEngine.lower_wick(row)

        if body <= 0:

            return False

        return (

            lower_wick >= body * wick_ratio

            and float(row["close"])

            > float(row["open"])

        )

    @staticmethod

    def bearish_pin_bar(

        data,

        i,

        wick_ratio=2.0

    ):

        if i < 0:

            return False

        row = data.iloc[i]

        body = StrategyEngine.candle_body(row)

        upper_wick = StrategyEngine.upper_wick(row)

        if body <= 0:

            return False

        return (

            upper_wick >= body * wick_ratio

            and float(row["close"])

            < float(row["open"])

        )

    # ========================================================

    # MOVING AVERAGE

    # ========================================================

    @staticmethod

    def sma(series, period):

        return series.rolling(

            window=int(period)

        ).mean()

    @staticmethod

    def ema(series, period):

        return series.ewm(

            span=int(period),

            adjust=False

        ).mean()

    # ========================================================

    # RSI

    # ========================================================

    @staticmethod

    def rsi(series, period=14):

        delta = series.diff()

        gains = delta.clip(lower=0)

        losses = -delta.clip(upper=0)

        average_gain = gains.ewm(

            alpha=1 / period,

            adjust=False

        ).mean()

        average_loss = losses.ewm(

            alpha=1 / period,

            adjust=False

        ).mean()

        rs = (

            average_gain

            / average_loss.replace(0, np.nan)

        )

        result = 100 - (

            100 / (1 + rs)

        )

        return result.fillna(50)

    # ========================================================

    # ATR

    # ========================================================

    @staticmethod

    def atr(data, period=14):

        previous_close = data["close"].shift(1)

        true_range = pd.concat(

            [

                data["high"] - data["low"],

                (

                    data["high"]

                    - previous_close

                ).abs(),

                (

                    data["low"]

                    - previous_close

                ).abs()

            ],

            axis=1

        ).max(axis=1)

        return true_range.rolling(

            int(period)

        ).mean()

    # ========================================================

    # INDICATOR REGISTRATION

    # ========================================================

    def calculate_indicators(self, data):

        df = data.copy()

        # --------------------------------------------

        # Moving averages

        # --------------------------------------------

        for period in [

            9,

            20,

            50,

            100,

            200

        ]:

            df[f"sma_{period}"] = self.sma(

                df["close"],

                period

            )

            df[f"ema_{period}"] = self.ema(

                df["close"],

                period

            )

        # --------------------------------------------

        # RSI

        # --------------------------------------------

        df["rsi_14"] = self.rsi(

            df["close"],

            14

        )

        # --------------------------------------------

        # ATR

        # --------------------------------------------

        df["atr_14"] = self.atr(

            df,

            14

        )

        self.indicators = {

            "sma_9": df["sma_9"],

            "sma_20": df["sma_20"],

            "sma_50": df["sma_50"],

            "sma_100": df["sma_100"],

            "sma_200": df["sma_200"],

            "ema_9": df["ema_9"],

            "ema_20": df["ema_20"],

            "ema_50": df["ema_50"],

            "ema_100": df["ema_100"],

            "ema_200": df["ema_200"],

            "rsi_14": df["rsi_14"],

            "atr_14": df["atr_14"]

        }

        return df

    # ========================================================

    # SIGNAL CREATOR

    # ========================================================

    @staticmethod

    def create_signal(

        side=None,

        entry=None,

        stop_loss=None,

        take_profit=None,

        reason="",

        confidence=0.0,

        close_position=False

    ):

        return {

            "side": side,

            "entry": entry,

            "stop_loss": stop_loss,

            "take_profit": take_profit,

            "reason": reason,

            "confidence": float(confidence),

            "close_position": close_position

        }

    # ========================================================

    # GENERIC STRATEGY

    # ========================================================

    def generate_signal(self, data, i):

        """

        Override this method when creating

        a specific trading strategy.

        """

        if i < 1:

            return self.create_signal()

        return self.create_signal()

    # ========================================================

    # RUN STRATEGY

    # ========================================================

    def prepare(self, data):

        self.validate_market_data(data)

        df = data.copy()

        df = df.sort_values(

            "datetime"

        ).reset_index(drop=True)

        df = self.calculate_indicators(

            df

        )

        return df

    def run(self, data):

        df = self.prepare(data)

        self.signal_history = []

        for i in range(len(df)):

            signal = self.generate_signal(

                df,

                i

            )

            if signal is None:

                signal = self.create_signal()

            signal["index"] = i

            signal["datetime"] = df.iloc[i][

                "datetime"

            ]

            self.signal_history.append(

                signal

            )

        return df, pd.DataFrame(

            self.signal_history

        )

# ============================================================

# EXAMPLE STRATEGY

# ============================================================

class ExamplePriceActionStrategy(StrategyEngine):

    def __init__(

        self,

        name="Example Price Action Strategy",

        settings=None

    ):

        super().__init__(

            name=name,

            settings=settings

        )

    def generate_signal(self, data, i):

        if i < 20:

            return self.create_signal()

        row = data.iloc[i]

        close = float(row["close"])

        # --------------------------------------------

        # Bullish price action

        # --------------------------------------------

        bullish = (

            self.bullish_engulfing(

                data,

                i

            )

            or

            self.bullish_pin_bar(

                data,

                i

            )

        )

        # --------------------------------------------

        # Bearish price action

        # --------------------------------------------

        bearish = (

            self.bearish_engulfing(

                data,

                i

            )

            or

            self.bearish_pin_bar(

                data,

                i

            )

        )

        # --------------------------------------------

        # Trend filter

        # --------------------------------------------

        above_200 = (

            close

            > float(row["ema_200"])

        )

        below_200 = (

            close

            < float(row["ema_200"])

        )

        atr = float(row["atr_14"])

        if not np.isfinite(atr):

            return self.create_signal()

        # --------------------------------------------

        # LONG

        # --------------------------------------------

        if bullish and above_200:

            entry = close

            stop_loss = (

                float(row["low"])

                - atr * 0.20

            )

            risk = entry - stop_loss

            if risk > 0:

                take_profit = (

                    entry

                    + risk * 2

                )

                return self.create_signal(

                    side="LONG",

                    entry=entry,

                    stop_loss=stop_loss,

                    take_profit=take_profit,

                    reason="Bullish Price Action + EMA 200",

                    confidence=0.75

                )

        # --------------------------------------------

        # SHORT

        # --------------------------------------------

        if bearish and below_200:

            entry = close

            stop_loss = (

                float(row["high"])

                + atr * 0.20

            )

            risk = stop_loss - entry

            if risk > 0:

                take_profit = (

                    entry

                    - risk * 2

                )

                return self.create_signal(

                    side="SHORT",

                    entry=entry,

                    stop_loss=stop_loss,

                    take_profit=take_profit,

                    reason="Bearish Price Action + EMA 200",

                    confidence=0.75

                )

        return self.create_signal()
        # ============================================================

# ZIGZAG + EMA 200 STRATEGY

# ============================================================

class ZigZagStrategy(StrategyEngine):

    def __init__(

        self,

        name="ZigZag + EMA 200",

        settings=None

    ):

        super().__init__(

            name=name,

            settings=settings

        )

        self.settings = settings or {}

        self.pivot_left = int(

            self.settings.get("pivot_left", 2)

        )

        self.pivot_right = int(

            self.settings.get("pivot_right", 2)

        )

        self.risk_reward = float(

            self.settings.get("risk_reward", 2.0)

        )

        self.ma_period = int(

            self.settings.get("ma_period", 200)

        )

        self.last_broken_high = None

        self.last_broken_low = None

    # ========================================================

    # PIVOT HIGH

    # ========================================================

    @staticmethod

    def is_pivot_high(data, index, left=2, right=2):

        if index < left:

            return False

        if index + right >= len(data):

            return False

        high = float(data.iloc[index]["high"])

        for j in range(

            index - left,

            index + right + 1

        ):

            if j == index:

                continue

            if float(data.iloc[j]["high"]) >= high:

                return False

        return True

    # ========================================================

    # PIVOT LOW

    # ========================================================

    @staticmethod

    def is_pivot_low(data, index, left=2, right=2):

        if index < left:

            return False

        if index + right >= len(data):

            return False

        low = float(data.iloc[index]["low"])

        for j in range(

            index - left,

            index + right + 1

        ):

            if j == index:

                continue

            if float(data.iloc[j]["low"]) <= low:

                return False

        return True

    # ========================================================

    # GET CONFIRMED ZIGZAG SWINGS

    # ========================================================

    def get_swings(self, data, current_index):

        right = self.pivot_right

        left = self.pivot_left

        # The pivot at this position is only confirmed

        # after "right" candles have closed.

        confirmed_index = current_index - right

        if confirmed_index <= left:

            return [], []

        highs = []

        lows = []

        start = max(

            left,

            confirmed_index - 500

        )

        end = confirmed_index + 1

        for i in range(start, end):

            if self.is_pivot_high(

                data,

                i,

                left,

                right

            ):

                highs.append({

                    "index": i,

                    "price": float(

                        data.iloc[i]["high"]

                    )

                })

            if self.is_pivot_low(

                data,

                i,

                left,

                right

            ):

                lows.append({

                    "index": i,

                    "price": float(

                        data.iloc[i]["low"]

                    )

                })

        return highs, lows

    # ========================================================

    # GENERATE SIGNAL

    # ========================================================

    def generate_signal(self, data, i):

        # ----------------------------------------------------

        # Not enough candles

        # ----------------------------------------------------

        minimum_bars = max(

            self.ma_period,

            50

        )

        if i < minimum_bars:

            return self.create_signal()

        row = data.iloc[i]

        close = float(row["close"])

        high = float(row["high"])

        low = float(row["low"])

        # ----------------------------------------------------

        # EMA / MA 200

        # ----------------------------------------------------

        closes = data["close"].astype(float)

        ma200 = (

            closes

            .iloc[:i + 1]

            .rolling(self.ma_period)

            .mean()

            .iloc[-1]

        )

        if pd.isna(ma200):

            return self.create_signal()

        # ----------------------------------------------------

        # Get confirmed ZigZag swings

        # ----------------------------------------------------

        swing_highs, swing_lows = self.get_swings(

            data,

            i

        )

        # ----------------------------------------------------

        # Need at least 3 swing highs/lows

        # ----------------------------------------------------

        if len(swing_highs) < 3 and len(swing_lows) < 3:

            return self.create_signal()

        # ====================================================

        # LONG SETUP

        # ====================================================

        if len(swing_highs) >= 3:

            third_high = swing_highs[-3]

            third_high_price = third_high["price"]

            # Only consider a fresh break

            if (

                self.last_broken_high

                != third_high["index"]

            ):

                # Trend filter

                bullish_trend = close > ma200

                # Break of the third confirmed swing high

                bullish_break = close > third_high_price

                if bullish_trend and bullish_break:

                    # Latest confirmed swing low

                    if len(swing_lows) > 0:

                        latest_low = swing_lows[-1]

                        stop_loss = latest_low["price"]

                        risk = close - stop_loss

                        if risk > 0:

                            take_profit = (

                                close

                                + risk * self.risk_reward

                            )

                            self.last_broken_high = (

                                third_high["index"]

                            )

                            return self.create_signal(

                                side="LONG",

                                entry=close,

                                stop_loss=stop_loss,

                                take_profit=take_profit,

                                reason=(

                                    "ZigZag 3rd High Break "

                                    "+ MA 200"

                                ),

                                confidence=0.80

                            )

        # ====================================================

        # SHORT SETUP

        # ====================================================

        if len(swing_lows) >= 3:

            third_low = swing_lows[-3]

            third_low_price = third_low["price"]

            # Only consider a fresh break

            if (

                self.last_broken_low

                != third_low["index"]

            ):

                # Trend filter

                bearish_trend = close < ma200

                # Break of the third confirmed swing low

                bearish_break = close < third_low_price

                if bearish_trend and bearish_break:

                    # Latest confirmed swing high

                    if len(swing_highs) > 0:

                        latest_high = swing_highs[-1]

                        stop_loss = latest_high["price"]

                        risk = stop_loss - close

                        if risk > 0:

                            take_profit = (

                                close

                                - risk * self.risk_reward

                            )

                            self.last_broken_low = (

                                third_low["index"]

                            )

                            return self.create_signal(

                                side="SHORT",

                                entry=close,

                                stop_loss=stop_loss,

                                take_profit=take_profit,

                                reason=(

                                    "ZigZag 3rd Low Break "

                                    "+ MA 200"

                                ),

                                confidence=0.80

                            )

        # ----------------------------------------------------

        # No signal

        # ----------------------------------------------------

        return self.create_signal()
