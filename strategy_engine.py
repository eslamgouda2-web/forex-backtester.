import pandas as pd

import numpy as np

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

        self.spread_pips = float(spread_pips)

        self.slippage_pips = float(slippage_pips)

        self.pip_size = float(pip_size)

        self.lot_size = float(lot_size)

        self.pip_value_per_lot = pip_value_per_lot

        self.risk_based_on = risk_based_on

        self.allow_long = allow_long

        self.allow_short = allow_short

        self.one_position_only = one_position_only

        self.position = None

        self.pending_order = None

        self.pending_close = None

        self.trades = []

        self.equity_curve = []

    # ========================================================

    # PRICE HELPERS

    # ========================================================

    def _spread_price(self):

        return (

            self.spread_pips

            * self.pip_size

        )

    def _slippage_price(self):

        return (

            self.slippage_pips

            * self.pip_size

        )

    def _bid(self, price):

        return (

            float(price)

            - self._spread_price() / 2

        )

    def _ask(self, price):

        return (

            float(price)

            + self._spread_price() / 2

        )

    # ========================================================

    # POSITION SIZE

    # ========================================================

    def calculate_position_size(

        self,

        entry,

        stop_loss

    ):

        if stop_loss is None:

            return 0.0

        entry = float(entry)

        stop_loss = float(stop_loss)

        distance = abs(

            entry - stop_loss

        )

        if distance <= 0:

            return 0.0

        risk_money = (

            self.balance

            * self.risk_percent

            / 100

        )

        size = (

            risk_money

            / distance

        )

        return float(size)

    # ========================================================

    # OPEN POSITION

    # ========================================================

    def open_position(

        self,

        side,

        entry,

        stop_loss,

        take_profit,

        timestamp

    ):

        if self.position is not None:

            return False

        if side == "LONG":

            if not self.allow_long:

                return False

            actual_entry = (

                self._ask(entry)

                + self._slippage_price()

            )

            if (

                stop_loss is None

                or stop_loss >= actual_entry

            ):

                return False

        elif side == "SHORT":

            if not self.allow_short:

                return False

            actual_entry = (

                self._bid(entry)

                - self._slippage_price()

            )

            if (

                stop_loss is None

                or stop_loss <= actual_entry

            ):

                return False

        else:

            return False

        size = self.calculate_position_size(

            actual_entry,

            stop_loss

        )

        if size <= 0:

            return False

        self.position = {

            "side": side,

            "entry": actual_entry,

            "stop_loss": float(stop_loss),

            "take_profit": (

                float(take_profit)

                if take_profit is not None

                else None

            ),

            "initial_stop_loss": float(stop_loss),

            "size": size,

            "entry_time": timestamp,

            "highest_price": actual_entry,

            "lowest_price": actual_entry

        }

        return True

    # ========================================================

    # CLOSE POSITION

    # ========================================================

    def close_position(

        self,

        market_price,

        timestamp,

        reason

    ):

        if self.position is None:

            return None

        position = self.position

        side = position["side"]

        entry = position["entry"]

        size = position["size"]

        if side == "LONG":

            exit_price = (

                self._bid(market_price)

                - self._slippage_price()

            )

            pnl = (

                exit_price - entry

            ) * size

        else:

            exit_price = (

                self._ask(market_price)

                + self._slippage_price()

            )

            pnl = (

                entry - exit_price

            ) * size

        lots = (

            size

            / self.lot_size

        )

        commission = (

            lots

            * self.commission_per_lot_side

            * 2

        )

        net_pnl = (

            pnl - commission

        )

        self.balance += net_pnl

        risk_distance = abs(

            entry

            - position["initial_stop_loss"]

        )

        if risk_distance > 0:

            if side == "LONG":

                r_multiple = (

                    exit_price - entry

                ) / risk_distance

            else:

                r_multiple = (

                    entry - exit_price

                ) / risk_distance

        else:

            r_multiple = 0.0

        trade = {

            "side": side,

            "entry_time": (

                position["entry_time"]

            ),

            "exit_time": timestamp,

            "entry": entry,

            "exit": exit_price,

            "stop_loss": (

                position["stop_loss"]

            ),

            "initial_stop_loss": (

                position["initial_stop_loss"]

            ),

            "take_profit": (

                position["take_profit"]

            ),

            "size_units": size,

            "lots": lots,

            "gross_pnl": pnl,

            "commission": commission,

            "net_pnl": net_pnl,

            "r_multiple": r_multiple,

            "reason": reason,

            "balance": self.balance

        }

        self.trades.append(trade)

        self.position = None

        return trade

    # ========================================================

    # CHECK EXIT

    # ========================================================

    def check_exit(

        self,

        high,

        low,

        timestamp

    ):

        if self.position is None:

            return

        position = self.position

        side = position["side"]

        stop = position["stop_loss"]

        target = position["take_profit"]

        high = float(high)

        low = float(low)

        # LONG

        if side == "LONG":

            if (

                stop is not None

                and self._bid(low) <= stop

            ):

                self.close_position(

                    stop,

                    timestamp,

                    "Stop Loss"

                )

                return

            if (

                target is not None

                and self._bid(high) >= target

            ):

                self.close_position(

                    target,

                    timestamp,

                    "Take Profit"

                )

                return

        # SHORT

        elif side == "SHORT":

            if (

                stop is not None

                and self._ask(high) >= stop

            ):

                self.close_position(

                    stop,

                    timestamp,

                    "Stop Loss"

                )

                return

            if (

                target is not None

                and self._ask(low) <= target

            ):

                self.close_position(

                    target,

                    timestamp,

                    "Take Profit"

                )

                return

    # ========================================================

    # EQUITY

    # ========================================================

    def calculate_equity(

        self,

        close

    ):

        equity = self.balance

        if self.position is None:

            return equity

        position = self.position

        if position["side"] == "LONG":

            current_price = self._bid(close)

            unrealized = (

                current_price

                - position["entry"]

            ) * position["size"]

        else:

            current_price = self._ask(close)

            unrealized = (

                position["entry"]

                - current_price

            ) * position["size"]

        return (

            equity + unrealized

        )

    # ========================================================

    # STRATEGY SIGNAL

    # ========================================================

    @staticmethod

    def get_signal(

        strategy,

        df,

        index

    ):

        try:

            signal = strategy.generate_signal(

                df,

                index

            )

            if isinstance(

                signal,

                dict

            ):

                return signal

        except Exception:

            return {}

        return {}

    # ========================================================

    # MAX DRAWDOWN

    # ========================================================

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

            / peak

        ) * 100

        return abs(

            float(

                drawdown.min()

            )

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

        required = [

            "datetime",

            "open",

            "high",

            "low",

            "close"

        ]

        missing = [

            col

            for col in required

            if col not in data.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

        # ====================================================

        # RESET

        # ====================================================

        self.balance = self.initial_balance

        self.position = None

        self.pending_order = None

        self.pending_close = None

        self.trades = []

        self.equity_curve = []

        # ====================================================

        # FAST DATA ARRAYS

        # ====================================================

        df = (

            data

            .sort_values("datetime")

            .reset_index(drop=True)

        )

        timestamps = (

            df["datetime"].to_numpy()

        )

        opens = (

            df["open"]

            .astype(float)

            .to_numpy()

        )

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

        closes = (

            df["close"]

            .astype(float)

            .to_numpy()

        )

        total_bars = len(df)

        # ====================================================

        # MAIN LOOP

        # ====================================================

        for i in range(total_bars):

            timestamp = timestamps[i]

            open_price = opens[i]

            high = highs[i]

            low = lows[i]

            close = closes[i]

            # ------------------------------------------------

            # EXECUTE PENDING ORDER

            # ------------------------------------------------

            if (

                self.pending_order is not None

                and self.position is None

            ):

                order = self.pending_order

                self.open_position(

                    side=order["side"],

                    entry=open_price,

                    stop_loss=order["stop_loss"],

                    take_profit=order["take_profit"],

                    timestamp=timestamp

                )

                self.pending_order = None

            # ------------------------------------------------

            # CHECK CURRENT POSITION

            # ------------------------------------------------

            if self.position is not None:

                self.position[

                    "highest_price"

                ] = max(

                    self.position[

                        "highest_price"

                    ],

                    high

                )

                self.position[

                    "lowest_price"

                ] = min(

                    self.position[

                        "lowest_price"

                    ],

                    low

                )

                self.check_exit(

                    high,

                    low,

                    timestamp

                )

            # ------------------------------------------------

            # STRATEGY SIGNAL

            # ------------------------------------------------

            signal = self.get_signal(

                strategy,

                df,

                i

            )

            # ------------------------------------------------

            # OPEN NEW POSITION NEXT BAR

            # ------------------------------------------------

            if (

                self.position is None

                and signal

                and i < total_bars - 1

            ):

                side = signal.get(

                    "side"

                )

                if side in [

                    "LONG",

                    "SHORT"

                ]:

                    stop_loss = signal.get(

                        "stop_loss"

                    )

                    take_profit = signal.get(

                        "take_profit"

                    )

                    if stop_loss is not None:

                        self.pending_order = {

                            "side": side,

                            "stop_loss": stop_loss,

                            "take_profit": take_profit

                        }

            # ------------------------------------------------

            # EQUITY

            # ------------------------------------------------

            equity = self.calculate_equity(

                close

            )

            self.equity_curve.append({

                "datetime": timestamp,

                "equity": equity

            })

        # ====================================================

        # CLOSE LAST POSITION

        # ====================================================

        if self.position is not None:

            self.close_position(

                closes[-1],

                timestamps[-1],

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

        total_trades = len(

            trades_df

        )

        if total_trades == 0:

            return {

                "initial_balance":

                    self.initial_balance,

                "final_balance":

                    self.balance,

                "net_profit":

                    self.balance

                    - self.initial_balance,

                "return_percent":

                    0.0,

                "total_trades":

                    0,

                "winning_trades":

                    0,

                "losing_trades":

                    0,

                "win_rate":

                    0.0,

                "gross_profit":

                    0.0,

                "gross_loss":

                    0.0,

                "profit_factor":

                    0.0,

                "average_win":

                    0.0,

                "average_loss":

                    0.0,

                "expectancy":

                    0.0,

                "average_r":

                    0.0,

                "best_trade":

                    0.0,

                "worst_trade":

                    0.0,

                "max_drawdown":

                    self.calculate_max_drawdown(

                        equity_df

                    ),

                "max_drawdown_money":

                    0.0,

                "recovery_factor":

                    0.0,

                "long_trades":

                    0,

                "short_trades":

                    0,

                "long_win_rate":

                    0.0,

                "short_win_rate":

                    0.0,

                "trades":

                    trades_df,

                "equity_curve":

                    equity_df

            }

        winning = trades_df[

            trades_df["net_pnl"] > 0

        ]

        losing = trades_df[

            trades_df["net_pnl"] < 0

        ]

        winning_trades = len(

            winning

        )

        losing_trades = len(

            losing

        )

        win_rate = (

            winning_trades

            / total_trades

        ) * 100

        gross_profit = float(

            winning["net_pnl"].sum()

        )

        gross_loss = abs(

            float(

                losing["net_pnl"].sum()

            )

        )

        if gross_loss > 0:

            profit_factor = (

                gross_profit

                / gross_loss

            )

        else:

            profit_factor = float("inf")

        net_profit = (

            self.balance

            - self.initial_balance

        )

        return {

            "initial_balance":

                self.initial_balance,

            "final_balance":

                self.balance,

            "net_profit":

                net_profit,

            "return_percent":

                (

                    net_profit

                    / self.initial_balance

                ) * 100,

            "total_trades":

                total_trades,

            "winning_trades":

                winning_trades,

            "losing_trades":

                losing_trades,

            "win_rate":

                win_rate,

            "gross_profit":

                gross_profit,

            "gross_loss":

                gross_loss,

            "profit_factor":

                profit_factor,

            "average_win":

                float(

                    winning["net_pnl"].mean()

                )

                if winning_trades > 0

                else 0.0,

            "average_loss":

                float(

                    losing["net_pnl"].mean()

                )

                if losing_trades > 0

                else 0.0,

            "expectancy":

                float(

                    trades_df["net_pnl"].mean()

                ),

            "average_r":

                float(

                    trades_df["r_multiple"].mean()

                ),

            "best_trade":

                float(

                    trades_df["net_pnl"].max()

                ),

            "worst_trade":

                float(

                    trades_df["net_pnl"].min()

                ),

            "max_drawdown":

                self.calculate_max_drawdown(

                    equity_df

                ),

            "max_drawdown_money":

                0.0,

            "recovery_factor":

                0.0,

            "long_trades":

                int(

                    (

                        trades_df["side"]

                        == "LONG"

                    ).sum()

                ),

            "short_trades":

                int(

                    (

                        trades_df["side"]

                        == "SHORT"

                    ).sum()

                ),

            "long_win_rate":

                0.0,

            "short_win_rate":

                0.0,

            "trades":

                trades_df,

            "equity_curve":

                equity_df

        }
