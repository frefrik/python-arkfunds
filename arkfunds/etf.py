from datetime import date

import pandas as pd

from .arkfunds import ArkFunds
from .utils import _convert_to_list


class ETF(ArkFunds):
    """Class for accessing ARK ETF data"""

    _COLUMNS = {
        "profile": [
            "symbol",
            "name",
            "description",
            "fund_type",
            "inception_date",
            "cusip",
            "isin",
            "website",
        ],
        "holdings": [
            "fund",
            "date",
            "company",
            "ticker",
            "cusip",
            "shares",
            "market_value",
            "share_price",
            "weight",
            "weight_rank",
        ],
        "trades": [
            "fund",
            "date",
            "direction",
            "ticker",
            "company",
            "cusip",
            "shares",
            "etf_percent",
        ],
        "news": [
            "id",
            "datetime",
            "related",
            "source",
            "headline",
            "summary",
            "url",
            "image",
        ],
        "performance": [
            "fund",
            "datatype",
            "as_of_date",
            "period",
            "return",
        ],
    }

    def __init__(self, symbols: str):
        """Initialize

        Args:
            symbols (str or list): ARK ETF symbol or list collection of symbols
        """
        super(ETF, self).__init__(symbols)
        self.symbols = _convert_to_list(symbols)
        self._validate_symbols()

    def _validate_symbols(self):
        valid_symbols = []
        invalid_symbols = []

        for symbol in self.symbols:
            if symbol in self.ARK_FUNDS:
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)

        self.symbols = valid_symbols
        self.invalid_symbols = invalid_symbols or None

    def _dataframe(self, symbols, params):
        endpoint = params["endpoint"]
        columns = self._COLUMNS[endpoint]
        dataframes = []

        if not self.symbols:
            return (
                f"ETF.{endpoint}: Invalid symbols {self.invalid_symbols}. "
                f"Symbols accepted: {', '.join(self.ARK_FUNDS)}"
            )
        else:
            for symbol in symbols:
                params["query"]["symbol"] = symbol
                data = self._get(params)

                if endpoint == "performance":
                    data = self._transform_performance_data(data)

                if not isinstance(data[endpoint], list):
                    df = pd.DataFrame([data[endpoint]], columns=columns)
                else:
                    df = pd.DataFrame(data[endpoint], columns=columns)

                dataframes.append(df)

            return pd.concat(dataframes, axis=0).reset_index(drop=True)

    def _transform_performance_data(self, data):
        fund = data["symbol"]
        performance = data["performance"][0]

        overview = performance["overview"]
        trailing_returns = performance["trailingReturns"]
        annual_returns = performance["annualReturns"]

        rows = []

        # Handle overview data
        for period, return_value in overview.items():
            if period != "asOfDate":
                rows.append(
                    {
                        "fund": fund,
                        "datatype": "Overview",
                        "as_of_date": overview["asOfDate"],
                        "period": period,
                        "return": return_value,
                    }
                )

        # Handle trailing returns data
        for period, return_value in trailing_returns.items():
            if period != "asOfDate":
                rows.append(
                    {
                        "fund": fund,
                        "datatype": "TrailingReturns",
                        "as_of_date": trailing_returns["asOfDate"],
                        "period": period,
                        "return": return_value,
                    }
                )

        # Handle annual returns data
        for annual_return in annual_returns:
            rows.append(
                {
                    "fund": fund,
                    "datatype": "AnnualReturns",
                    "as_of_date": f"{annual_return['year']}-12-31",
                    "period": str(annual_return["year"]),
                    "return": annual_return["value"],
                }
            )

        return {"performance": rows}

    def profile(self):
        """Get ARK ETF profile information

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "etf",
            "endpoint": "profile",
            "query": {},
        }

        return self._dataframe(self.symbols, params)

    def holdings(self, _date: date = None):
        """Get ARK ETF holdings

        Args:
            _date (date, optional): Fund holding date in ISO 8601 format. Defaults to None.

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "etf",
            "endpoint": "holdings",
            "query": {
                "date": _date,
            },
        }

        return self._dataframe(self.symbols, params)

    def trades(self, period: str = "1d"):
        """Get ARK ETF intraday trades

        Args:
            period (str, optional): Valid periods: 1d, 7d, 1m, 3m, 1y, ytd. Defaults to "1d".

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "etf",
            "endpoint": "trades",
            "query": {
                "period": period,
            },
        }

        return self._dataframe(self.symbols, params)

    def news(self, date_from: date = None, date_to: date = None):
        """Get ARK ETF news

        Args:
            date_from (date, optional): From-date in ISO 8601 format. Defaults to None.
            date_to (date, optional): To-date in ISO 8601 format. Defaults to None.

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "etf",
            "endpoint": "news",
            "query": {
                "date_from": date_from,
                "date_to": date_to,
            },
        }

        return self._dataframe(self.symbols, params)

    def performance(self, formatted: bool = False):
        """Get ARK ETF performance

        Args:
            formatted (bool, optional): Return formatted values. Defaults to false.

        Returns:
            pandas.DataFrame
        """
        params = {
            "key": "etf",
            "endpoint": "performance",
            "query": {
                "formatted": formatted,
            },
        }

        return self._dataframe(self.symbols, params)
