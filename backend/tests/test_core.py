from datetime import UTC, datetime, timedelta
from decimal import Decimal
import pytest
from app.core.config import Settings
from app.exchanges.factory import get_exchange_adapter
from app.exchanges.types import Candle, ExchangeMarket
from app.ingestion.validation import validate_candles
from app.market.universe import filter_market_universe, is_leveraged_token
from app.services.candles import expected_missing

def test_settings_defaults(): assert Settings().market_universe_max == 20
def test_factory(): assert get_exchange_adapter('kraken').key == 'kraken'
def test_stablecoin_and_leverage_filters():
    ms=[ExchangeMarket(symbol='USDT/USD',base='USDT',quote='USD',spot=True,amount_precision=8,price_precision=2,minimum_amount=Decimal('1')), ExchangeMarket(symbol='BTCUP/USD',base='BTCUP',quote='USD',spot=True,amount_precision=8,price_precision=2,minimum_amount=Decimal('1')), ExchangeMarket(symbol='BTC/USD',base='BTC',quote='USD',spot=True,amount_precision=8,price_precision=2,minimum_amount=Decimal('1'),quote_volume=Decimal('9'))]
    assert [m.symbol for m in filter_market_universe(ms)] == ['BTC/USD']; assert is_leveraged_token('ETH3L')
def test_candle_validation():
    now=datetime(2024,1,1,tzinfo=UTC); validate_candles([Candle(opened_at=now,open=Decimal('1'),high=Decimal('2'),low=Decimal('1'),close=Decimal('1.5'),volume=Decimal('0'))])
    with pytest.raises(ValueError): validate_candles([Candle(opened_at=now,open=Decimal('0'),high=Decimal('2'),low=Decimal('1'),close=Decimal('1'),volume=Decimal('0'))])
def test_missing_detection():
    s=datetime(2024,1,1,tzinfo=UTC); assert expected_missing([s,s+timedelta(hours=2)],s,s+timedelta(hours=2),timedelta(hours=1)) == [s+timedelta(hours=1)]
