"""
Trading Market AI

Regression Test Scenarios

Every function returns an OptionChain.

Used by:

- Options Brain
- Trade Manager
- Reasoning Brain
- Learning Engine
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.brains.options.option_chain import (
    OptionChain,
    OptionData
)


# ============================================================
# Helper
# ============================================================

def build_chain(
    symbol,
    expiry,
    spot,
    strikes
):

    options = []

    for row in strikes:

        options.append(

            OptionData(

                strike=row["strike"],

                call_ltp=row["call_ltp"],
                put_ltp=row["put_ltp"],

                call_oi=row["call_oi"],
                put_oi=row["put_oi"],

                call_change_oi=row["call_change_oi"],
                put_change_oi=row["put_change_oi"],

                call_iv=row["call_iv"],
                put_iv=row["put_iv"],

                call_volume=row["call_volume"],
                put_volume=row["put_volume"]

            )

        )

    return OptionChain(

        symbol=symbol,

        expiry=expiry,

        spot_price=spot,

        options=options

    )

def bullish_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":210,
            "put_ltp":20,

            "call_oi":250000,
            "put_oi":850000,

            "call_change_oi":12000,
            "put_change_oi":52000,

            "call_iv":13.5,
            "put_iv":14.2,

            "call_volume":180000,
            "put_volume":420000,
        },

        {
            "strike":25100,

            "call_ltp":170,
            "put_ltp":30,

            "call_oi":260000,
            "put_oi":900000,

            "call_change_oi":10000,
            "put_change_oi":60000,

            "call_iv":13.8,
            "put_iv":14.5,

            "call_volume":170000,
            "put_volume":450000,
        },

        {
            "strike":25200,

            "call_ltp":120,
            "put_ltp":60,

            "call_oi":280000,
            "put_oi":980000,

            "call_change_oi":15000,
            "put_change_oi":70000,

            "call_iv":14.0,
            "put_iv":15.0,

            "call_volume":200000,
            "put_volume":520000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25180,

        strikes=strikes

    )

def bearish_chain():

    strikes = [

        {

            "strike":25000,

            "call_ltp":40,
            "put_ltp":210,

            "call_oi":950000,
            "put_oi":250000,

            "call_change_oi":70000,
            "put_change_oi":9000,

            "call_iv":15.2,
            "put_iv":13.5,

            "call_volume":520000,
            "put_volume":180000,

        },

        {

            "strike":25100,

            "call_ltp":60,
            "put_ltp":180,

            "call_oi":980000,
            "put_oi":260000,

            "call_change_oi":60000,
            "put_change_oi":8000,

            "call_iv":15.0,
            "put_iv":13.8,

            "call_volume":500000,
            "put_volume":160000,

        },

        {

            "strike":25200,

            "call_ltp":85,
            "put_ltp":140,

            "call_oi":1050000,
            "put_oi":280000,

            "call_change_oi":72000,
            "put_change_oi":11000,

            "call_iv":15.5,
            "put_iv":14.0,

            "call_volume":610000,
            "put_volume":210000,

        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25120,

        strikes=strikes

    )

def sideways_chain():

    strikes = [

        {

            "strike":25000,

            "call_ltp":120,
            "put_ltp":118,

            "call_oi":620000,
            "put_oi":610000,

            "call_change_oi":8000,
            "put_change_oi":7500,

            "call_iv":15.0,
            "put_iv":15.2,

            "call_volume":260000,
            "put_volume":255000,

        },

        {

            "strike":25100,

            "call_ltp":95,
            "put_ltp":92,

            "call_oi":640000,
            "put_oi":650000,

            "call_change_oi":7000,
            "put_change_oi":7600,

            "call_iv":15.1,
            "put_iv":15.1,

            "call_volume":240000,
            "put_volume":245000,

        },

        {

            "strike":25200,

            "call_ltp":75,
            "put_ltp":72,

            "call_oi":660000,
            "put_oi":655000,

            "call_change_oi":8500,
            "put_change_oi":8200,

            "call_iv":15.0,
            "put_iv":15.0,

            "call_volume":250000,
            "put_volume":248000,

        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25150,

        strikes=strikes

    )

def high_iv_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":180,
            "put_ltp":160,

            "call_oi":620000,
            "put_oi":640000,

            "call_change_oi":9000,
            "put_change_oi":9500,

            "call_iv":32.5,
            "put_iv":34.0,

            "call_volume":240000,
            "put_volume":245000,
        },

        {
            "strike":25100,

            "call_ltp":145,
            "put_ltp":145,

            "call_oi":640000,
            "put_oi":650000,

            "call_change_oi":9200,
            "put_change_oi":9800,

            "call_iv":33.2,
            "put_iv":34.5,

            "call_volume":250000,
            "put_volume":252000,
        },

        {
            "strike":25200,

            "call_ltp":120,
            "put_ltp":122,

            "call_oi":660000,
            "put_oi":670000,

            "call_change_oi":10000,
            "put_change_oi":10500,

            "call_iv":34.0,
            "put_iv":35.5,

            "call_volume":260000,
            "put_volume":265000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25180,

        strikes=strikes

    )
def low_iv_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":110,
            "put_ltp":108,

            "call_oi":620000,
            "put_oi":625000,

            "call_change_oi":7000,
            "put_change_oi":7100,

            "call_iv":9.5,
            "put_iv":10.2,

            "call_volume":210000,
            "put_volume":208000,
        },

        {
            "strike":25100,

            "call_ltp":90,
            "put_ltp":92,

            "call_oi":635000,
            "put_oi":640000,

            "call_change_oi":6900,
            "put_change_oi":7000,

            "call_iv":10.0,
            "put_iv":10.5,

            "call_volume":205000,
            "put_volume":206000,
        },

        {
            "strike":25200,

            "call_ltp":70,
            "put_ltp":72,

            "call_oi":645000,
            "put_oi":650000,

            "call_change_oi":6800,
            "put_change_oi":6900,

            "call_iv":10.5,
            "put_iv":11.0,

            "call_volume":198000,
            "put_volume":200000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25150,

        strikes=strikes

    )

def heavy_call_writing_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":95,
            "put_ltp":105,

            "call_oi":1200000,
            "put_oi":320000,

            "call_change_oi":95000,
            "put_change_oi":8000,

            "call_iv":15.0,
            "put_iv":15.2,

            "call_volume":420000,
            "put_volume":160000,
        },

        {
            "strike":25100,

            "call_ltp":82,
            "put_ltp":118,

            "call_oi":1350000,
            "put_oi":340000,

            "call_change_oi":110000,
            "put_change_oi":7000,

            "call_iv":15.1,
            "put_iv":15.0,

            "call_volume":460000,
            "put_volume":170000,
        },

        {
            "strike":25200,

            "call_ltp":70,
            "put_ltp":132,

            "call_oi":1500000,
            "put_oi":360000,

            "call_change_oi":125000,
            "put_change_oi":6000,

            "call_iv":15.2,
            "put_iv":15.1,

            "call_volume":500000,
            "put_volume":180000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25140,

        strikes=strikes

    )

def heavy_put_writing_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":145,
            "put_ltp":55,

            "call_oi":320000,
            "put_oi":1200000,

            "call_change_oi":9000,
            "put_change_oi":95000,

            "call_iv":15.0,
            "put_iv":15.1,

            "call_volume":170000,
            "put_volume":430000,
        },

        {
            "strike":25100,

            "call_ltp":132,
            "put_ltp":42,

            "call_oi":340000,
            "put_oi":1350000,

            "call_change_oi":8000,
            "put_change_oi":110000,

            "call_iv":15.2,
            "put_iv":15.3,

            "call_volume":180000,
            "put_volume":470000,
        },

        {
            "strike":25200,

            "call_ltp":118,
            "put_ltp":30,

            "call_oi":360000,
            "put_oi":1500000,

            "call_change_oi":7000,
            "put_change_oi":125000,

            "call_iv":15.1,
            "put_iv":15.2,

            "call_volume":190000,
            "put_volume":520000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25180,

        strikes=strikes

    )
def premium_bullish_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":220,
            "put_ltp":45,

            "call_oi":620000,
            "put_oi":625000,

            "call_change_oi":9000,
            "put_change_oi":8500,

            "call_iv":15.2,
            "put_iv":15.1,

            "call_volume":850000,
            "put_volume":180000,
        },

        {
            "strike":25100,

            "call_ltp":180,
            "put_ltp":60,

            "call_oi":630000,
            "put_oi":635000,

            "call_change_oi":9200,
            "put_change_oi":9000,

            "call_iv":15.3,
            "put_iv":15.2,

            "call_volume":900000,
            "put_volume":190000,
        },

        {
            "strike":25200,

            "call_ltp":145,
            "put_ltp":82,

            "call_oi":640000,
            "put_oi":645000,

            "call_change_oi":9400,
            "put_change_oi":9100,

            "call_iv":15.4,
            "put_iv":15.3,

            "call_volume":980000,
            "put_volume":210000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25180,

        strikes=strikes

    )

def premium_bearish_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":55,
            "put_ltp":215,

            "call_oi":620000,
            "put_oi":625000,

            "call_change_oi":9000,
            "put_change_oi":8500,

            "call_iv":15.2,
            "put_iv":15.1,

            "call_volume":180000,
            "put_volume":850000,
        },

        {
            "strike":25100,

            "call_ltp":70,
            "put_ltp":185,

            "call_oi":630000,
            "put_oi":635000,

            "call_change_oi":9200,
            "put_change_oi":9000,

            "call_iv":15.3,
            "put_iv":15.2,

            "call_volume":190000,
            "put_volume":900000,
        },

        {
            "strike":25200,

            "call_ltp":90,
            "put_ltp":150,

            "call_oi":640000,
            "put_oi":645000,

            "call_change_oi":9400,
            "put_change_oi":9100,

            "call_iv":15.4,
            "put_iv":15.3,

            "call_volume":210000,
            "put_volume":980000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25140,

        strikes=strikes

    )

def conflicting_chain():

    """
    Conflicting Market

    OI            -> Bullish
    PCR           -> Bearish
    Premium Flow  -> Bearish
    IV            -> Neutral
    Strike        -> Neutral

    Expected:
        WAIT
    """

    strikes = [

        {

            "strike":25000,

            "call_ltp":85,
            "put_ltp":130,

            # OI Bullish
            "call_oi":420000,
            "put_oi":920000,

            "call_change_oi":8000,
            "put_change_oi":62000,

            # Neutral IV
            "call_iv":15.2,
            "put_iv":15.3,

            # Premium Bearish
            "call_volume":210000,
            "put_volume":640000,

        },

        {

            "strike":25100,

            "call_ltp":70,
            "put_ltp":150,

            "call_oi":430000,
            "put_oi":950000,

            "call_change_oi":9000,
            "put_change_oi":64000,

            "call_iv":15.1,
            "put_iv":15.2,

            "call_volume":220000,
            "put_volume":700000,

        },

        {

            "strike":25200,

            "call_ltp":58,
            "put_ltp":170,

            "call_oi":450000,
            "put_oi":980000,

            "call_change_oi":10000,
            "put_change_oi":68000,

            "call_iv":15.0,
            "put_iv":15.0,

            "call_volume":240000,
            "put_volume":760000,

        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25160,

        strikes=strikes

    )

def empty_chain():

    return OptionChain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot_price=25150,

        options=[]

    )

def single_strike_chain():

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25150,

        strikes=[

            {

                "strike":25150,

                "call_ltp":95,
                "put_ltp":92,

                "call_oi":620000,
                "put_oi":630000,

                "call_change_oi":8000,
                "put_change_oi":8500,

                "call_iv":15.2,
                "put_iv":15.1,

                "call_volume":240000,
                "put_volume":245000,

            }

        ]

    )

def zero_oi_chain():

    strikes = [

        {
            "strike":25000,

            "call_ltp":140,
            "put_ltp":40,

            "call_oi":0,
            "put_oi":0,

            "call_change_oi":0,
            "put_change_oi":0,

            "call_iv":15.0,
            "put_iv":15.0,

            "call_volume":150000,
            "put_volume":145000,
        },

        {
            "strike":25100,

            "call_ltp":110,
            "put_ltp":70,

            "call_oi":0,
            "put_oi":0,

            "call_change_oi":0,
            "put_change_oi":0,

            "call_iv":15.1,
            "put_iv":15.2,

            "call_volume":160000,
            "put_volume":155000,
        },

        {
            "strike":25200,

            "call_ltp":80,
            "put_ltp":100,

            "call_oi":0,
            "put_oi":0,

            "call_change_oi":0,
            "put_change_oi":0,

            "call_iv":15.2,
            "put_iv":15.1,

            "call_volume":170000,
            "put_volume":165000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25150,

        strikes=strikes

    )

def zero_volume_chain():

    strikes=[

        {

            "strike":25100,

            "call_ltp":120,
            "put_ltp":118,

            "call_oi":650000,
            "put_oi":640000,

            "call_change_oi":8000,
            "put_change_oi":8200,

            "call_iv":15.1,
            "put_iv":15.0,

            "call_volume":0,
            "put_volume":0,

        }

    ]

    return build_chain(

        "NIFTY",

        "30-Jul-2026",

        25150,

        strikes

    )

def zero_iv_chain():

    strikes=[

        {

            "strike":25100,

            "call_ltp":100,
            "put_ltp":95,

            "call_oi":650000,
            "put_oi":640000,

            "call_change_oi":9000,
            "put_change_oi":9100,

            "call_iv":0,
            "put_iv":0,

            "call_volume":210000,
            "put_volume":205000,

        }

    ]

    return build_chain(

        "NIFTY",

        "30-Jul-2026",

        25150,

        strikes

    )

def duplicate_strike_chain():

    strikes = [

        {
            "strike":25100,

            "call_ltp":100,
            "put_ltp":95,

            "call_oi":650000,
            "put_oi":640000,

            "call_change_oi":9000,
            "put_change_oi":8500,

            "call_iv":15.0,
            "put_iv":15.1,

            "call_volume":220000,
            "put_volume":215000,
        },

        {
            "strike":25100,

            "call_ltp":102,
            "put_ltp":97,

            "call_oi":660000,
            "put_oi":650000,

            "call_change_oi":9100,
            "put_change_oi":8600,

            "call_iv":15.2,
            "put_iv":15.3,

            "call_volume":225000,
            "put_volume":220000,
        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25150,

        strikes=strikes

    )

def negative_values_chain():

    """
    Invalid Market Data

    Used to verify OptionChain validation.
    """

    strikes = [

        {

            "strike":25100,

            "call_ltp":100,
            "put_ltp":95,

            # Invalid values
            "call_oi":-500,
            "put_oi":-100,

            "call_change_oi":-50,
            "put_change_oi":-20,

            "call_iv":-15.0,
            "put_iv":-14.5,

            "call_volume":-1000,
            "put_volume":-900,

        }

    ]

    return build_chain(

        symbol="NIFTY",

        expiry="30-Jul-2026",

        spot=25150,

        strikes=strikes

    )