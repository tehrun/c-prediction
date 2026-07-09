from app.exchanges.types import Candle

def validate_candles(candles: list[Candle]) -> None:
    seen = set(); prev = None
    for c in candles:
        if prev and c.opened_at <= prev: raise ValueError("candles not in ascending timestamp order")
        if c.opened_at in seen: raise ValueError("duplicate candle timestamp")
        if min(c.open, c.high, c.low, c.close) <= 0: raise ValueError("OHLC must be positive")
        if c.high < max(c.open, c.close, c.low): raise ValueError("high below OHLC value")
        if c.low > min(c.open, c.close, c.high): raise ValueError("low above OHLC value")
        if c.volume < 0: raise ValueError("volume must be non-negative")
        seen.add(c.opened_at); prev = c.opened_at
