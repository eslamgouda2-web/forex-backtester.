import pandas as pd

import numpy as np

from bisect import bisect_right

# ============================================================

# FOREX BACKTESTER

# STRATEGY ENGINE - OPTIMIZED VERSION

# ============================================================

class StrategyEngine:

    """

    Universal strategy framework.

    Responsibilities:

    - Validate market data

    - Calculate indicators

    - Detect price action

    - Generate trading signals

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

    # PRICE ACTION HELPERS

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

        total_range = StrategyEngine.candle_range(row)

        if total_range <= 0:

            return 0.0

        return (

            StrategyEngine.candle_body(row)

            / total_range

        )

    # ========================================================

    # PRICE ACTION PATTERNS

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

            and float(current["open"])

            <= float(previous["close"])

            and float(current["close"])

            >= float(previous["open"])

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

            and float(current["open"])

            >= float(previous["close"])

            and float(current["close"])

            <= float(previous["open"])

        )

    @staticmethod

    def bullish_pin_bar(

        data,

        i,

        wick_ratio=2.0

    ):

        if i < 0 or i >= len(data):

            return False

        row = data.iloc[i]

        body = StrategyEngine.candle_body(row)

        lower_wick = StrategyEngine.lower_wick(row)

        if body <= 0:

            return False

        return (

            lower_wick >= body * wick_ratio

            and StrategyEngine.is_bullish(row)

        )

    @staticmethod

    def bearish_pin_bar(

        data,

        i,

        wick_ratio=2.0

    ):

        if i < 0 or i >= len(data):

            return False

        row = data.iloc[i]

        body = StrategyEngine.candle_body(row)

        upper_wick = StrategyEngine.upper_wick(row)

        if body <= 0:

            return False

        return (

            upper_wick >= body * wick_ratio

            and StrategyEngine.is_bearish(row)

        )

    # ========================================================

    # INDICATORS

    # ========================================================

    @staticmethod

    def sma(series, period):

        period = int(period)

        return series.rolling(

            window=period,

            min_periods=period

        ).mean()

    @staticmethod

    def ema(series, period):

        period = int(period)

        return series.ewm(

            span=period,

            adjust=False,

            min_periods=period

        ).mean()

    @staticmethod

    def rsi(series, period=14):

        period = int(period)

        delta = series.diff()

        gains = delta.clip(lower=0)

        losses = -delta.clip(upper=0)

        average_gain = gains.ewm(

            alpha=1 / period,

            adjust=False,

            min_periods=period

        ).mean()

        average_loss = losses.ewm(

            alpha=1 / period,

            adjust=False,

            min_periods=period

        ).mean()

        rs = (

            average_gain

            / average_loss.replace(0, np.nan)

        )

        result = 100 - (

            100 / (1 + rs)

        )

        return result.fillna(50.0)

    @staticmethod

    def atr(data, period=14):

        period = int(period)

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

            period,

            min_periods=period

        ).mean()

    # ========================================================

    # INDICATOR CALCULATION

    # ========================================================

    def calculate_indicators(self, data):

        df = data.copy()

        periods = [

            9,

            20,

            50,

            100,

            200

        ]

        for period in periods:

            df[f"sma_{period}"] = self.sma(

                df["close"],

                period

            )

            df[f"ema_{period}"] = self.ema(

                df["close"],

                period

            )

        df["rsi_14"] = self.rsi(

            df["close"],

            14

        )

        df["atr_14"] = self.atr(

            df,

            14

        )

        self.indicators = {

            column: df[column]

            for column in df.columns

            if (

                column.startswith("sma_")

                or column.startswith("ema_")

                or column.startswith("rsi_")

                or column.startswith("atr_")

            )

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

            "close_position": bool(close_position)

        }

    # ========================================================

    # GENERIC STRATEGY

    # ========================================================

    def generate_signal(self, data, i):

        return self.create_signal()

    # ========================================================

    # PREPARE DATA

    # ========================================================

    def prepare(self, data):

        self.validate_market_data(data)

        df = data.copy()

        df = df.sort_values(

            "datetime"

        ).reset_index(

            drop=True

        )

        numeric_columns = [

            "open",

            "high",

            "low",

            "close"

        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(

                df[column],

                errors="coerce"

            )

        df = df.dropna(

            subset=numeric_columns

        ).reset_index(

            drop=True

        )

        df = self.calculate_indicators(df)

        return df

    # ========================================================

    # RUN STRATEGY

    # ========================================================

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

            signal["datetime"] = (

                df.iloc[i]["datetime"]

            )

            self.signal_history.append(

                signal

            )

        return (

            df,

            pd.DataFrame(self.signal_history)

        )

# ============================================================

# EXAMPLE PRICE ACTION STRATEGY

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

    def generate_signal(

        self,

        data,

        i

    ):

        if i < 200:

            return self.create_signal()

        row = data.iloc[i]

        close = float(row["close"])

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

        ema200 = row.get(

            "ema_200",

            np.nan

        )

        atr = row.get(

            "atr_14",

            np.nan

        )

        if (

            pd.isna(ema200)

            or pd.isna(atr)

        ):

            return self.create_signal()

        ema200 = float(ema200)

        atr = float(atr)

        # LONG

        if bullish and close > ema200:

            entry = close

            stop_loss = (

                float(row["low"])

                - atr * 0.20

            )

            risk = (

                entry

                - stop_loss

            )

            if risk > 0:

                take_profit = (

                    entry

                    + risk * 2.0

                )

                return self.create_signal(

                    side="LONG",

                    entry=entry,

                    stop_loss=stop_loss,

                    take_profit=take_profit,

                    reason=(

                        "Bullish Price Action "

                        "+ EMA 200"

                    ),

                    confidence=0.75

                )

        # SHORT

        if bearish and close < ema200:

            entry = close

            stop_loss = (

                float(row["high"])

                + atr * 0.20

            )

            risk = (

                stop_loss

                - entry

            )

            if risk > 0:

                take_profit = (

                    entry

                    - risk * 2.0

                )

                return self.create_signal(

                    side="SHORT",

                    entry=entry,

                    stop_loss=stop_loss,

                    take_profit=take_profit,

                    reason=(

                        "Bearish Price Action "

                        "+ EMA 200"

                    ),

                    confidence=0.75

                )

        return self.create_signal()

# ============================================================

# ZIGZAG + EMA STRATEGY

# OPTIMIZED

# ============================================================

class ZigZagStrategy(StrategyEngine):

    """

    Optimized ZigZag strategy.

    Entry logic:

    LONG

    ----

    1. Price above EMA

    2. At least 3 confirmed swing highs

    3. Price breaks the third-most-recent confirmed high

    4. Stop loss below latest confirmed swing low

    SHORT

    -----

    1. Price below EMA

    2. At least 3 confirmed swing lows

    3. Price breaks the third-most-recent confirmed low

    4. Stop loss above latest confirmed swing high

    Important:

    Pivot calculations are prepared ONCE.

    The old version scanned up to 500 candles again

    on every single candle.

    """

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

        self.pivot_left = max(

            1,

            int(

                self.settings.get(

                    "pivot_left",

                    2

                )

            )

        )

        self.pivot_right = max(

            1,

            int(

                self.settings.get(

                    "pivot_right",

                    2

                )

            )

        )

        self.risk_reward = max(

            0.1,

            float(

                self.settings.get(

                    "risk_reward",

                    2.0

                )

            )

        )

        self.ma_period = max(

            2,

            int(

                self.settings.get(

                    "ma_period",

                    200

                )

            )

        )

        self.last_broken_high = None

        self.last_broken_low = None

        self._pivot_high_indices = []

        self._pivot_low_indices = []

    # ========================================================

    # PIVOT DETECTION

    # ========================================================

    @staticmethod

    def is_pivot_high(

        data,

        index,

        left=2,

        right=2

    ):

        if index < left:

            return False

        if index + right >= len(data):

            return False

        high = float(

            data.iloc[index]["high"]

        )

        for j in range(

            index - left,

            index + right + 1

        ):

            if j == index:

                continue

            if (

                float(data.iloc[j]["high"])

                >= high

            ):

                return False

        return True

    @staticmethod

    def is_pivot_low(

        data,

        index,

        left=2,

        right=2

    ):

        if index < left:

            return False

        if index + right >= len(data):

            return False

        low = float(

            data.iloc[index]["low"]

        )

        for j in range(

            index - left,

            index + right + 1

        ):

            if j == index:

                continue

            if (

                float(data.iloc[j]["low"])

                <= low

            ):

                return False

        return True

    # ========================================================

    # FAST PIVOT PRECALCULATION

    # ========================================================

    def _calculate_pivots(

        self,

        df

    ):

        n = len(df)

        highs = (

            df["high"]

            .astype(float)

            .to_numpy()

        )

        lows = (

            df["low"]

            .astype(float)

            .to_numpy()

        )

        pivot_high = np.ones(

            n,

            dtype=bool

        )

        pivot_low = np.ones(

            n,

            dtype=bool

        )

        left = self.pivot_left

        right = self.pivot_right

        # Remove invalid edges

        pivot_high[:left] = False

        pivot_low[:left] = False

        if right > 0:

            pivot_high[n - right:] = False

            pivot_low[n - right:] = False

        # Strict pivot comparison.

        # This preserves the old behavior where equal highs

        # or equal lows do NOT count as pivots.

        for offset in range(

            1,

            left + 1

        ):

            pivot_high[left:n-right] &= (

                highs[left:n-right]

                > highs[left-offset:n-right-offset]

            )

            pivot_low[left:n-right] &= (

                lows[left:n-right]

                < lows[left-offset:n-right-offset]

            )

        for offset in range(

            1,

            right + 1

        ):

            pivot_high[left:n-right] &= (

                highs[left:n-right]

                > highs[left+offset:n-right+offset]

            )

            pivot_low[left:n-right] &= (

                lows[left:n-right]

                < lows[left+offset:n-right+offset]

            )

        df["zigzag_pivot_high"] = pivot_high

        df["zigzag_pivot_low"] = pivot_low

        self._pivot_high_indices = (

            np.flatnonzero(

                pivot_high

            ).astype(int).tolist()

        )

        self._pivot_low_indices = (

            np.flatnonzero(

                pivot_low

            ).astype(int).tolist()

        )

        return df

    # ========================================================

    # PREPARE

    # ========================================================

    def prepare(

        self,

        data

    ):

        df = super().prepare(data)

        # Custom EMA period if not already calculated

        ema_column = (

            f"ema_{self.ma_period}"

        )

        if ema_column not in df.columns:

            df[ema_column] = self.ema(

                df["close"],

                self.ma_period

            )

        # Calculate all ZigZag pivots ONCE

        df = self._calculate_pivots(

            df

        )

        # Reset break memory for new backtest

        self.last_broken_high = None

        self.last_broken_low = None

        return df

    # ========================================================

    # GET CONFIRMED SWINGS - FAST

    # ========================================================

    def _get_confirmed_indices(

        self,

        current_index,

        indices

    ):

        # Pivot at index X becomes available only after

        # pivot_right candles have closed.

        confirmed_index = (

            current_index

            - self.pivot_right

        )

        if confirmed_index < 0:

            return []

        position = bisect_right(

            indices,

            confirmed_index

        )

        return indices[:position]

    # ========================================================

    # GET SWINGS

    # ========================================================

    def get_swings(

        self,

        data,

        current_index

    ):

        confirmed_highs = (

            self._get_confirmed_indices(

                current_index,

                self._pivot_high_indices

            )

        )

        confirmed_lows = (

            self._get_confirmed_indices(

                current_index,

                self._pivot_low_indices

            )

        )

        highs = [

            {

                "index": index,

                "price": float(

                    data.iloc[index]["high"]

                )

            }

            for index in confirmed_highs

        ]

        lows = [

            {

                "index": index,

                "price": float(

                    data.iloc[index]["low"]

                )

            }

            for index in confirmed_lows

        ]

        return highs, lows

    # ========================================================

    # GENERATE SIGNAL

    # ========================================================

    def generate_signal(

        self,

        data,

        i

    ):

        minimum_bars = max(

            self.ma_period,

            self.pivot_left

            + self.pivot_right

            + 10

        )

        if i < minimum_bars:

            return self.create_signal()

        row = data.iloc[i]

        close = float(

            row["close"]

        )

        ema_column = (

            f"ema_{self.ma_period}"

        )

        ma_value = row.get(

            ema_column,

            np.nan

        )

        if pd.isna(ma_value):

            return self.create_signal()

        ma_value = float(ma_value)

        # Get ONLY confirmed swings.

        # No 500-candle rescanning here.

        high_indices = (

            self._get_confirmed_indices(

                i,

                self._pivot_high_indices

            )

        )

        low_indices = (

            self._get_confirmed_indices(

                i,

                self._pivot_low_indices

            )

        )

        # ====================================================

        # LONG SETUP

        # ====================================================

        if len(high_indices) >= 3:

            third_high_index = (

                high_indices[-3]

            )

            third_high_price = float(

                data.iloc[

                    third_high_index

                ]["high"]

            )

            bullish_trend = (

                close > ma_value

            )

            bullish_break = (

                close > third_high_price

            )

            if (

                bullish_trend

                and bullish_break

            ):

                # Prevent duplicate signal for same level

                if (

                    self.last_broken_high

                    != third_high_index

                ):

                    if len(low_indices) > 0:

                        latest_low_index = (

                            low_indices[-1]

                        )

                        stop_loss = float(

                            data.iloc[

                                latest_low_index

                            ]["low"]

                        )

                        risk = (

                            close

                            - stop_loss

                        )

                        if risk > 0:

                            take_profit = (

                                close

                                + risk

                                * self.risk_reward

                            )

                            self.last_broken_high = (

                                third_high_index

                            )

                            return self.create_signal(

                                side="LONG",

                                entry=close,

                                stop_loss=stop_loss,

                                take_profit=take_profit,

                                reason=(

                                    "ZigZag 3rd High Break "

                                    f"+ EMA {self.ma_period}"

                                ),

                                confidence=0.80

                            )

        # ====================================================

        # SHORT SETUP

        # ====================================================

        if len(low_indices) >= 3:

            third_low_index = (

                low_indices[-3]

            )

            third_low_price = float(

                data.iloc[

                    third_low_index

                ]["low"]

            )

            bearish_trend = (

                close < ma_value

            )

            bearish_break = (

                close < third_low_price

            )

            if (

                bearish_trend

                and bearish_break

            ):

                # Prevent duplicate signal for same level

                if (

                    self.last_broken_low

                    != third_low_index

                ):

                    if len(high_indices) > 0:

                        latest_high_index = (

                            high_indices[-1]

                        )

                        stop_loss = float(

                            data.iloc[

                                latest_high_index

                            ]["high"]

                        )

                        risk = (

                            stop_loss

                            - close

                        )

                        if risk > 0:

                            take_profit = (

                                close

                                - risk

                                * self.risk_reward

                            )

                            self.last_broken_low = (

                                third_low_index

                            )

                            return self.create_signal(

                                side="SHORT",

                                entry=close,

                                stop_loss=stop_loss,

                                take_profit=take_profit,

                                reason=(

                                    "ZigZag 3rd Low Break "

                                    f"+ EMA {self.ma_period}"

                                ),

                                confidence=0.80

                            )

        return self.create_signal()
