from app.exchanges.base import ExchangeAdapter
from app.exchanges.ccxt_adapter import BinanceExchangeAdapter, KrakenExchangeAdapter

def get_exchange_adapter(key: str) -> ExchangeAdapter:
    match key.lower():
        case "kraken": return KrakenExchangeAdapter()
        case "binance": return BinanceExchangeAdapter()
        case _: raise ValueError(f"Unsupported exchange: {key}")
