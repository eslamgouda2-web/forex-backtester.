import pandas as pd
import numpy as np

# ============================================================
# FOREX BACKTESTER
# BACKTEST ENGINE V2
#
# Execution model:
# - Strategy signal is evaluated at candle close.
# - New market entries execute at the NEXT candle open.
# - Spread is modeled with Bid/Ask.
# - Slippage is modeled in pips and always works against the trade.
# - If SL and TP are both touched inside the same OHLC candle,
#   SL is assumed to happen first (conservative default).
# - A newly calculated trailing stop becomes active from the
#   NEXT candle, avoiding same-candle look-ahead.
# ============================================================


class BacktestEngine:

    def __init__(
        self,
        initial_balance=10000.0,
        risk_percent=1.0,
        commission_per_lot_side=0.0,
        spread_pips=0.0,
        slippage_pips=0.0,
        pip_size=0.0001,
        lot_size=100000.0,
        pip_value_per_lot=None,
        risk_based_on="balance",
        allow_long=True,
        allow_short=True,
        one_position_only=True,
    ):
        self.initial_balance = float(initial_balance)
        self.balance = float(initial_balance)

        self.risk_percent = float(risk_percent)

        self.commission_per_lot_side = float(
            commission_per_lot_side
        )

        self.spread_pips = max(0.0, float(spread_pips))
        self.slippage_pips = max(0.0, float(slippage_pips))
        self.pip_size = float(pip_size)

        self.lot_size = float(lot_size)

        # Optional fixed pip value in account currency per
        # standard lot. If omitted, the engine derives a
        # simple quote-currency approximation from price.
        self.pip_value_per_lot = (
            None
            if pip_value_per_lot is None
            else float(pip_value_per_lot)
        )

        self.risk_based_on = str(risk_based_on).lower()

        self.allow_long = bool(allow_long)
        self.allow_short = bool(allow_short)
        self.one_position_only = bool(one_position_only)

        self.position = None
        self.pending_order = None
        self.pending_close = None

        self.trades = []
        self.equity_curve = []

        self._validate_settings()

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate_settings(self):
        if self.initial_balance <= 0:
            raise ValueError(
                "initial_balance must be greater than 0."
            )

        if self.risk_percent < 0:
            raise ValueError(
                "risk_percent cannot be negative."
            )

        if self.pip_size <= 0:
            raise ValueError(
                "pip_size must be greater than 0."
            )

        if self.lot_size <= 0:
            raise ValueError(
                "lot_size must be greater than 0."
            )

        if self.commission_per_lot_side < 0:
            raise ValueError(
                "commission_per_lot_side cannot be negative."
            )

        if self.risk_based_on not in {
            "balance",
            "equity",
        }:
            raise ValueError(
                "risk_based_on must be 'balance' or 'equity'."
            )

    # ========================================================
    # EXECUTION HELPERS
    # ========================================================

    def _spread_price(self):
        return self.spread_pips * self.pip_size

    def _slippage_price(self):
        return self.slippage_pips * self.pip_size

    def _bid(self, mid_price):
        return float(mid_price) - (
            self._spread_price() / 2.0
        )

    def _ask(self, mid_price):
        return float(mid_price) + (
            self._spread_price() / 2.0
        )

    def _entry_price(self, side, mid_price):
        mid_price = float(mid_price)
        slippage = self._slippage_price()

        if side == "LONG":
            return self._ask(mid_price) + slippage

        if side == "SHORT":
            return self._bid(mid_price) - slippage

        raise ValueError(
            f"Unsupported side: {side}"
        )

    def _exit_price(self, side, market_price):
        market_price = float(market_price)
        slippage = self._slippage_price()

        # market_price represents the executable Bid for LONG
        # exits and Ask for SHORT exits.
        if side == "LONG":
            return market_price - slippage

        if side == "SHORT":
            return market_price + slippage

        raise ValueError(
            f"Unsupported side: {side}"
        )

    # ========================================================
    # POSITION SIZE
    # ========================================================

    def _get_risk_base(self):
        if self.risk_based_on == "equity":
            if self.equity_curve:
                return float(
                    self.equity_curve[-1]["equity"]
                )
            return float(self.balance)

        return float(self.balance)

    def _pip_value_per_unit(
        self,
        price
    ):
        if self.pip_value_per_lot is not None:
            return (
                self.pip_value_per_lot
                / self.lot_size
            )

        # Generic quote-currency approximation.
        # For EURUSD-like pairs with USD account currency,
        # pip value per unit is approximately pip_size.
        return self.pip_size

    def calculate_position_size(
        self,
        entry,
        stop_loss
    ):
        if stop_loss is None:
            return 0.0

        entry = float(entry)
        stop_loss = float(stop_loss)

        stop_distance = abs(
            entry - stop_loss
        )

        if stop_distance <= 0:
            return 0.0

        risk_base = self._get_risk_base()

        risk_money = (
            risk_base
            * (self.risk_percent / 100.0)
        )

        if risk_money <= 0:
            return 0.0

        pip_distance = (
            stop_distance
            / self.pip_size
        )

        if pip_distance <= 0:
            return 0.0

        pip_value_per_unit = (
            self._pip_value_per_unit(entry)
        )

        risk_per_unit = (
            pip_distance
            * pip_value_per_unit
        )

        if risk_per_unit <= 0:
            return 0.0

        size = (
            risk_money
            / risk_per_unit
        )

        return float(size)

    # ========================================================
    # OPEN POSITION
    # ========================================================

    def open_position(
        self,
        side,
        entry,
        stop_loss=None,
        take_profit=None,
        timestamp=None,
        entry_reference=None,
    ):
        if self.position is not None:
            return False

        if side not in {"LONG", "SHORT"}:
            return False

        if side == "LONG" and not self.allow_long:
            return False

        if side == "SHORT" and not self.allow_short:
            return False

        actual_entry = self._entry_price(
            side,
            entry
        )

        if stop_loss is not None:
            stop_loss = float(stop_loss)

        if take_profit is not None:
            take_profit = float(take_profit)

        # Validate SL direction before sizing.
        if side == "LONG" and stop_loss is not None:
            if stop_loss >= actual_entry:
                return False

        if side == "SHORT" and stop_loss is not None:
            if stop_loss <= actual_entry:
                return False

        size = self.calculate_position_size(
            actual_entry,
            stop_loss
        )

        # V2 does NOT silently open a size=1 trade when
        # position sizing fails. Invalid risk settings reject
        # the trade instead.
        if size <= 0:
            return False

        self.position = {
            "side": side,
            "entry": actual_entry,
            "entry_reference": (
                actual_entry
                if entry_reference is None
                else float(entry_reference)
            ),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "initial_stop_loss": stop_loss,
            "size": size,
            "entry_time": timestamp,
            "highest_price": actual_entry,
            "lowest_price": actual_entry,
            "trailing_active": False,
        }

        return True

    # ========================================================
    # CLOSE POSITION
    # ========================================================

    def close_position(
        self,
        exit_price,
        timestamp=None,
        reason="Manual"
    ):
        if self.position is None:
            return None

        position = self.position

        side = position["side"]
        entry = position["entry"]
        size = position["size"]

        actual_exit = self._exit_price(
            side,
            exit_price
        )

        if side == "LONG":
            pnl = (
                actual_exit - entry
            ) * size
        else:
            pnl = (
                entry - actual_exit
            ) * size

        lots = size / self.lot_size

        commission_cost = (
            abs(lots)
            * self.commission_per_lot_side
            * 2.0
        )

        net_pnl = (
            pnl - commission_cost
        )

        self.balance += net_pnl

        initial_stop = position.get(
            "initial_stop_loss"
        )

        risk_distance = None

        if initial_stop is not None:
            risk_distance = abs(
                entry - initial_stop
            )

        if risk_distance and risk_distance > 0:
            if side == "LONG":
                r_multiple = (
                    actual_exit - entry
                ) / risk_distance
            else:
                r_multiple = (
                    entry - actual_exit
                ) / risk_distance
        else:
            r_multiple = None

        trade = {
            "side": side,
            "entry_time": position["entry_time"],
            "exit_time": timestamp,
            "entry": entry,
            "exit": actual_exit,
            "stop_loss": position["stop_loss"],
            "initial_stop_loss": initial_stop,
            "take_profit": position["take_profit"],
            "size_units": size,
            "lots": lots,
            "gross_pnl": pnl,
            "commission": commission_cost,
            "net_pnl": net_pnl,
            "r_multiple": r_multiple,
            "reason": reason,
            "balance": self.balance,
        }

        self.trades.append(trade)

        self.position = None

        return trade

    # ========================================================
    # STOP / TARGET EXECUTION PRICE
    # ========================================================

    def _resolve_open_gap_exit(
        self,
        open_price
    ):
        """Close an existing position if the new candle opens
        beyond its SL/TP. The actual executable open is used,
        rather than pretending the requested level was filled.
        """
        if self.position is None:
            return None

        position = self.position
        side = position["side"]
        stop_loss = position["stop_loss"]
        take_profit = position["take_profit"]

        open_price = float(open_price)

        if side == "LONG":
            bid_open = self._bid(open_price)

            if (
                stop_loss is not None
                and bid_open <= stop_loss
            ):
                return self.close_position(
                    open_price,
                    self._current_timestamp,
                    "Stop Loss Gap"
                )

            if (
                take_profit is not None
                and bid_open >= take_profit
            ):
                return self.close_position(
                    open_price,
                    self._current_timestamp,
                    "Take Profit Gap"
                )

        elif side == "SHORT":
            ask_open = self._ask(open_price)

            if (
                stop_loss is not None
                and ask_open >= stop_loss
            ):
                return self.close_position(
                    open_price,
                    self._current_timestamp,
                    "Stop Loss Gap"
                )

            if (
                take_profit is not None
                and ask_open <= take_profit
            ):
                return self.close_position(
                    open_price,
                    self._current_timestamp,
                    "Take Profit Gap"
                )

        return None

    # ========================================================
    # CHECK STOP LOSS / TAKE PROFIT
    # ========================================================

    def check_exit(
        self,
        high,
        low,
        timestamp=None
    ):
        if self.position is None:
            return None

        position = self.position

        side = position["side"]

        stop_loss = position["stop_loss"]
        take_profit = position["take_profit"]

        high = float(high)
        low = float(low)

        # Convert current candle's mid OHLC to Bid/Ask ranges.
        bid_high = self._bid(high)
        bid_low = self._bid(low)

        ask_high = self._ask(high)
        ask_low = self._ask(low)

        # ----------------------------------------------------
        # LONG
        # Long positions exit through BID.
        # Conservative rule:
        # if SL and TP are both touched in the same candle,
        # assume SL happened first.
        # ----------------------------------------------------

        if side == "LONG":

            if (
                stop_loss is not None
                and bid_low <= stop_loss
            ):
                return self.close_position(
                    stop_loss,
                    timestamp,
                    "Stop Loss"
                )

            if (
                take_profit is not None
                and bid_high >= take_profit
            ):
                return self.close_position(
                    take_profit,
                    timestamp,
                    "Take Profit"
                )

        # ----------------------------------------------------
        # SHORT
        # Short positions exit through ASK.
        # ----------------------------------------------------

        elif side == "SHORT":

            if (
                stop_loss is not None
                and ask_high >= stop_loss
            ):
                return self.close_position(
                    stop_loss,
                    timestamp,
                    "Stop Loss"
                )

            if (
                take_profit is not None
                and ask_low <= take_profit
            ):
                return self.close_position(
                    take_profit,
                    timestamp,
                    "Take Profit"
                )

        return None

    # ========================================================
    # UPDATE POSITION EXTREMES
    # ========================================================

    def update_position_extremes(
        self,
        high,
        low
    ):
        if self.position is None:
            return

        self.position["highest_price"] = max(
            self.position["highest_price"],
            float(high)
        )

        self.position["lowest_price"] = min(
            self.position["lowest_price"],
            float(low)
        )

    # ========================================================
    # TRAILING STOP
    # ========================================================

    def update_trailing_stop(
        self,
        trailing_distance=None,
        trailing_mode="price"
    ):
        if self.position is None:
            return

        if trailing_distance is None:
            return

        trailing_distance = float(
            trailing_distance
        )

        if trailing_distance <= 0:
            return

        position = self.position
        side = position["side"]

        if side == "LONG":

            new_stop = (
                position["highest_price"]
                - trailing_distance
            )

            if position["stop_loss"] is None:
                position["stop_loss"] = new_stop
            else:
                position["stop_loss"] = max(
                    position["stop_loss"],
                    new_stop
                )

            position["trailing_active"] = True

        elif side == "SHORT":

            new_stop = (
                position["lowest_price"]
                + trailing_distance
            )

            if position["stop_loss"] is None:
                position["stop_loss"] = new_stop
            else:
                position["stop_loss"] = min(
                    position["stop_loss"],
                    new_stop
                )

            position["trailing_active"] = True

    # ========================================================
    # SIGNAL HELPERS
    # ========================================================

    @staticmethod
    def _get_strategy_signal(
        strategy,
        df,
        i
    ):
        if hasattr(
            strategy,
            "generate_signal"
        ):
            return strategy.generate_signal(
                df,
                i
            )

        if isinstance(strategy, type):
            strategy_instance = strategy()
            return strategy_instance.generate_signal(
                df,
                i
            )

        try:
            return strategy(
                df,
                i
            )
        except TypeError:
            return strategy(
                df.iloc[i],
                i
            )

    # ========================================================
    # EQUITY
    # ========================================================

    def _calculate_equity(
        self,
        close
    ):
        equity = float(self.balance)

        if self.position is None:
            return equity

        position = self.position

        if position["side"] == "LONG":

            # Mark LONG at Bid.
            mark_price = self._bid(close)

            unrealized = (
                mark_price
                - position["entry"]
            ) * position["size"]

        else:

            # Mark SHORT at Ask.
            mark_price = self._ask(close)

            unrealized = (
                position["entry"]
                - mark_price
            ) * position["size"]

        return float(
            equity + unrealized
        )

    # ========================================================
    # RUN BACKTEST
    # ========================================================

    def run(
        self,
        data,
        strategy,
        trailing_distance=None
    ):
        if data is None:
            raise ValueError(
                "No market data supplied."
            )

        if len(data) == 0:
            raise ValueError(
                "Market data is empty."
            )

        df = data.copy()

        required_columns = [
            "datetime",
            "open",
            "high",
            "low",
            "close"
        ]

        missing = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        df = (
            df.sort_values("datetime")
            .reset_index(drop=True)
        )

        self.balance = self.initial_balance
        self.position = None
        self.pending_order = None
        self.pending_close = None
        self._current_timestamp = None
        self.trades = []
        self.equity_curve = []

        # ====================================================
        # MAIN MARKET LOOP
        # ====================================================

        for i in range(len(df)):

            row = df.iloc[i]

            timestamp = row["datetime"]
            self._current_timestamp = timestamp

            open_price = float(row["open"])
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])

            # ------------------------------------------------
            # 1. Execute pending orders at NEXT candle OPEN.
            # ------------------------------------------------

            if self.pending_close is not None:
                if self.position is not None:
                    self.close_position(
                        self._bid(open_price)
                        if self.position["side"] == "LONG"
                        else self._ask(open_price),
                        timestamp,
                        self.pending_close
                    )

                self.pending_close = None

            if self.pending_order is not None:
                order = self.pending_order

                if self.position is None:
                    self.open_position(
                        side=order["side"],
                        entry=open_price,
                        stop_loss=order["stop_loss"],
                        take_profit=order["take_profit"],
                        timestamp=timestamp,
                        entry_reference=order.get(
                            "signal_entry"
                        )
                    )

                self.pending_order = None

            # ------------------------------------------------
            # 2. Existing position uses current candle.
            #
            # First resolve a gap at the candle OPEN. If the
            # market opens beyond SL/TP, the executable open
            # is used instead of the requested level.
            # ------------------------------------------------

            if self.position is not None:
                self._resolve_open_gap_exit(
                    open_price
                )

            if self.position is not None:
                self.update_position_extremes(
                    high,
                    low
                )

                self.check_exit(
                    high,
                    low,
                    timestamp
                )

            # ------------------------------------------------
            # 3. Trailing is updated AFTER the candle's
            #    existing SL/TP check. The new level becomes
            #    active on the NEXT candle.
            # ------------------------------------------------

            if self.position is not None:
                self.update_trailing_stop(
                    trailing_distance
                )

            # ------------------------------------------------
            # 4. Generate strategy signal at candle close.
            #    Any NEW market entry is scheduled for the
            #    next candle open.
            # ------------------------------------------------

            signal = self._get_strategy_signal(
                strategy,
                df,
                i
            )

            if signal is None:
                signal = {}

            if not isinstance(signal, dict):
                signal = {}

            if self.position is None:

                side = signal.get("side")

                if side in {
                    "LONG",
                    "SHORT"
                } and i < len(df) - 1:

                    self.pending_order = {
                        "side": side,
                        "signal_entry": signal.get(
                            "entry"
                        ),
                        "stop_loss": signal.get(
                            "stop_loss"
                        ),
                        "take_profit": signal.get(
                            "take_profit"
                        ),
                    }

            elif signal.get(
                "close_position"
            ):

                # Strategy exit is also executed on the
                # next candle open, not at the signal candle
                # close.
                if i < len(df) - 1:
                    self.pending_close = (
                        "Strategy Exit"
                    )

            # ------------------------------------------------
            # 5. Equity is marked at current candle close.
            # ------------------------------------------------

            equity = self._calculate_equity(
                close
            )

            self.equity_curve.append({
                "datetime": timestamp,
                "equity": equity
            })

        # ====================================================
        # CLOSE OPEN POSITION AT END OF DATA
        # ====================================================

        if self.position is not None:

            last_row = df.iloc[-1]

            last_close = float(
                last_row["close"]
            )

            exit_price = (
                self._bid(last_close)
                if self.position["side"] == "LONG"
                else self._ask(last_close)
            )

            self.close_position(
                exit_price,
                last_row["datetime"],
                "End of Data"
            )

        return self.get_results()

    # ========================================================
    # RESULTS
    # ========================================================

    def get_results(self):

        trades_df = pd.DataFrame(
            self.trades
        )

        equity_df = pd.DataFrame(
            self.equity_curve
        )

        if trades_df.empty:

            return {
                "initial_balance": (
                    self.initial_balance
                ),
                "final_balance": self.balance,
                "net_profit": (
                    self.balance
                    - self.initial_balance
                ),
                "return_percent": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "profit_factor": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "expectancy": 0.0,
                "average_r": 0.0,
                "best_trade": 0.0,
                "worst_trade": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_money": 0.0,
                "recovery_factor": 0.0,
                "long_trades": 0,
                "short_trades": 0,
                "long_win_rate": 0.0,
                "short_win_rate": 0.0,
                "trades": trades_df,
                "equity_curve": equity_df,
            }

        winning = trades_df[
            trades_df["net_pnl"] > 0
        ]

        losing = trades_df[
            trades_df["net_pnl"] < 0
        ]

        total_trades = len(
            trades_df
        )

        winning_trades = len(
            winning
        )

        losing_trades = len(
            losing
        )

        win_rate = (
            winning_trades
            / total_trades
        ) * 100.0

        gross_profit = float(
            winning["net_pnl"].sum()
        )

        gross_loss = float(
            abs(losing["net_pnl"].sum())
        )

        if gross_loss > 0:
            profit_factor = (
                gross_profit
                / gross_loss
            )
        else:
            profit_factor = np.inf

        average_win = (
            float(
                winning["net_pnl"].mean()
            )
            if not winning.empty
            else 0.0
        )

        average_loss = (
            float(
                losing["net_pnl"].mean()
            )
            if not losing.empty
            else 0.0
        )

        expectancy = float(
            trades_df["net_pnl"].mean()
        )

        valid_r = trades_df[
            trades_df["r_multiple"].notna()
        ]

        average_r = (
            float(
                valid_r["r_multiple"].mean()
            )
            if not valid_r.empty
            else 0.0
        )

        best_trade = float(
            trades_df["net_pnl"].max()
        )

        worst_trade = float(
            trades_df["net_pnl"].min()
        )

        max_drawdown = (
            self.calculate_max_drawdown(
                equity_df
            )
        )

        max_drawdown_money = (
            self.calculate_max_drawdown_money(
                equity_df
            )
        )

        net_profit = (
            self.balance
            - self.initial_balance
        )

        return_percent = (
            net_profit
            / self.initial_balance
        ) * 100.0

        if max_drawdown_money > 0:
            recovery_factor = (
                net_profit
                / max_drawdown_money
            )
        else:
            recovery_factor = (
                np.inf
                if net_profit > 0
                else 0.0
            )

        long_trades = trades_df[
            trades_df["side"] == "LONG"
        ]

        short_trades = trades_df[
            trades_df["side"] == "SHORT"
        ]

        long_win_rate = self._win_rate(
            long_trades
        )

        short_win_rate = self._win_rate(
            short_trades
        )

        return {
            "initial_balance": (
                self.initial_balance
            ),
            "final_balance": self.balance,
            "net_profit": net_profit,
            "return_percent": return_percent,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "average_win": average_win,
            "average_loss": average_loss,
            "expectancy": expectancy,
            "average_r": average_r,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "max_drawdown": max_drawdown,
            "max_drawdown_money": max_drawdown_money,
            "recovery_factor": recovery_factor,
            "long_trades": len(
                long_trades
            ),
            "short_trades": len(
                short_trades
            ),
            "long_win_rate": long_win_rate,
            "short_win_rate": short_win_rate,
            "trades": trades_df,
            "equity_curve": equity_df,
        }

    # ========================================================
    # STATISTICS HELPERS
    # ========================================================

    @staticmethod
    def _win_rate(
        trades_df
    ):
        if trades_df is None:
            return 0.0

        if trades_df.empty:
            return 0.0

        return float(
            (
                trades_df["net_pnl"] > 0
            ).mean()
            * 100.0
        )

    @staticmethod
    def calculate_max_drawdown(
        equity_df
    ):
        if equity_df is None:
            return 0.0

        if equity_df.empty:
            return 0.0

        equity = (
            equity_df["equity"]
            .astype(float)
        )

        peak = equity.cummax()

        drawdown = (
            (equity - peak)
            / peak.replace(0, np.nan)
        ) * 100.0

        return float(
            abs(
                drawdown.min()
            )
        )

    @staticmethod
    def calculate_max_drawdown_money(
        equity_df
    ):
        if equity_df is None:
            return 0.0

        if equity_df.empty:
            return 0.0

        equity = (
            equity_df["equity"]
            .astype(float)
        )

        peak = equity.cummax()

        drawdown_money = (
            peak - equity
        )

        return float(
            drawdown_money.max()
        )


# ============================================================
# SIMPLE STRATEGY EXAMPLE
# ============================================================

def example_strategy(
    data,
    i
):
    if i < 2:
        return {}

    row = data.iloc[i]
    previous = data.iloc[i - 1]

    # Simple bullish candle example.
    # The signal is generated at candle close.
    # V2 executes a new market order at the NEXT candle open.

    if (
        row["close"] > row["open"]
        and previous["close"]
        <= previous["open"]
    ):

        entry = float(
            row["close"]
        )

        stop_loss = float(
            row["low"]
        )

        risk = (
            entry - stop_loss
        )

        if risk > 0:

            take_profit = (
                entry
                + risk * 2
            )

            return {
                "side": "LONG",
                "entry": entry,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
            }

    return {}
