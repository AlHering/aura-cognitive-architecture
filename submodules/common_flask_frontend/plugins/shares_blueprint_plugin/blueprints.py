# -*- coding: utf-8 -*-
"""
****************************************************
*        Share Screener Blueprints-Plugin
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from datetime import datetime
from typing import Any, List, Optional, Union
from flask import Blueprint, render_template, request, url_for, redirect, flash, Response
import yfinance

PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
TICKERS = {}
SHARE_SCREENER_BLUEPRINT = Blueprint(
    "share_screener",
    __name__,
    template_folder=f"{PLUGIN_PATH}/templates",
    static_folder=f"{PLUGIN_PATH}/static",
    url_prefix='/share-screener'
)
UNIX_TS_CONVERSION = lambda x: datetime.utcfromtimestamp(int(x)).strftime("%d. %B %Y")
ROUND_VALUE = lambda x: round(float(x), 2)
PERCENTAGE_VALUE = lambda x: f"{round(float(x)*100, 2)}%"
STATIC_TRANSFORMATION = {
    "shortName": {
        "name": "Name"
    },
    "longName": {
        "name": "Long Name"
    },
    "longBusinessSummary": {
        "name": "Description"
    },
    "address1": {
        "name": "Address"
    },
    "zip": {
        "name": "ZIP Code"
    },
    "companyOfficers": {
        "name": "Officers"
    },
    "financialCurrency": {
        "name": "Currency"
    },
    "quoteType": {
        "name": "Quote Type"
    },
    "industry": {
        "name": "Industry"
    },
    "sector": {
        "name": "Sector"
    },
    "country": {
        "name": "Country"
    },
    "city": {
        "name": "City"
    },
    "phone": {
        "name": "Phone"
    },
    "fax": {
        "name": "Fax"
    },
    "website": {
        "name": "Website"
    },
    "logo_url": {
        "name": "Logo URL"
    },
    "exchange": {
        "name": "Exchange"
    },
    "exchangeTimezoneName": {
        "name": "Exchange Timezone"
    },
    "exchangeTimezoneShortName": {
        "name": "Exchange Timezone Short"
    },
    "fundFamily": {
        "name": "Fund Family"
    }
}
VALUATION_MEASURES_TRANSFORMATION = {
    "market_cap": {
        "name": "Market Cap (intraday)",
        "transform": ROUND_VALUE
    },
    "enterpriseValue": {
        "name": "Enterprise Value",
        "transform": ROUND_VALUE
    },
    "trailingPE": {
        "name": "Trailing P/E",
        "transform": ROUND_VALUE
    },
    "forwardPE": {
        "name": "Forward P/E",
        "transform": ROUND_VALUE
    },
    "trailingPegRatio": {
        "name": "Trailing PEG Ratio (5 year expected)",
        "transform": ROUND_VALUE
    },
    "pegRatio": {
        "name": "PEG Ratio",
        "transform": ROUND_VALUE
    },
    "priceToSalesTrailing12Months": {
        "name": "Price/Sales (ttm)",
        "transform": ROUND_VALUE
    },
    "priceToBook": {
        "name": "Price/Book (mrq)",
        "transform": ROUND_VALUE
    },
    "enterpriseToRevenue": {
        "name": "Enterprise Value/Revenue",
        "transform": ROUND_VALUE
    },
    "enterpriseToEbitda": {
        "name": "Enterprise Value/EBITDA",
        "transform": ROUND_VALUE
    }
}
FINANCIAL_HIGHLIGHTS_TRANSFORMATION = {
    "lastFiscalYearEnd": {
        "name": "Last Fiscal Year End",
        "transform": UNIX_TS_CONVERSION
    },
    "nextFiscalYearEnd": {
        "name": "Fiscal Year End",
        "transform": UNIX_TS_CONVERSION
    },
    "mostRecentQuarter": {
        "name": "Most Recent Quarter (mrq)",
        "transform": UNIX_TS_CONVERSION
    },
    "profitMargins": {
        "name": "Profit Margin",
        "transform": PERCENTAGE_VALUE
    },
    "operatingMargins": {
        "name": "Operating Margin (ttm)",
        "transform": PERCENTAGE_VALUE
    },
    "returnOnAssets": {
        "name": "Return on Assets (ttm)",
        "transform": PERCENTAGE_VALUE
    },
    "returnOnEquity": {
        "name": "Return on Equity (ttm)",
        "transform": PERCENTAGE_VALUE
    },
    "ytdReturn": {
        "name": "Year-to-Date Return",
        "transform": PERCENTAGE_VALUE
    },
    "fiveYearAverageReturn": {
        "name": "Average Return (5 year)",
        "transform": PERCENTAGE_VALUE
    },
    "totalRevenue": {
        "name": "Revenue (ttm)",
        "transform": ROUND_VALUE
    },
    "revenuePerShare": {
        "name": "Revenue Per Share (ttm)",
        "transform": ROUND_VALUE
    },
    "revenueGrowth": {
        "name": "Quarterly Revenue Growth (yoy)",
        "transform": PERCENTAGE_VALUE
    },
    "grossProfits": {
        "name": "Gross Profit (ttm)",
        "transform": ROUND_VALUE
    },
    "ebitda": {
        "name": "EBITDA",
        "transform": ROUND_VALUE
    },
    "netIncomeToCommon": {
        "name": "Net Income Avi to Common (ttm)",
        "transform": ROUND_VALUE
    },
    "trailingEps": {
        "name": "Diluted EPS (ttm)",
        "transform": ROUND_VALUE
    },
    "forwardEps": {
        "name": "Forward EPS",
        "transform": ROUND_VALUE
    },
    "earningsQuarterlyGrowth": {
        "name": "Quarterly Earnings Growth (yoy)",
        "transform": PERCENTAGE_VALUE
    },
    "totalCash": {
        "name": "Total Cash (mrq)",
        "transform": ROUND_VALUE
    },
    "totalCashPerShare": {
        "name": "Total Cash Per Share (mrq)",
        "transform": ROUND_VALUE
    },
    "totalDept": {
        "name": "Total Debt (mrq)",
        "transform": ROUND_VALUE
    },
    "debtToEquity": {
        "name": "Total Debt/Equity (mrq)",
        "transform": ROUND_VALUE
    },
    "currentRatio": {
        "name": "Current Ratio (mrq)",
        "transform": ROUND_VALUE
    },
    "bookValue": {
        "name": "Book Value Per Share (mrq)",
        "transform": ROUND_VALUE
    },
    "operatingCashflow": {
        "name": "Operating Cash Flow (ttm)",
        "transform": ROUND_VALUE
    },
    "freeCashflow": {
        "name": "Levered Free Cash Flow (ttm)",
        "transform": ROUND_VALUE
    }
}
TRADING_INFORMATION_TRANSFORMATION = {
    "beta": {
        "name": "Beta (5Y Monthly) ",
        "transform": ROUND_VALUE
    },
    "52WeekChange": {
        "name": "52-Week Change",
        "transform": PERCENTAGE_VALUE
    },
    "SandP52WeekChange": {
        "name": "S&P500 52-Week Change",
        "transform": PERCENTAGE_VALUE
    },
    "year_high": {
        "name": "52 Week High",
        "transform": ROUND_VALUE
    },
    "year_low": {
        "name": "52 Week Low",
        "transform": ROUND_VALUE
    },
    "fifty_day_average": {
        "name": "50-Day Moving Average",
        "transform": ROUND_VALUE
    },
    "two_hundred_day_average": {
        "name": "200-Day Moving Average",
        "transform": ROUND_VALUE
    },
    "three_month_average_volume": {
        "name": "Average Volume (3 month)",
        "transform": ROUND_VALUE
    },
    "ten_day_average_volume": {
        "name": "Average Volume (10 day)",
        "transform": ROUND_VALUE
    },
    "shares": {
        "name": "Shares Outstanding",
        "transform": ROUND_VALUE
    },
    "impliedSharesOutstanding": {
        "name": "Implied Shares Outstanding",
        "transform": ROUND_VALUE
    },
    "floatShares": {
        "name": "Float Shares",
        "transform": ROUND_VALUE
    },
    "heldPercentInsiders": {
        "name": "% Held by Insiders",
        "transform": PERCENTAGE_VALUE
    },
    "heldPercentInstitutions": {
        "name": "% Held by Institutions",
        "transform": PERCENTAGE_VALUE
    },
    "sharesShort": {
        "name": "Shares Short",
        "transform": ROUND_VALUE
    },
    "shortRatio": {
        "name": "Short Ratio",
        "transform": ROUND_VALUE
    },
    "shortPercentOfFloat": {
        "name": "Short % of Float",
        "transform": PERCENTAGE_VALUE
    },
    "sharesPercentSharesOut": {
        "name": "Short % of Shares Outstanding",
        "transform": PERCENTAGE_VALUE
    },
    "sharesShortPreviousMonthDate": {
        "name": "Shares Short (prior month)",
        "transform": ROUND_VALUE
    },
    "dividendRate": {
        "name": "Forward Annual Dividend Rate",
        "transform": ROUND_VALUE
    },
    "dividendYield": {
        "name": "Forward Annual Dividend Yield",
        "transform": PERCENTAGE_VALUE
    },
    "trailingAnnualDividendRate": {
        "name": "Trailing Annual Dividend Rate",
        "transform": ROUND_VALUE
    },
    "trailingAnnualDividendYield": {
        "name": "Trailing Annual Dividend Yield",
        "transform": PERCENTAGE_VALUE
    },
    "fiveYearAvgDividendYield": {
        "name": "5 Year Average Dividend Yield",
        "transform": PERCENTAGE_VALUE
    },
    "payoutRatio": {
        "name": "Payout Ratio",
        "transform": PERCENTAGE_VALUE
    },
    "lastDividendDate": {
        "name": "Dividend Date",
        "transform": UNIX_TS_CONVERSION
    },
    "exDividendDate": {
        "name": "Ex-Dividend Date",
        "transform": UNIX_TS_CONVERSION
    },
    "lastDividendValue": {
        "name": "Last Dividend Value",
        "transform": ROUND_VALUE
    },
    "lastSplitFactor": {
        "name": "Last Split Factor"
    },
    "lastSplitDate": {
        "name": "Last Split Date",
        "transform": UNIX_TS_CONVERSION
    }
}


def setup_ticker(ticker: str) -> yfinance.Ticker:
    """
    Function for setting up ticker.
    :param ticker: Ticker to set up.
    :return: YFinance Ticker.
    """
    return yfinance.Ticker(ticker)


def extract_dictionary(transformation: dict, info: dict, fast_info: dict) -> dict:
    """
    Function for extracting dictionary from YFinance info.
    :param transformation: Transformation dictionary.
    :param info: Info dictionary.
    :param fast_info: Fast info dictionary.
    :return: Transformed dictionary
    """
    res = {}
    for key in transformation:
        try:
            val = fast_info[key]
        except KeyError:
            val = None
        if val is None:
            val = info.get(key)
        if val and "transform" in transformation[key]:
            val = transformation[key]["transform"](val)
        res[transformation[key]["name"]] = val
    return res


def get_blueprints(global_config: dict) -> List[Blueprint]:
    """
    Main plugin handle function.
    :param global_config: Global Flask app config.
    :return: List of blueprints to integrate into flask app.
    """
    global_config["plugins"]["SharesBlueprints"] = {
    }

    @SHARE_SCREENER_BLUEPRINT.route("/shares", methods=["GET", "POST"])
    def show_share_screener() -> Union[str, Response]:
        """
        Share screener template method.
        :return: Share screener template.
        """
        if request.method == "GET":
            return render_template("shares.html", **global_config)
        elif request.method == "POST":
            data = request.form
            ticker_symbol = data.get("ticker")
            if ticker_symbol not in global_config["plugins"]["SharesBlueprints"]:
                ticker = setup_ticker(ticker_symbol)
                try:
                    info = ticker.info
                except Exception:
                    info = {}
                fast_info = ticker.fast_info
                history = ticker.history(period="1y", repair=True).to_dict(orient="index")
                if ticker:
                    TICKERS[ticker_symbol] = ticker
                    global_config["plugins"]["SharesBlueprints"][ticker_symbol] = {
                        "static": extract_dictionary(STATIC_TRANSFORMATION, info, fast_info),
                        "valuation": extract_dictionary(VALUATION_MEASURES_TRANSFORMATION, info, fast_info),
                        "financials": extract_dictionary(FINANCIAL_HIGHLIGHTS_TRANSFORMATION, info, fast_info),
                        "trading": extract_dictionary(TRADING_INFORMATION_TRANSFORMATION, info, fast_info),
                        "history": history
                    }
                    # Redirect to new ticker screener endpoint with GET request.
                    return redirect(url_for(".show_ticker", ticker=ticker_symbol), code=303)
                else:
                    flash(f"Ticker {ticker} could not be setup!", "error")
                    # Redirect to screener main page endpoint with GET request.
                    return render_template("shares.html", **global_config)
            else:
                flash(f"Ticker {ticker_symbol} already registered!", "info")
                # Redirect to new ticker screener endpoint with GET request.
                return redirect(url_for(".show_ticker", ticker=ticker_symbol), code=303)

    @SHARE_SCREENER_BLUEPRINT.route("/shares/<ticker>", methods=["GET"])
    def show_ticker(ticker: str = None) -> Union[str, Response]:
        """
        Share screener template method.
        :param ticker: Ticker symbol. Defaults to None.
        :return: Share screener template.
        """
        if ticker in global_config["plugins"]["SharesBlueprints"]:
            return render_template("shares.html", ticker=ticker, **global_config)
        else:
            flash(f"Ticker {ticker} was not found!", "warning")
            # Redirect to main screener endpoint with GET request.
            return render_template("shares.html", **global_config)

    return [SHARE_SCREENER_BLUEPRINT]


def get_menu() -> dict:
    """
    Function for getting menu dictionary.
    :return: Menu dictionary.
    """
    return {
        "Share Screener": {
            "Shares": {
                "icon": "bed",
                "type": "fa",
                "href": "share_screener.show_share_screener"
            }
        }
    }