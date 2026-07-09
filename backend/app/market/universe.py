from app.exchanges.types import ExchangeMarket
STABLECOINS = {"USDT","USDC","DAI","FDUSD","TUSD","EURT","PYUSD"}
QUOTE_ALLOWLIST = {"USD","USDT","USDC","EUR"}
LEVERAGED_SUFFIXES = ("UP","DOWN","BULL","BEAR","2L","2S","3L","3S")

def is_leveraged_token(base: str) -> bool:
    return base.upper().endswith(LEVERAGED_SUFFIXES)

def filter_market_universe(markets: list[ExchangeMarket], max_markets: int = 20) -> list[ExchangeMarket]:
    eligible = [m for m in markets if m.active and m.spot and m.quote in QUOTE_ALLOWLIST and m.base not in STABLECOINS and not is_leveraged_token(m.base) and m.amount_precision is not None and m.price_precision is not None and (m.minimum_amount is not None or m.minimum_cost is not None)]
    return sorted(eligible, key=lambda m: (m.quote_volume is None, -(m.quote_volume or 0), m.symbol))[:max_markets]
