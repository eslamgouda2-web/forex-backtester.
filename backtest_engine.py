import pandas as pd

import numpy as np

# ============================================================

# FOREX BACKTESTER

# BACKTEST ENGINE V1

# ============================================================

class BacktestEngine:

    def __init__(

        self,

        initial_balance=10000.0,

        risk_percent=1.0,

        commission=0.0,

        slippage=0.0,

        allow_long=True,

        allow_short=True,

        one_position_only=True

    ):

        self.initial_balance = float(initial_balance)

        self.balance = float(initial_balance)

        self.risk_percent = float(risk_percent)

        self.commission = float(commission)

        self.slippage = float(slippage)

        self.allow_long = allow_long

        self.allow_short = allow_short

        self.one_position_only = one_position_only

        self.position = None

        self.trades = []

        self.equity_curve = []

    # ========================================================

    # POSITION SIZE

    # ========================================================

    def calculate_position_size(self, entry, stop_loss):

        risk_money = self.balance * (self.risk_percent / 100.0)

        stop_distance = abs(entry - stop_loss)

        if stop_distance <= 0:

            return 0.0

        size = risk_money / stop_distance

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

        timestamp=None

    ):

        if self.one_position_only and self.position is not None:

            return False

        if side == "LONG" and not self.allow_long:

            return False

        if side == "SHORT" and not self.allow_short:

            return False

        entry = float(entry)

        # Apply slippage

        if side == "LONG":

            actual_entry = entry + self.slippage

        else:

            actual_entry = entry - self.slippage

        size = self.calculate_position_size(

            actual_entry,

            stop_loss if stop_loss is not None else actual_entry

        )

        # If there is no stop loss, use a safe default size

        if size <= 0:

            size = 1.0

        self.position = {

            "side": side,

            "entry": actual_entry,

            "stop_loss": stop_loss,

            "take_profit": take_profit,

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

        exit_price = float(exit_price)

        if side == "LONG":

            actual_exit = exit_price - self.slippage

            pnl = (actual_exit - entry) * size

        else:

            actual_exit = exit_price + self.slippage

            pnl = (entry - actual_exit) * size

        commission_cost = (

            abs(entry * size) * self.commission

            + abs(actual_exit * size) * self.commission

        )

        net_pnl = pnl - commission_cost

        self.balance += net_pnl

        trade = {

            "side": side,

            "entry_time": position["entry_time"],

            "exit_time": timestamp,

            "entry": entry,

            "exit": actual_exit,

            "stop_loss": position["stop_loss"],

            "take_profit": position["take_profit"],

            "size": size,

            "gross_pnl": pnl,

            "commission": commission_cost,

            "net_pnl": net_pnl,

            "reason": reason,

            "balance": self.balance

        }

        self.trades.append(trade)

        self.position = None

        return trade

    # ========================================================

    # CHECK STOP LOSS / TAKE PROFIT

    # ========================================================

    def check_exit(self, high, low, timestamp=None):

        if self.position is None:

            return None

        position = self.position

        side = position["side"]

        stop_loss = position["stop_loss"]

        take_profit = position["take_profit"]

        # ---------------------------------------------

        # LONG

        # ---------------------------------------------

        if side == "LONG":

            # Conservative assumption:

            # If both SL and TP are touched in the same candle,

            # assume SL happened first.

            if stop_loss is not None and low <= stop_loss:

                return self.close_position(

                    stop_loss,

                    timestamp,

                    "Stop Loss"

                )

            if take_profit is not None and high >= take_profit:

                return self.close_position(

                    take_profit,

                    timestamp,

                    "Take Profit"

                )

        # ---------------------------------------------

        # SHORT

        # ---------------------------------------------

        elif side == "SHORT":

            if stop_loss is not None and high >= stop_loss:

                return self.close_position(

                    stop_loss,

                    timestamp,

                    "Stop Loss"

                )

            if take_profit is not None and low <= take_profit:

                return self.close_position(

                    take_profit,

                    timestamp,

                    "Take Profit"

                )

        return None

    # ========================================================

    # UPDATE POSITION EXTREMES

    # ========================================================

    def update_position_extremes(self, high, low):

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

            raise ValueError("No market data supplied.")

        if len(data) == 0:

            raise ValueError("Market data is empty.")

        df = data.copy()

        required_columns = [

            "datetime",

            "open",

            "high",

            "low",

            "close"

        ]

        missing = [

            col for col in required_columns

            if col not in df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing required columns: {missing}"

            )

        df = df.sort_values("datetime").reset_index(drop=True)

        self.balance = self.initial_balance

        self.position = None

        self.trades = []

        self.equity_curve = []

        # ====================================================

        # MAIN MARKET LOOP

        # ====================================================

        for i in range(len(df)):

            row = df.iloc[i]

            timestamp = row["datetime"]

            open_price = float(row["open"])

            high = float(row["high"])

            low = float(row["low"])

            close = float(row["close"])

            # -----------------------------------------------

            # Update current position

            # -----------------------------------------------

            self.update_position_extremes(

                high,

                low

            )

            # -----------------------------------------------

            # Check existing position exits

            # -----------------------------------------------

            self.check_exit(

                high,

                low,

                timestamp

            )

            # -----------------------------------------------

            # Trailing stop

            # -----------------------------------------------

            if self.position is not None:

                self.update_trailing_stop(

                    trailing_distance

                )

                self.check_exit(

                    high,

                    low,

                    timestamp

                )

            # -----------------------------------------------

            # Strategy signal

            # -----------------------------------------------
              try:

                   if hasattr(strategy, "generate_signal"):

                    signal = strategy.generate_signal(

                        df,

                        i

                        )

                   elif isinstance(strategy, type):

                     strategy_instance = strategy()

                     signal = strategy_instance.generate_signal(

                         df,

                         i

                         )

                    else:

                         signal = strategy(

                             df,

                             i

                             )
   
            except TypeError:

                 signal = strategy(

                      row,

                      i

                  )

             if signal is None:

                  signal = {}

            # -----------------------------------------------

            # New position

            # -----------------------------------------------

            if self.position is None:

                side = signal.get("side")

                if side in ["LONG", "SHORT"]:

                    entry = signal.get(

                        "entry",

                        close

                    )

                    stop_loss = signal.get(

                        "stop_loss"

                    )

                    take_profit = signal.get(

                        "take_profit"

                    )

                    self.open_position(

                        side=side,

                        entry=entry,

                        stop_loss=stop_loss,

                        take_profit=take_profit,

                        timestamp=timestamp

                    )

            # -----------------------------------------------

            # Manual close signal

            # -----------------------------------------------

            elif signal.get("close_position"):

                self.close_position(

                    close,

                    timestamp,

                    "Strategy Exit"

                )

            # -----------------------------------------------

            # Equity

            # -----------------------------------------------

            equity = self.balance

            if self.position is not None:

                position = self.position

                if position["side"] == "LONG":

                    unrealized = (

                        close - position["entry"]

                    ) * position["size"]

                else:

                    unrealized = (

                        position["entry"] - close

                    ) * position["size"]

                equity += unrealized

            self.equity_curve.append({

                "datetime": timestamp,

                "equity": equity

            })

        # ====================================================

        # CLOSE OPEN POSITION AT END

        # ====================================================

        if self.position is not None:

            last_row = df.iloc[-1]

            self.close_position(

                float(last_row["close"]),

                last_row["datetime"],

                "End of Data"

            )

        return self.get_results()

    # ========================================================

    # RESULTS

    # ========================================================

    def get_results(self):

        trades_df = pd.DataFrame(self.trades)

        equity_df = pd.DataFrame(

            self.equity_curve

        )

        if trades_df.empty:

            return {

                "initial_balance": self.initial_balance,

                "final_balance": self.balance,

                "net_profit": self.balance - self.initial_balance,

                "total_trades": 0,

                "winning_trades": 0,

                "losing_trades": 0,

                "win_rate": 0.0,

                "profit_factor": 0.0,

                "max_drawdown": 0.0,

                "trades": trades_df,

                "equity_curve": equity_df

            }

        winning = trades_df[

            trades_df["net_pnl"] > 0

        ]

        losing = trades_df[

            trades_df["net_pnl"] < 0

        ]

        total_trades = len(trades_df)

        winning_trades = len(winning)

        losing_trades = len(losing)

        win_rate = (

            winning_trades / total_trades

        ) * 100.0

        gross_profit = winning[

            "net_pnl"

        ].sum()

        gross_loss = abs(

            losing["net_pnl"].sum()

        )

        if gross_loss > 0:

            profit_factor = (

                gross_profit / gross_loss

            )

        else:

            profit_factor = np.inf

        max_drawdown = self.calculate_max_drawdown(

            equity_df

        )

        return {

            "initial_balance": self.initial_balance,

            "final_balance": self.balance,

            "net_profit": (

                self.balance

                - self.initial_balance

            ),

            "total_trades": total_trades,

            "winning_trades": winning_trades,

            "losing_trades": losing_trades,

            "win_rate": win_rate,

            "profit_factor": profit_factor,

            "max_drawdown": max_drawdown,

            "trades": trades_df,

            "equity_curve": equity_df

        }

    # ========================================================

    # MAX DRAWDOWN

    # ========================================================

    @staticmethod

    def calculate_max_drawdown(equity_df):

        if equity_df is None:

            return 0.0

        if equity_df.empty:

            return 0.0

        equity = equity_df[

            "equity"

        ].astype(float)

        peak = equity.cummax()

        drawdown = (

            (equity - peak)

            / peak

        ) * 100.0

        return float(

            abs(drawdown.min())

        )

# ============================================================

# SIMPLE STRATEGY EXAMPLE

# ============================================================

def example_strategy(data, i):

    if i < 2:

        return {}

    row = data.iloc[i]

    previous = data.iloc[i - 1]

    # Simple bullish candle example

    if (

        row["close"] > row["open"]

        and previous["close"] <= previous["open"]

    ):

        entry = row["close"]

        stop_loss = row["low"]

        risk = entry - stop_loss

        if risk > 0:

            take_profit = entry + (

                risk * 2

            )

            return {

                "side": "LONG",

                "entry": entry,

                "stop_loss": stop_loss,

                "take_profit": take_profit

            }

    return {}
