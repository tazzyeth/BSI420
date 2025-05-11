import requests
import pandas as pd
from datetime import datetime
import time
from config import Config
import re
from collections import deque
from datetime import datetime, timedelta
import json
import random
import numpy as np

class DataFetcher:
    def __init__(self):
        self.api_key = Config.ALPHA_VANTAGE_API_KEY
        self.base_url = Config.ALPHA_VANTAGE_BASE_URL
        self.request_times = deque(maxlen=Config.REQUESTS_PER_MINUTE)
        self.api_timeout = Config.API_TIMEOUT
        
        print(f"DataFetcher initialized with API key: {self.api_key[:4]}***")
        print(f"Rate limit set to {Config.REQUESTS_PER_MINUTE} requests per minute")
        print(f"API timeout set to {self.api_timeout} seconds")
        
        # Always disable mock data
        self.use_mock_data = False
        self.use_advanced_indicators = Config.USE_ADVANCED_INDICATORS
        
        print(f"Mock data feature: DISABLED")
        print(f"Advanced indicators: {'ENABLED' if self.use_advanced_indicators else 'DISABLED'}")
        
        self.mock_data_loaded = False
        self.mock_data = {}

    def _load_mock_data(self):
        """Load mock data for fallback when APIs fail"""
        try:
            # Sample mocked data
            self.mock_data = {
                # Overview data mock
                "overview": {
                    "Symbol": "MOCK",
                    "Name": "Mock Company Inc.",
                    "Description": "This is mock data used when API calls fail. The company doesn't exist.",
                    "Exchange": "NASDAQ",
                    "Currency": "USD",
                    "Country": "USA",
                    "Sector": "Technology",
                    "Industry": "Software",
                    "MarketCapitalization": "1200000000",
                    "EBITDA": "500000000",
                    "PERatio": "25.5",
                    "PEGRatio": "1.5",
                    "BookValue": "45.5",
                    "DividendPerShare": "0.5",
                    "DividendYield": "0.01",
                    "EPS": "8.5",
                    "RevenuePerShareTTM": "75.5",
                    "ProfitMargin": "0.15",
                    "OperatingMarginTTM": "0.25",
                    "ReturnOnAssetsTTM": "0.12",
                    "ReturnOnEquityTTM": "0.22",
                    "RevenueTTM": "7500000000",
                    "GrossProfitTTM": "5000000000",
                    "DilutedEPSTTM": "8.5",
                    "QuarterlyEarningsGrowthYOY": "0.05",
                    "QuarterlyRevenueGrowthYOY": "0.08",
                    "AnalystTargetPrice": "155.5",
                    "TrailingPE": "25.5",
                    "ForwardPE": "22.5",
                    "PriceToSalesRatioTTM": "6.5",
                    "PriceToBookRatio": "3.5",
                    "EVToRevenue": "6.2",
                    "EVToEBITDA": "12.5",
                    "Beta": "1.2",
                    "52WeekHigh": "180.75",
                    "52WeekLow": "120.25",
                    "50DayMovingAverage": "150.5",
                    "200DayMovingAverage": "145.25",
                    "SharesOutstanding": "100000000",
                    "SharesFloat": "85000000",
                    "SharesShort": "2000000",
                    "SharesShortPriorMonth": "1800000",
                    "ShortRatio": "2.5",
                    "ShortPercentOutstanding": "0.02",
                    "ShortPercentFloat": "0.0235",
                    "PercentInsiders": "15",
                    "PercentInstitutions": "65",
                    "ForwardAnnualDividendRate": "2.0",
                    "ForwardAnnualDividendYield": "0.01",
                    "PayoutRatio": "0.2",
                    "DividendDate": "2023-12-15",
                    "ExDividendDate": "2023-11-30",
                    "LastSplitFactor": "2:1",
                    "LastSplitDate": "2020-08-31",
                    "CurrentRatio": "2.5"
                },
                
                # Time series data mock
                "time_series": self._generate_mock_time_series(),
                
                # Global quote mock
                "global_quote": {
                    "Global Quote": {
                        "01. symbol": "MOCK",
                        "02. open": "155.5",
                        "03. high": "156.8",
                        "04. low": "153.2",
                        "05. price": "155.0",
                        "06. volume": "5500000",
                        "07. latest trading day": datetime.now().strftime("%Y-%m-%d"),
                        "08. previous close": "154.2",
                        "09. change": "0.8",
                        "10. change percent": "0.52%"
                    }
                },
                
                # Supplementary data mock
                "supplementary": {
                    "float": "85M",
                    "short_float_percent": "2.35%",
                    "institutional_ownership": "65%",
                    "insider_ownership": "15%",
                    "short_ratio": "2.5",
                    "beta": "1.2",
                    "52_week_high": "$180.75",
                    "52_week_low": "$120.25",
                    "profit_margin": "15%",
                    "operating_margin": "25%",
                    "return_on_assets": "12%",
                    "return_on_equity": "22%",
                    "revenue_per_share": "$75.50",
                    "peg_ratio": "1.5",
                    "enterprise_value": "$12.5B",
                    "forward_pe": "22.5",
                    "current_ratio": "2.5",
                    "current_volume": "5,500,000",
                    "average_volume": "4,800,000",
                    "relative_volume": "1.15x",
                    "analyst_rating": "2.5 (Buy)",
                    "buy_ratings": "15",
                    "hold_ratings": "8",
                    "sell_ratings": "2"
                },
                
                # Insider transactions mock
                "insider_transactions": {
                    "symbol": "MOCK",
                    "transactions": [
                        {
                            "transactionDate": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                            "transactionType": "Buy",
                            "transactionShares": "10000",
                            "transactionPrice": "150.25",
                            "reporterName": "SMITH JOHN",
                            "reporterTitle": "CEO"
                        },
                        {
                            "transactionDate": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                            "transactionType": "Sell",
                            "transactionShares": "5000",
                            "transactionPrice": "155.50",
                            "reporterName": "DOE JANE",
                            "reporterTitle": "CFO"
                        },
                        {
                            "transactionDate": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                            "transactionType": "Buy",
                            "transactionShares": "2500",
                            "transactionPrice": "145.75",
                            "reporterName": "BROWN DAVID",
                            "reporterTitle": "Director"
                        }
                    ]
                },
                
                # Balance sheet mock
                "balance_sheet": {
                    "symbol": "MOCK",
                    "annualReports": [
                        {
                            "fiscalDateEnding": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                            "totalAssets": "12000000000",
                            "totalCurrentAssets": "5000000000",
                            "totalLiabilities": "5000000000",
                            "totalCurrentLiabilities": "2000000000",
                            "totalShareholderEquity": "7000000000",
                            "intangibleAssets": "1500000000",
                            "longTermDebt": "2500000000"
                        }
                    ]
                },
                
                # Income statement mock
                "income_statement": {
                    "symbol": "MOCK",
                    "annualReports": [
                        {
                            "fiscalDateEnding": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                            "totalRevenue": "7500000000",
                            "grossProfit": "5000000000",
                            "netIncome": "1200000000",
                            "operatingIncome": "1800000000",
                            "ebitda": "2200000000",
                            "researchAndDevelopment": "800000000",
                            "sellingGeneralAdministrative": "1200000000"
                        }
                    ]
                },
                
                # Cash flow mock
                "cash_flow": {
                    "symbol": "MOCK",
                    "annualReports": [
                        {
                            "fiscalDateEnding": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                            "operatingCashflow": "1500000000",
                            "capitalExpenditures": "-500000000",
                            "dividendPayout": "-200000000",
                            "netIncome": "1200000000",
                            "changeInCash": "700000000"
                        }
                    ]
                }
            }
            
            self.mock_data_loaded = True
            
        except Exception as e:
            print(f"Error loading mock data: {e}")
            self.mock_data_loaded = False

    def _generate_mock_time_series(self):
        """Generate realistic looking mock time series data for 1 year"""
        # Start with a base price
        base_price = 150.0
        # Create a dataframe with dates for the past year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        
        # Generate slightly random but trending prices
        trend = 0.0001  # Slight upward trend
        volatility = 0.015  # Daily volatility
        
        # Generate OHLCV data
        data = []
        prev_close = base_price
        for date in dates:
            # Random walk with drift
            change = trend + volatility * random.normalvariate(0, 1)
            close = prev_close * (1 + change)
            # Generate other values based on close
            open_price = close * (1 + 0.005 * random.normalvariate(0, 1))
            high = max(open_price, close) * (1 + abs(0.005 * random.normalvariate(0, 1)))
            low = min(open_price, close) * (1 - abs(0.005 * random.normalvariate(0, 1)))
            # Volume with some randomness
            volume = int(5000000 * (1 + 0.3 * random.normalvariate(0, 1)))
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
            
            prev_close = close
        
        # Create a DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Add technical indicators
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        df['MA200'] = df['close'].rolling(window=200).mean()
        df['daily_return'] = df['close'].pct_change() * 100
        df['avg_volume'] = df['volume'].rolling(window=20).mean()
        df['relative_volume'] = df['volume'] / df['avg_volume']
        df['MA20_std'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['MA20'] + (df['MA20_std'] * 2)
        df['lower_band'] = df['MA20'] - (df['MA20_std'] * 2)
        
        return df

    def _check_rate_limits(self):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Check per-minute limit
        if len(self.request_times) >= Config.REQUESTS_PER_MINUTE:
            oldest_request = self.request_times[0]
            time_since_oldest = current_time - oldest_request
            
            if time_since_oldest < 60:  # Less than a minute has passed
                sleep_time = 60 - time_since_oldest + 1  # Add 1 second buffer
                print(f"Rate limit approaching, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        # Update request times
        self.request_times.append(current_time)

    def _make_request(self, params):
        """Make API request with rate limiting"""
        try:
            self._check_rate_limits()
            
            print(f"Making API request: {self.base_url} with params: {params}")
            response = requests.get(self.base_url, params=params, timeout=self.api_timeout)
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}, Response: {response.text}")
                return None, f"HTTP Error: {response.status_code}"
            
            data = response.json()
            
            # Check for various API error responses
            if "Information" in data:
                if "API call frequency" in data["Information"]:
                    print(f"API rate limit hit: {data['Information']}")
                    return None, "API call frequency limit reached. Please wait a minute before trying again."
                else:
                    print(f"API information message: {data['Information']}")
                    return None, data["Information"]
            
            if "Error Message" in data:
                print(f"API error message: {data['Error Message']}")
                return None, data["Error Message"]
            
            if "Note" in data:
                print(f"API note: {data['Note']}")
                return None, data["Note"]
                
            return data, None
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {str(e)}")
            return None, f"Network error: {str(e)}"
        except ValueError as e:
            print(f"Invalid response: {str(e)}")
            return None, f"Invalid response: {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None, f"Unexpected error: {str(e)}"

    def _generate_mock_technical_indicator(self, params):
        """Generate mock technical indicator data based on function type"""
        function = params.get('function', '').lower()
        symbol = params.get('symbol', 'MOCK')
        
        # Get the base time series data
        df = self.mock_data['time_series']
        
        if function == 'stochrsi':
            # Generate mock StochRSI data
            result = {
                "Meta Data": {
                    "1: Symbol": symbol,
                    "2: Indicator": "Stochastic Relative Strength Index (STOCHRSI)",
                    "3: Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
                    "4: Interval": params.get('interval', 'daily'),
                    "5: Time Period": params.get('time_period', '14'),
                    "6: Series Type": params.get('series_type', 'close')
                },
                "Technical Analysis: STOCHRSI": {}
            }
            
            # Generate random StochRSI values
            for date, row in df.iterrows():
                fastk = random.uniform(0, 100)
                fastd = random.uniform(0, 100)
                
                result["Technical Analysis: STOCHRSI"][date.strftime("%Y-%m-%d")] = {
                    "FastK": str(round(fastk, 2)),
                    "FastD": str(round(fastd, 2))
                }
                
            return result
            
        elif function == 'stochf':
            # Generate mock Fast Stochastic data
            result = {
                "Meta Data": {
                    "1: Symbol": symbol,
                    "2: Indicator": "Stochastic Fast (STOCHF)",
                    "3: Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
                    "4: Interval": params.get('interval', 'daily')
                },
                "Technical Analysis: STOCHF": {}
            }
            
            # Generate random Fast Stochastic values
            for date, row in df.iterrows():
                fastk = random.uniform(0, 100)
                fastd = random.uniform(0, 100)
                
                result["Technical Analysis: STOCHF"][date.strftime("%Y-%m-%d")] = {
                    "FastK": str(round(fastk, 2)),
                    "FastD": str(round(fastd, 2))
                }
                
            return result
            
        elif function == 'bbands':
            # Generate mock Bollinger Bands data
            result = {
                "Meta Data": {
                    "1: Symbol": symbol,
                    "2: Indicator": "Bollinger Bands (BBANDS)",
                    "3: Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
                    "4: Interval": params.get('interval', 'daily'),
                    "5: Time Period": params.get('time_period', '20'),
                    "6: Series Type": params.get('series_type', 'close'),
                    "7: Dev Upper": params.get('nbdevup', '2'),
                    "8: Dev Lower": params.get('nbdevdn', '2')
                },
                "Technical Analysis: BBANDS": {}
            }
            
            # Use the actual moving average and standard deviation if available
            for date, row in df.iterrows():
                middle = row['MA20'] if 'MA20' in df.columns else row['close']
                std = row['MA20_std'] if 'MA20_std' in df.columns else row['close'] * 0.02
                
                upper = middle + (float(params.get('nbdevup', 2)) * std)
                lower = middle - (float(params.get('nbdevdn', 2)) * std)
                
                result["Technical Analysis: BBANDS"][date.strftime("%Y-%m-%d")] = {
                    "Real Upper Band": str(round(upper, 2)),
                    "Real Middle Band": str(round(middle, 2)),
                    "Real Lower Band": str(round(lower, 2))
                }
                
            return result
            
        elif function == 'apo':
            # Generate mock APO data
            result = {
                "Meta Data": {
                    "1: Symbol": symbol,
                    "2: Indicator": "Absolute Price Oscillator (APO)",
                    "3: Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
                    "4: Interval": params.get('interval', 'daily'),
                    "5: Fast Period": params.get('fastperiod', '10'),
                    "6: Slow Period": params.get('slowperiod', '26'),
                    "7: MA Type": params.get('matype', '1'),
                    "8: Series Type": params.get('series_type', 'close')
                },
                "Technical Analysis: APO": {}
            }
            
            # Generate random APO values
            for date, row in df.iterrows():
                apo = random.uniform(-5, 5)
                
                result["Technical Analysis: APO"][date.strftime("%Y-%m-%d")] = {
                    "APO": str(round(apo, 2))
                }
                
            return result
        
        # Default empty response for unsupported functions
        return {
            "Meta Data": {
                "1: Symbol": symbol,
                "2: Indicator": f"Mock {function}",
                "3: Last Refreshed": datetime.now().strftime("%Y-%m-%d")
            },
            f"Technical Analysis: {function.upper()}": {}
        }

    def fetch_time_series_data(self, ticker, function="TIME_SERIES_DAILY", outputsize="full"):
        """Fetch time series data from Alpha Vantage"""
        params = {
            "function": function,
            "symbol": ticker,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        # Find the time series key (differs based on function)
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break
        
        if not time_series_key:
            return None, "No time series data found in response"
            
        time_series = data.get(time_series_key, {})
        if not time_series:
            return None, "No time series data found"
            
        try:
            df = pd.DataFrame(time_series).T
            
            # Rename columns for consistency
            if function == "TIME_SERIES_DAILY":
                column_map = {
                    '1. open': 'open',
                    '2. high': 'high',
                    '3. low': 'low',
                    '4. close': 'close',
                    '5. volume': 'volume'
                }
            else:
                # Default mapping for other time series functions
                column_map = {}
                for col in df.columns:
                    if 'open' in col.lower():
                        column_map[col] = 'open'
                    elif 'high' in col.lower():
                        column_map[col] = 'high'
                    elif 'low' in col.lower():
                        column_map[col] = 'low'
                    elif 'close' in col.lower():
                        column_map[col] = 'close'
                    elif 'volume' in col.lower():
                        column_map[col] = 'volume'
                    else:
                        column_map[col] = col
            
            # Rename columns
            df = df.rename(columns=column_map)
            
            # Extract standard columns
            standard_columns = ['open', 'high', 'low', 'close', 'volume']
            available_columns = [col for col in standard_columns if col in df.columns]
            
            # Use only available columns
            df = df[available_columns]
            
            # Convert string values to float
            df = df.astype(float)
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            # Sort from oldest to newest
            df = df.sort_index()
            
            # Calculate additional metrics
            self._add_technical_indicators(df)
            
            # Enhance with additional Alpha Vantage technical indicators if possible
            try:
                df = self.enhance_technical_indicators(ticker, df)
            except Exception as e:
                print(f"Warning: Could not enhance time series with API indicators: {e}")
            
            return df, None
        except Exception as e:
            return None, f"Error processing time series data: {str(e)}"

    def _add_technical_indicators(self, df):
        """Add technical indicators to the dataframe"""
        try:
            # Calculate moving averages
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            df['MA200'] = df['close'].rolling(window=200).mean()
            
            # Calculate relative volume
            df['avg_volume'] = df['volume'].rolling(window=20).mean()
            df['relative_volume'] = df['volume'] / df['avg_volume']
            
            # Calculate daily returns
            df['daily_return'] = df['close'].pct_change() * 100
            
            # Calculate Bollinger Bands
            df['MA20_std'] = df['close'].rolling(window=20).std()
            df['upper_band'] = df['MA20'] + (df['MA20_std'] * 2)
            df['lower_band'] = df['MA20'] - (df['MA20_std'] * 2)
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            ema12 = df['close'].ewm(span=12, adjust=False).mean()
            ema26 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = ema12 - ema26
            df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_hist'] = df['MACD'] - df['MACD_signal']
            
            # Calculate Average True Range (ATR)
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=14).mean()
            
            # Calculate On-Balance Volume (OBV)
            df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
            
        except Exception as e:
            print(f"Warning: Could not calculate all technical indicators: {str(e)}")

    def enhance_technical_indicators(self, ticker, df):
        """Add enhanced technical indicators to the dataframe from Alpha Vantage API"""
        # Skip if advanced indicators are disabled
        if not self.use_advanced_indicators:
            print("Advanced technical indicators disabled in configuration")
            return df
            
        try:
            # Fetch advanced indicators from API
            # Bollinger Bands (BB)
            bb_data, error = self.fetch_bbands(ticker)
            if not error and isinstance(bb_data, pd.DataFrame) and not bb_data.empty:
                # Merge with time series data
                df = df.join(bb_data, how='left')
                print("Added Bollinger Bands data")
                
            # Stochastic RSI
            stoch_rsi_data, error = self.fetch_stoch_rsi(ticker)
            if not error and isinstance(stoch_rsi_data, pd.DataFrame) and not stoch_rsi_data.empty:
                # Merge with time series data
                df = df.join(stoch_rsi_data, how='left')
                print("Added StochRSI data")
                
            # Fast Stochastic
            stoch_fast_data, error = self.fetch_stoch_fast(ticker)
            if not error and isinstance(stoch_fast_data, pd.DataFrame) and not stoch_fast_data.empty:
                # Merge with time series data
                df = df.join(stoch_fast_data, how='left')
                print("Added Fast Stochastic data")
                
            # APO
            apo_data, error = self.fetch_apo(ticker)
            if not error and isinstance(apo_data, pd.DataFrame) and not apo_data.empty:
                # Merge with time series data
                df = df.join(apo_data, how='left')
                print("Added APO data")
            
            return df
            
        except Exception as e:
            print(f"Warning: Could not add all enhanced technical indicators: {e}")
            return df

    def fetch_bbands(self, ticker):
        """Fetch Bollinger Bands indicator data from Alpha Vantage"""
        params = {
            "function": "BBANDS",
            "symbol": ticker,
            "interval": "daily",
            "time_period": "20",
            "series_type": "close",
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "Technical Analysis: BBANDS" not in data:
            return None, "No Bollinger Bands data found"
            
        # Convert to DataFrame
        try:
            bbands_data = data["Technical Analysis: BBANDS"]
            df = pd.DataFrame.from_dict(bbands_data, orient='index')
            
            # Convert string values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            # Rename columns
            df.columns = ['bb_upper', 'bb_middle', 'bb_lower']
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            return df, None
        except Exception as e:
            return None, f"Error processing Bollinger Bands data: {str(e)}"

    def _format_number_with_suffix(self, number):
        """Format large numbers with K, M, B suffixes"""
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.2f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.2f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.2f}K"
        else:
            return f"{number:.2f}"

    def fetch_company_overview(self, ticker):
        """Fetch company overview data from Alpha Vantage."""
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        # Process and format the data for better display
        try:
            # Helper function to safely extract and format percentage values
            def safe_value(value, is_percentage=False):
                try:
                    if value == "None" or value is None or value == "":
                        return "N/A"
                    
                    if isinstance(value, str) and is_percentage and "%" in value:
                        return value  # Already formatted
                    
                    if is_percentage:
                        try:
                            float_val = float(value)
                            return f"{float_val * 100:.2f}%" if float_val < 1 else f"{float_val:.2f}%"
                        except (ValueError, TypeError):
                            return f"{value}%"
                    
                    # For non-percentage values
                    if isinstance(value, (int, float)):
                        return str(value)
                    elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                        return value
                    else:
                        return value
                except:
                    return "N/A"
            
            # Format ownership data if available
            if 'PercentInsiders' in data:
                try:
                    insider_pct = float(data['PercentInsiders'])
                    data['InsiderOwnership'] = f"{insider_pct:.2f}%"
                except (ValueError, TypeError):
                    if isinstance(data['PercentInsiders'], str) and "%" in data['PercentInsiders']:
                        data['InsiderOwnership'] = data['PercentInsiders']
                    else:
                        data['InsiderOwnership'] = 'N/A'
            
            if 'PercentInstitutions' in data:
                try:
                    inst_pct = float(data['PercentInstitutions'])
                    data['InstitutionalOwnership'] = f"{inst_pct:.2f}%"
                except (ValueError, TypeError):
                    if isinstance(data['PercentInstitutions'], str) and "%" in data['PercentInstitutions']:
                        data['InstitutionalOwnership'] = data['PercentInstitutions']
                    else:
                        data['InstitutionalOwnership'] = 'N/A'
            
            # Calculate float if we have shares outstanding and insider percentage
            if 'SharesOutstanding' in data and 'PercentInsiders' in data:
                try:
                    shares = float(data['SharesOutstanding'])
                    insider_pct = float(data['PercentInsiders']) / 100.0
                    float_shares = shares * (1 - insider_pct)
                    data['Float'] = float_shares
                    data['FloatFormatted'] = self._format_number_with_suffix(float_shares)
                except Exception as e:
                    print(f"Error calculating float: {e}")
                    data['FloatFormatted'] = 'N/A'
            
            # Explicitly handle float data if directly available
            if 'SharesFloat' in data:
                try:
                    float_shares = float(data['SharesFloat'])
                    data['FloatFormatted'] = self._format_number_with_suffix(float_shares)
                except (ValueError, TypeError):
                    if data['SharesFloat'] != 'None' and data['SharesFloat'] is not None:
                        data['FloatFormatted'] = data['SharesFloat']
            
            # Parse current ratio
            if 'CurrentRatio' in data:
                try:
                    current_ratio = safe_value(data['CurrentRatio'])
                    data['CurrentRatioFormatted'] = f"{float(current_ratio):.2f}"
                except (ValueError, TypeError):
                    data['CurrentRatioFormatted'] = data.get('CurrentRatio', 'N/A')
            
            # Parse market cap
            if 'MarketCapitalization' in data:
                try:
                    market_cap = float(data['MarketCapitalization'])
                    data['MarketCapFormatted'] = self._format_number_with_suffix(market_cap)
                except (ValueError, TypeError):
                    data['MarketCapFormatted'] = data.get('MarketCapitalization', 'N/A')
            
            # Parse PEG Ratio
            if 'PEGRatio' in data:
                try:
                    peg_ratio = float(data['PEGRatio'])
                    data['PEGRatioFormatted'] = f"{peg_ratio:.2f}"
                except (ValueError, TypeError):
                    data['PEGRatioFormatted'] = data.get('PEGRatio', 'N/A')
            
            # Parse Forward P/E
            if 'ForwardPE' in data:
                try:
                    forward_pe = float(data['ForwardPE'])
                    data['ForwardPEFormatted'] = f"{forward_pe:.2f}"
                except (ValueError, TypeError):
                    data['ForwardPEFormatted'] = data.get('ForwardPE', 'N/A')
            
            # Print debug information for fields we're having trouble with
            print("\nDEBUG - Company Overview Raw Data:")
            print(f"EPS: {data.get('EPS', 'Not found')}")
            print(f"PEGRatio: {data.get('PEGRatio', 'Not found')}")
            print(f"ForwardPE: {data.get('ForwardPE', 'Not found')}")
            print(f"DividendYield: {data.get('DividendYield', 'Not found')}")
            print(f"MarketCapitalization: {data.get('MarketCapitalization', 'Not found')}")
            print(f"CurrentRatio: {data.get('CurrentRatio', 'Not found')}")
            print(f"SharesFloat: {data.get('SharesFloat', 'Not found')}")
            print(f"PercentInsiders: {data.get('PercentInsiders', 'Not found')}")
            print(f"PercentInstitutions: {data.get('PercentInstitutions', 'Not found')}")
            
            # Print debug info for our formatted values
            print("\nDEBUG - Formatted Values:")
            print(f"InsiderOwnership: {data.get('InsiderOwnership', 'Not found')}")
            print(f"InstitutionalOwnership: {data.get('InstitutionalOwnership', 'Not found')}")
            print(f"FloatFormatted: {data.get('FloatFormatted', 'Not found')}")
            print(f"CurrentRatioFormatted: {data.get('CurrentRatioFormatted', 'Not found')}")
            print(f"MarketCapFormatted: {data.get('MarketCapFormatted', 'Not found')}")
            print(f"PEGRatioFormatted: {data.get('PEGRatioFormatted', 'Not found')}")
            print(f"ForwardPEFormatted: {data.get('ForwardPEFormatted', 'Not found')}")
            
        except Exception as e:
            print(f"Warning: Error parsing overview data: {e}")
        
        return data, None

    def fetch_balance_sheet(self, ticker):
        """Fetch balance sheet data from Alpha Vantage."""
        params = {
            "function": "BALANCE_SHEET",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "annualReports" not in data or not data["annualReports"]:
            return None, "No balance sheet data found"
        
        # Extract and format intangible assets data
        try:
            latest_report = data["annualReports"][0]
            if 'intangibleAssets' in latest_report:
                # Handle 'None' string values
                if latest_report['intangibleAssets'] == 'None' or latest_report['intangibleAssets'] is None:
                    data['IntangibleAssetsFormatted'] = 'N/A'
                else:
                    intangible_assets = float(latest_report['intangibleAssets'])
                    data['IntangibleAssetsFormatted'] = self._format_number_with_suffix(intangible_assets)
        except Exception as e:
            print(f"Error extracting intangible assets: {e}")
            data['IntangibleAssetsFormatted'] = 'N/A'
        
        return data, None

    def fetch_income_statement(self, ticker):
        """Fetch income statement data"""
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "annualReports" not in data or not data["annualReports"]:
            return None, "No income statement data found"
            
        return data, None

    def fetch_cash_flow(self, ticker):
        """Fetch cash flow data"""
        params = {
            "function": "CASH_FLOW",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "annualReports" not in data or not data["annualReports"]:
            return None, "No cash flow data found"
            
        return data, None

    def fetch_earnings(self, ticker):
        """Fetch earnings data"""
        params = {
            "function": "EARNINGS",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "annualEarnings" not in data or not data["annualEarnings"]:
            return None, "No earnings data found"
            
        return data, None

    def fetch_earnings_calendar(self, ticker=None):
        """Fetch earnings calendar"""
        params = {
            "function": "EARNINGS_CALENDAR",
            "apikey": self.api_key
        }
        
        if ticker:
            params["symbol"] = ticker
            
        data, error = self._make_request(params)
        if error:
            return None, error
            
        return data, None

    def fetch_insider_transactions(self, ticker):
        """Fetch insider transactions data"""
        params = {
            "function": "INSIDER_TRANSACTIONS",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "transactions" not in data or not data["transactions"]:
            return None, "No insider transactions data found"
            
        return data, None

    def fetch_global_quote(self, ticker):
        """Fetch current stock quote"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "Global Quote" not in data or not data["Global Quote"]:
            return None, "No quote data found"
            
        return data["Global Quote"], None

    def fetch_supplementary_data(self, ticker):
        """Fetch additional supplementary data for a stock."""
        try:
            print(f"Fetching supplementary data for {ticker}...")
            
            # Initialize with default values
            supp_data = {
                "52_week_high": "N/A",
                "52_week_low": "N/A",
                "peg_ratio": "N/A",
                "forward_pe": "N/A",
                "operating_margin": "N/A",
                "revenue_per_share": "N/A",
                "enterprise_value": "N/A",
                "current_ratio": "N/A",
                "current_volume": "N/A",
                "average_volume": "N/A",
                "relative_volume": "N/A",
                "short_float": "N/A",
                "float": "N/A"
            }
            
            # Try to get data from overview
            company_overview, error = self.fetch_company_overview(ticker)
            if not error and company_overview:
                # Add float and short float to supplementary data
                if 'Float' in company_overview:
                    supp_data['float'] = company_overview.get('FloatFormatted', 'N/A')
                    
                if 'ShortPercentFloat' in company_overview:
                    try:
                        # Handle 'None' string values
                        if company_overview['ShortPercentFloat'] == 'None' or company_overview['ShortPercentFloat'] is None:
                            supp_data['short_float'] = 'N/A'
                        else:
                            short_float = float(company_overview['ShortPercentFloat']) * 100
                            supp_data['short_float'] = f"{short_float:.2f}%"
                    except (ValueError, TypeError):
                        supp_data['short_float'] = 'N/A'
            
            # Now also gather volume data from global quote
            global_quote, error = self.fetch_global_quote(ticker)
            if not error and global_quote:
                # Store current volume and calculate relative volume
                if "06. volume" in global_quote:
                    try:
                        volume = int(global_quote["06. volume"])
                        supp_data["current_volume"] = f"{volume:,}"
                        
                        # Calculate average and relative volume from time series
                        try:
                            time_series_data, error = self.fetch_time_series_data(ticker, outputsize="compact")
                            if not error and isinstance(time_series_data, pd.DataFrame) and not time_series_data.empty:
                                # Calculate 20-day average volume
                                avg_volume = time_series_data['volume'].rolling(window=20).mean().iloc[-1]
                                rel_volume = volume / avg_volume if avg_volume > 0 else 0
                                supp_data["average_volume"] = f"{avg_volume:,.0f}"
                                supp_data["relative_volume"] = f"{rel_volume:.2f}x"
                        except Exception as e:
                            print(f"Error calculating volume metrics: {e}")
                    except (ValueError, TypeError):
                        # If volume can't be converted to int, leave as N/A
                        pass
            
            return supp_data, None
            
        except Exception as e:
            print(f"Error fetching supplementary data: {str(e)}")
            return None, f"Error fetching supplementary data: {str(e)}"

    def extract_float_value(self, value_str):
        """Extract numerical value from formatted string"""
        if value_str == "N/A" or not value_str:
            return None
        
        value_str = value_str.replace(',', '').replace('%', '')
        match = re.search(r'([-+]?\d*\.\d+|\d+)', value_str)
        if not match:
            return None
        
        value = float(match.group(0))
        
        if 'B' in value_str or 'b' in value_str:
            value *= 1_000_000_000
        elif 'M' in value_str or 'm' in value_str:
            value *= 1_000_000
        elif 'K' in value_str or 'k' in value_str:
            value *= 1_000
        
        return value

    def compile_complete_dataset(self, ticker):
        """Fetch all data for a ticker and compile into a complete dataset"""
        try:
            print(f"Compiling complete dataset for {ticker}...")
            
            # Get time series data
            time_series_data, error = self.fetch_time_series_data(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get company overview
            company_overview, error = self.fetch_company_overview(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get balance sheet data
            balance_sheet, error = self.fetch_balance_sheet(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get income statement data
            income_statement, error = self.fetch_income_statement(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get cash flow data
            cash_flow, error = self.fetch_cash_flow(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get earnings data
            earnings, error = self.fetch_earnings(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get insider transactions
            insider_transactions, error = self.fetch_insider_transactions(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get global quote
            global_quote, error = self.fetch_global_quote(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Get supplementary data
            supplementary_data, error = self.fetch_supplementary_data(ticker)
            if error:
                print(f"Warning: {error}")
                
            # Create the complete dataset
            dataset = {
                'time_series': time_series_data,
                'company_overview': company_overview,
                'balance_sheet': balance_sheet,
                'income_statement': income_statement,
                'cash_flow': cash_flow,
                'earnings': earnings,
                'insider_transactions': insider_transactions,
                'global_quote': global_quote,
                'supplementary_data': supplementary_data
            }
            
            # Calculate additional metrics if we have the necessary data
            self._add_calculated_metrics(dataset)
            
            return dataset, None
            
        except Exception as e:
            print(f"Error compiling dataset: {str(e)}")
            return None, f"Error compiling dataset: {str(e)}"
            
    def _add_calculated_metrics(self, dataset):
        """Add calculated metrics to the dataset based on available data"""
        try:
            # Calculate financial metrics if we have income statement and balance sheet
            income_statement = dataset.get('income_statement', {})
            balance_sheet = dataset.get('balance_sheet', {})
            cash_flow = dataset.get('cash_flow', {})
            
            if income_statement and balance_sheet:
                calculated_metrics = {}
                
                # Get the most recent annual reports
                income_reports = income_statement.get('annualReports', [])
                balance_reports = balance_sheet.get('annualReports', [])
                cash_flow_reports = cash_flow.get('annualReports', []) if cash_flow else []
                
                if income_reports and balance_reports:
                    # Use the most recent data
                    latest_income = income_reports[0]
                    latest_balance = balance_reports[0]
                    latest_cash_flow = cash_flow_reports[0] if cash_flow_reports else None
                    
                    # Helper function to safely convert values
                    def safe_float(value, default=0):
                        if value is None or value == 'None' or value == '':
                            return default
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return default
                    
                    # Calculate additional metrics with safe conversion
                    total_revenue = safe_float(latest_income.get('totalRevenue'))
                    net_income = safe_float(latest_income.get('netIncome'))
                    gross_profit = safe_float(latest_income.get('grossProfit'))
                    total_assets = safe_float(latest_balance.get('totalAssets'))
                    total_liabilities = safe_float(latest_balance.get('totalLiabilities'))
                    total_shareholder_equity = safe_float(latest_balance.get('totalShareholderEquity'))
                    
                    # Only calculate if we have valid denominators
                    if total_revenue > 0:
                        calculated_metrics['profit_margin'] = (net_income / total_revenue) * 100
                        calculated_metrics['gross_margin'] = (gross_profit / total_revenue) * 100
                    
                    if total_assets > 0:
                        calculated_metrics['return_on_assets'] = (net_income / total_assets) * 100
                    
                    if total_shareholder_equity > 0:
                        calculated_metrics['return_on_equity'] = (net_income / total_shareholder_equity) * 100
                        calculated_metrics['debt_to_equity'] = (total_liabilities / total_shareholder_equity)
                    
                    # Cash flow metrics if available
                    if latest_cash_flow:
                        operating_cash_flow = safe_float(latest_cash_flow.get('operatingCashflow'))
                        capital_expenditure = safe_float(latest_cash_flow.get('capitalExpenditures'))
                        
                        if operating_cash_flow != 0:
                            calculated_metrics['free_cash_flow'] = operating_cash_flow + capital_expenditure  # CapEx is negative
                            
                            if total_revenue > 0:
                                calculated_metrics['cash_flow_to_revenue'] = (operating_cash_flow / total_revenue) * 100
                
                    # Add the calculated metrics to the dataset
                    dataset['calculated_metrics'] = calculated_metrics
                
        except Exception as e:
            print(f"Warning: Could not calculate additional metrics: {str(e)}")
            dataset['calculated_metrics'] = {}

    def fetch_stoch_rsi(self, ticker):
        """Fetch Stochastic RSI indicator data from Alpha Vantage"""
        params = {
            "function": "STOCHRSI",
            "symbol": ticker,
            "interval": "daily",
            "time_period": "14",
            "series_type": "close",
            "fastk_period": "5",
            "fastd_period": "3",
            "fastd_matype": "0",
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "Technical Analysis: STOCHRSI" not in data:
            return None, "No Stochastic RSI data found"
            
        # Convert to DataFrame
        try:
            stoch_rsi_data = data["Technical Analysis: STOCHRSI"]
            df = pd.DataFrame.from_dict(stoch_rsi_data, orient='index')
            
            # Convert string values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            # Rename columns
            df.columns = ['stoch_rsi_fastk', 'stoch_rsi_fastd']
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            return df, None
        except Exception as e:
            return None, f"Error processing Stochastic RSI data: {str(e)}"
            
    def fetch_stoch_fast(self, ticker):
        """Fetch Fast Stochastic indicator data from Alpha Vantage"""
        params = {
            "function": "STOCHF",
            "symbol": ticker,
            "interval": "daily",
            "fastkperiod": "5",
            "fastdperiod": "3",
            "fastdmatype": "0",
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "Technical Analysis: STOCHF" not in data:
            return None, "No Fast Stochastic data found"
            
        # Convert to DataFrame
        try:
            stoch_fast_data = data["Technical Analysis: STOCHF"]
            df = pd.DataFrame.from_dict(stoch_fast_data, orient='index')
            
            # Convert string values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            # Rename columns
            df.columns = ['stoch_fastk', 'stoch_fastd']
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            return df, None
        except Exception as e:
            return None, f"Error processing Fast Stochastic data: {str(e)}"
            
    def fetch_apo(self, ticker):
        """Fetch Absolute Price Oscillator indicator data from Alpha Vantage"""
        params = {
            "function": "APO",
            "symbol": ticker,
            "interval": "daily",
            "series_type": "close",
            "fastperiod": "12",
            "slowperiod": "26",
            "matype": "1",
            "apikey": self.api_key
        }
        
        data, error = self._make_request(params)
        if error:
            return None, error
            
        if "Technical Analysis: APO" not in data:
            return None, "No APO data found"
            
        # Convert to DataFrame
        try:
            apo_data = data["Technical Analysis: APO"]
            df = pd.DataFrame.from_dict(apo_data, orient='index')
            
            # Convert string values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            # Rename columns
            df.columns = ['apo']
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            return df, None
        except Exception as e:
            return None, f"Error processing APO data: {str(e)}" 