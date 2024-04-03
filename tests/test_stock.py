import pytest

from arkfunds import Stock

STOCKS = [
    Stock("TSLA"),
    Stock("tsla, coin"),
    Stock("tdoc, aapl, tsla"),
    Stock("tdoc, aapl, loloil"),
    Stock("roku SHOP tsla"),
    Stock(["TSLA", "sq", "TDOC", "spot"]),
]


@pytest.fixture(params=STOCKS)
def stock(request):
    return request.param


def test_stock_profile(stock):
    assert not stock.profile().empty


def test_stock_profile_columns(stock):
    columns = [
        "ticker",
        "name",
        "country",
        "industry",
        "sector",
        "fullTimeEmployees",
        "summary",
        "website",
        "exchange",
        "currency",
        "marketCap",
        "sharesOutstanding",
    ]
    assert stock.profile().columns.to_list() == columns


def test_bad_stock_profile(symbol="LOLOIL"):
    df = Stock(symbol).profile()
    assert df.empty and df.columns.to_list() == [
        "ticker",
        "name",
        "country",
        "industry",
        "sector",
        "fullTimeEmployees",
        "summary",
        "website",
        "exchange",
        "currency",
        "marketCap",
        "sharesOutstanding",
    ]


def test_stock_fund_ownership(stock):
    assert not stock.fund_ownership().empty


def test_stock_trades(stock):
    assert not stock.trades().empty


def test_stock_price(stock):
    assert not stock.price().empty


def test_stock_symbols_list():
    symbols = [
        "tsla, aapl, tdoc",
        "tsla aapl tdoc",
        ["tsla", "aapl", "tdoc"],
    ]
    for symbol in symbols:
        stock = Stock(symbol)
    assert stock.symbols == ["TSLA", "AAPL", "TDOC"]
