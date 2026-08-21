import pandas as pd

# =========================================================

# DATA ENGINE V1

# =========================================================

REQUIRED_COLUMNS = [

    "datetime",

    "open",

    "high",

    "low",

    "close"

]

def normalize_columns(df):

    """

    Convert common CSV column names into our standard names.

    """

    column_map = {}

    for column in df.columns:

        clean = str(column).strip().lower()

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

        if clean in replacements:

            column_map[column] = replacements[clean]

    df = df.rename(columns=column_map)

    return df

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

def prepare_data(df):

    """

    Clean and prepare market data.

    """

    df = df.copy()

    # Check required columns

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

    # Convert datetime

    df["datetime"] = pd.to_datetime(

        df["datetime"],

        errors="coerce"

    )

    # Convert price columns

    for column in [

        "open",

        "high",

        "low",

        "close"

    ]:

        df[column] = pd.to_numeric(

            df[column],

            errors="coerce"

        )

    # Volume is optional

    if "volume" in df.columns:

        df["volume"] = pd.to_numeric(

            df["volume"],

            errors="coerce"

        )

    # Remove invalid rows

    df = df.dropna(

        subset=[

            "datetime",

            "open",

            "high",

            "low",

            "close"

        ]

    )

    # Sort chronologically

    df = df.sort_values(

        "datetime"

    )

    # Remove duplicate candles

    duplicate_count = df.duplicated(

        subset=["datetime"]

    ).sum()

    df = df.drop_duplicates(

        subset=["datetime"],

        keep="first"

    )

    # Reset index

    df = df.reset_index(

        drop=True

    )

    # Basic OHLC validation

    invalid_ohlc = (

        (df["high"] < df["open"]) |

        (df["high"] < df["close"]) |

        (df["high"] < df["low"]) |

        (df["low"] > df["open"]) |

        (df["low"] > df["close"]) |

        (df["low"] > df["high"])

    )

    invalid_ohlc_count = int(

        invalid_ohlc.sum()

    )

    # Remove invalid OHLC candles

    if invalid_ohlc_count > 0:

        df = df.loc[

            ~invalid_ohlc

        ].reset_index(drop=True)

    # Calculate data information

    first_candle = df["datetime"].min()

    last_candle = df["datetime"].max()

    candle_count = len(df)

    # Estimate missing intervals

    missing_bars = 0

    if candle_count > 1:

        differences = (

            df["datetime"]

            .diff()

            .dropna()

        )

        median_interval = differences.median()

        if pd.notna(median_interval):

            missing_bars = int(

                (

                    differences

                    .div(median_interval)

                    .round()

                    .sub(1)

                    .clip(lower=0)

                ).sum()

            )

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

            int(duplicate_count),

        "invalid_ohlc_removed":

            invalid_ohlc_count,

        "missing_bars":

            missing_bars

    }

    return df, information

def validate_data(df):

    """

    Final validation before sending data

    to the backtest engine.

    """

    if df is None:

        return False, "No data loaded."

    if len(df) == 0:

        return False, "Dataset is empty."

    required = [

        "datetime",

        "open",

        "high",

        "low",

        "close"

    ]

    for column in required:

        if column not in df.columns:

            return False, (

                f"Missing column: {column}"

            )

    if not df["datetime"].is_monotonic_increasing:

        return False, (

            "Datetime is not sorted."

        )

    return True, "Data is valid."
