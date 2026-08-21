import pandas as pd

# =========================================================

# FOREX BACKTESTER

# DATA ENGINE V2

# =========================================================

REQUIRED_COLUMNS = [

    "datetime",

    "open",

    "high",

    "low",

    "close"

]

# =========================================================

# NORMALIZE COLUMNS

# =========================================================

def normalize_columns(df):

    """

    Convert common CSV column names into standard names.

    """

    column_map = {}

    replacements = {

        "date": "datetime",

        "time": "datetime",

        "timestamp": "datetime",

        "datetime": "datetime",

        "open": "open",

        "o": "open",

        "high": "high",

        "h": "high",

        "low": "low",

        "l": "low",

        "close": "close",

        "c": "close",

        "volume": "volume",

        "vol": "volume",

        "tick_volume": "volume"

    }

    for column in df.columns:

        clean = str(column).strip().lower()

        if clean in replacements:

            column_map[column] = replacements[clean]

    df = df.rename(columns=column_map)

    return df

# =========================================================

# LOAD CSV

# =========================================================

def load_csv(file):

    """

    Load market data from a CSV file.

    """

    try:

        df = pd.read_csv(file)

        df = normalize_columns(df)

        return df, None

    except Exception as e:

        return None, f"CSV error: {str(e)}"

# =========================================================

# PREPARE DATA

# =========================================================

def prepare_data(df):

    """

    Clean and prepare market data.

    """

    if df is None:

        return None, {

            "status": "error",

            "message": "No data supplied."

        }

    df = df.copy()

    # =====================================================

    # CHECK REQUIRED COLUMNS

    # =====================================================

    missing_columns = [

        column

        for column in REQUIRED_COLUMNS

        if column not in df.columns

    ]

    if missing_columns:

        return None, {

            "status": "error",

            "message": "Missing columns",

            "missing_columns": missing_columns

        }

    # =====================================================

    # CONVERT DATETIME

    # =====================================================

    df["datetime"] = pd.to_datetime(

        df["datetime"],

        errors="coerce"

    )

    # =====================================================

    # CONVERT PRICE COLUMNS

    # =====================================================

    price_columns = [

        "open",

        "high",

        "low",

        "close"

    ]

    for column in price_columns:

        df[column] = pd.to_numeric(

            df[column],

            errors="coerce"

        )

    # =====================================================

    # OPTIONAL VOLUME

    # =====================================================

    if "volume" in df.columns:

        df["volume"] = pd.to_numeric(

            df["volume"],

            errors="coerce"

        )

    # =====================================================

    # COUNT INVALID RAW VALUES

    # =====================================================

    invalid_datetime = df["datetime"].isna()

    invalid_price_values = (

        df[price_columns]

        .isna()

        .any(axis=1)

    )

    invalid_numeric_rows = (

        invalid_datetime

        | invalid_price_values

    )

    invalid_numeric_count = int(

        invalid_numeric_rows.sum()

    )

    # Remove rows that cannot be used

    df = df.loc[

        ~invalid_numeric_rows

    ].copy()

    # =====================================================

    # SORT CHRONOLOGICALLY

    # =====================================================

    df = df.sort_values(

        "datetime"

    )

    # =====================================================

    # REMOVE DUPLICATE CANDLES

    # =====================================================

    duplicate_count = int(

        df.duplicated(

            subset=["datetime"]

        ).sum()

    )

    df = df.drop_duplicates(

        subset=["datetime"],

        keep="first"

    )

    # =====================================================

    # RESET INDEX

    # =====================================================

    df = df.reset_index(

        drop=True

    )

    # =====================================================

    # OHLC VALIDATION

    # =====================================================

    invalid_ohlc = (

        (df["high"] < df["open"])

        |

        (df["high"] < df["close"])

        |

        (df["high"] < df["low"])

        |

        (df["low"] > df["open"])

        |

        (df["low"] > df["close"])

        |

        (df["low"] > df["high"])

    )

    invalid_ohlc_count = int(

        invalid_ohlc.sum()

    )

    # =====================================================

    # REMOVE INVALID OHLC

    # =====================================================

    if invalid_ohlc_count > 0:

        df = df.loc[

            ~invalid_ohlc

        ].reset_index(

            drop=True

        )

    # =====================================================

    # DATA INFORMATION

    # =====================================================

    if len(df) > 0:

        first_candle = df["datetime"].min()

        last_candle = df["datetime"].max()

    else:

        first_candle = None

        last_candle = None

    candle_count = len(df)

    # =====================================================

    # ESTIMATE MISSING INTERVALS

    # =====================================================

    missing_bars = 0

    if candle_count > 1:

        differences = (

            df["datetime"]

            .diff()

            .dropna()

        )

        median_interval = differences.median()

        if pd.notna(median_interval) and median_interval > pd.Timedelta(0):

            estimated_missing = (

                differences

                .div(median_interval)

                .round()

                .sub(1)

                .clip(lower=0)

            )

            missing_bars = int(

                estimated_missing.sum()

            )

    # =====================================================

    # INFORMATION

    # =====================================================

    information = {

        "status": "success",

        "candles": candle_count,

        "first_candle": (

            str(first_candle)

            if pd.notna(first_candle)

            else "—"

        ),

        "last_candle": (

            str(last_candle)

            if pd.notna(last_candle)

            else "—"

        ),

        "duplicates_removed":

            duplicate_count,

        # Main key expected by app.py

        "invalid_ohlc":

            invalid_ohlc_count,

        # Keep old key for compatibility

        "invalid_ohlc_removed":

            invalid_ohlc_count,

        "invalid_numeric_rows":

            invalid_numeric_count,

        "missing_bars":

            missing_bars

    }

    return df, information

# =========================================================

# FINAL DATA VALIDATION

# =========================================================

def validate_data(df):

    """

    Final validation before sending data

    to the backtest engine.

    """

    if df is None:

        return False, "No data loaded."

    if len(df) == 0:

        return False, "Dataset is empty."

    # =====================================================

    # REQUIRED COLUMNS

    # =====================================================

    for column in REQUIRED_COLUMNS:

        if column not in df.columns:

            return False, (

                f"Missing column: {column}"

            )

    # =====================================================

    # DATETIME VALIDATION

    # =====================================================

    if df["datetime"].isna().any():

        return False, (

            "Invalid datetime values detected."

        )

    if not df["datetime"].is_monotonic_increasing:

        return False, (

            "Datetime is not sorted."

        )

    # =====================================================

    # PRICE VALIDATION

    # =====================================================

    price_columns = [

        "open",

        "high",

        "low",

        "close"

    ]

    for column in price_columns:

        if df[column].isna().any():

            return False, (

                f"Invalid values in {column}."

            )

        if not pd.api.types.is_numeric_dtype(

            df[column]

        ):

            return False, (

                f"{column} must be numeric."

            )

    # =====================================================

    # OHLC LOGIC VALIDATION

    # =====================================================

    invalid_ohlc = (

        (df["high"] < df["open"])

        |

        (df["high"] < df["close"])

        |

        (df["high"] < df["low"])

        |

        (df["low"] > df["open"])

        |

        (df["low"] > df["close"])

        |

        (df["low"] > df["high"])

    )

    if invalid_ohlc.any():

        return False, (

            "Invalid OHLC candles detected."

        )

    return True, "Data is valid."
