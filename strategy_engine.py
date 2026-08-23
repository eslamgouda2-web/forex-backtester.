from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    name = "Base Strategy"
    description = ""

    def prepare(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.copy().reset_index(drop=True)

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, index: int) -> dict:
        """Return {} or {side, stop_loss, take_profit, metadata}."""
        raise NotImplementedError


class PriceActionReversalStrategy(BaseStrategy):
    name = "Price Action Reversal"
    description = "Engulfing reversal with candle-extreme stop."

    def __init__(self, risk_reward: float = 2.0):
        self.risk_reward = max(0.1, float(risk_reward))

    def generate_signal(self, data: pd.DataFrame, index: int) -> dict:
        if index < 1:
            return {}

        p = data.iloc[index - 1]
        c = data.iloc[index]

        po, pc = float(p.open), float(p.close)
        co, cc = float(c.open), float(c.close)
        high, low = float(c.high), float(c.low)

        bullish = pc < po and cc > co and co <= pc and cc >= po
        bearish = pc > po and cc < co and co >= pc and cc <= po

        if bullish:
            risk = cc - low
            if risk > 0:
                return {
                    "side": "LONG",
                    "stop_loss": low,
                    "take_profit": cc + risk * self.risk_reward,
                    "metadata": {"pattern": "bullish_engulfing"},
                }

        if bearish:
            risk = high - cc
            if risk > 0:
                return {
                    "side": "SHORT",
                    "stop_loss": high,
                    "take_profit": cc - risk * self.risk_reward,
                    "metadata": {"pattern": "bearish_engulfing"},
                }

        return {}


class EmaTrendPullbackStrategy(BaseStrategy):
    name = "EMA Trend Pullback"
    description = "Fast EMA recross in the direction of the slow EMA trend."

    def __init__(
        self,
        fast_period: int = 20,
        slow_period: int = 200,
        risk_reward: float = 2.0,
    ):
        self.fast_period = max(2, int(fast_period))
        self.slow_period = max(self.fast_period + 1, int(slow_period))
        self.risk_reward = max(0.1, float(risk_reward))

    def prepare(self, data: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare(data)
        df["ema_fast"] = df["close"].ewm(
            span=self.fast_period,
            adjust=False,
        ).mean()
        df["ema_slow"] = df["close"].ewm(
            span=self.slow_period,
            adjust=False,
        ).mean()
        return df

    def generate_signal(self, data: pd.DataFrame, index: int) -> dict:
        if index < self.slow_period:
            return {}

        p = data.iloc[index - 1]
        c = data.iloc[index]

        prev_close = float(p.close)
        prev_fast = float(p.ema_fast)
        close = float(c.close)
        fast = float(c.ema_fast)
        slow = float(c.ema_slow)
        high = float(c.high)
        low = float(c.low)

        long_signal = (
            prev_close <= prev_fast
            and close > fast
            and close > slow
        )

        short_signal = (
            prev_close >= prev_fast
            and close < fast
            and close < slow
        )

        if long_signal:
            risk = close - low
            if risk > 0:
                return {
                    "side": "LONG",
                    "stop_loss": low,
                    "take_profit": close + risk * self.risk_reward,
                    "metadata": {
                        "fast_ema": fast,
                        "slow_ema": slow,
                    },
                }

        if short_signal:
            risk = high - close
            if risk > 0:
                return {
                    "side": "SHORT",
                    "stop_loss": high,
                    "take_profit": close - risk * self.risk_reward,
                    "metadata": {
                        "fast_ema": fast,
                        "slow_ema": slow,
                    },
                }

        return {}


STRATEGY_REGISTRY = {
    PriceActionReversalStrategy.name: PriceActionReversalStrategy,
    EmaTrendPullbackStrategy.name: EmaTrendPullbackStrategy,
}


def create_strategy(name: str, **params) -> BaseStrategy:
    if name not in STRATEGY_REGISTRY:
        available = ", ".join(STRATEGY_REGISTRY.keys())
        raise ValueError(
            f"Unknown strategy: {name}. Available strategies: {available}"
        )

    return STRATEGY_REGISTRY[name](**params)
