from datetime import date

import pandas as pd

from .arkfunds import ArkFunds
from .utils import _convert_to_list


class Stock(ArkFunds):
    """Class for accessing Stock data"""

    _COLUMNS = {
        "profile": [
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
        ],
        "ownership": [
            "ticker",
            "date",
            "fund",
            "weight",
            "weight_rank",
            "shares",
            "market_value",
        ],
        "trades": [
            "ticker",
            "date",
            "fund",
            "direction",
            "shares",
            "etf_percent",
        ],
        "price": [
            "ticker",
            "exchange",
            "currency",
            "price",
            "change",
            "changep",
            "last_trade",
        ],
    }

    def __init__(self, symbols: str):
        """Initialize

        Args:
            symbol (str): Stock ticker
        """
        super(Stock, self).__init__(symbols)
        self.symbols = _convert_to_list(symbols)

    def _dataframe(self, symbols, params):
        endpoint = params["endpoint"]
        columns = self._COLUMNS[endpoint]
        dataframes = []

        for symbol in symbols:
            params["query"]["symbol"] = symbol
            data = self._get(params)

            if not data:
                continue

            if endpoint == "profile":
                df = self._handle_profile_data(data, columns)
            elif endpoint == "ownership":
                df = self._handle_ownership_data(symbol, data, columns)
            elif endpoint == "price":
                df = self._handle_price_data(symbol, data, columns)
            elif endpoint == "trades":
                df = self._handle_trades_data(symbol, data, columns)
            else:
                df = self._handle_generic_data(data, endpoint, columns)

            if df.empty:
                continue

            dataframes.append(df)

        if not dataframes:
            return pd.DataFrame(columns=columns)
        else:
            return pd.concat(dataframes, axis=0).reset_index(drop=True)

    def _handle_profile_data(self, data, columns):
        if not data["profile"]:
            return pd.DataFrame(columns=columns)

        return pd.DataFrame([data["profile"]], columns=columns)

    def _handle_price_data(self, symbol, data, columns):
        if all(value is None for key, value in data.items() if key != "symbol"):
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame([data], columns=columns)
        df["ticker"] = symbol

        return df

    def _handle_trades_data(self, symbol, data, columns):
        if not data["trades"]:
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(data["trades"], columns=columns)
        df["ticker"] = symbol

        return df

    def _handle_generic_data(self, data, endpoint, columns):
        if not isinstance(data[endpoint], list):
            return pd.DataFrame([data[endpoint]], columns=columns)

        return pd.DataFrame(data[endpoint], columns=columns)

    def _handle_ownership_data(self, symbol, data, columns):
        if not data["data"]:
            return pd.DataFrame(columns=columns)

        dataframes = []
        for day_data in data["data"]:
            for ownership_data in day_data["ownership"]:
                df = pd.DataFrame([ownership_data], columns=columns)
                df["ticker"] = symbol
                dataframes.append(df)

        df = pd.concat(dataframes, axis=0).reset_index(drop=True)
        df = df.sort_values(by=["ticker", "date", "weight_rank"])

        return df

    def profile(self, price: bool = False):
        """Get Stock profile information

        Args:
            price (bool, optional): Show current share price. Defaults to False.

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "stock",
            "endpoint": "profile",
            "query": {
                "price": price,
            },
        }

        return self._dataframe(self.symbols, params)

    def fund_ownership(
        self, date_from: date = None, date_to: date = None, limit: int = None
    ):
        """Get Stock Fund Ownership

        Args:
            date_from (date, optional): From-date in ISO 8601 format. Defaults to None.
            date_to (date, optional): To-date in ISO 8601 format. Defaults to None.
            limit (int, optional): Limit number of results. Defaults to None.

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "stock",
            "endpoint": "ownership",
            "query": {
                "date_from": date_from,
                "date_to": date_to,
                "limit": limit,
            },
        }

        return self._dataframe(self.symbols, params)

    def trades(
        self,
        direction: str = None,
        date_from: date = None,
        date_to: date = None,
        limit: int = None,
    ):
        """Get Stock Trades

        Args:
            direction (str, optional): 'Buy' or 'Sell'. Defaults to None.
            date_from (date, optional): From-date in ISO 8601 format.. Defaults to None.
            date_to (date, optional): To-date in ISO 8601 format.. Defaults to None.
            limit (int, optional): Limit number of results. Defaults to None.

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "stock",
            "endpoint": "trades",
            "query": {
                "direction": [direction.lower() if direction else None],
                "date_from": date_from,
                "date_to": date_to,
                "limit": limit,
            },
        }

        return self._dataframe(self.symbols, params)

    def price(self):
        """Get current stock price info

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "stock",
            "endpoint": "price",
            "query": {},
        }

        return self._dataframe(self.symbols, params)
