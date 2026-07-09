import argparse
import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Asset, Exchange, Market


async def seed_core() -> None:
    async with SessionLocal() as session:
        for key, name in (("kraken", "Kraken"), ("binance", "Binance")):
            if not await session.scalar(select(Exchange).where(Exchange.key == key)):
                session.add(Exchange(key=key, name=name, enabled=True))
        for symbol, name in (("BTC", "Bitcoin"), ("ETH", "Ether")):
            if not await session.scalar(select(Asset).where(Asset.symbol == symbol)):
                session.add(Asset(symbol=symbol, name=name, active=True))
        await session.commit()
        kraken = await session.scalar(select(Exchange).where(Exchange.key == "kraken"))
        btc = await session.scalar(select(Asset).where(Asset.symbol == "BTC"))
        eth = await session.scalar(select(Asset).where(Asset.symbol == "ETH"))
        assert kraken and btc and eth
        for asset, sym in ((btc, "BTC/USD"), (eth, "ETH/USD")):
            if not await session.scalar(
                select(Market).where(Market.exchange_id == kraken.id, Market.exchange_symbol == sym)
            ):
                session.add(
                    Market(
                        exchange_id=kraken.id,
                        asset_id=asset.id,
                        exchange_symbol=sym,
                        base_currency=asset.symbol,
                        quote_currency="USD",
                        active=True,
                        minimum_amount=Decimal("0.00000001"),
                        minimum_cost=Decimal("1"),
                        amount_precision=8,
                        price_precision=2,
                    )
                )
        await session.commit()


def main() -> None:
    argparse.ArgumentParser(description="Seed CryptoPilot core records").parse_args()
    asyncio.run(seed_core())


if __name__ == "__main__":
    main()
