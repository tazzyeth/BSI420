from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
import re
from flask_sqlalchemy import SQLAlchemy

# Ensure proper import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from modules.data_fetcher import DataFetcher
from modules.visualizer import Visualizer
from models import db, Watchlist
import pandas as pd
import json
import time
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

data_fetcher = DataFetcher()
visualizer = Visualizer()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/analyze')
def analyze_page():
    """Display the analysis page with a pre-filled ticker"""
    ticker = request.args.get('symbol', '')
    return render_template('home.html', ticker=ticker)

@app.route('/watchlist')
def watchlist():
    """Display the watchlist page"""
    return render_template('watchlist.html')

@app.route('/screener')
def screener():
    """Display the stock screener page"""
    return render_template('screener.html')

@app.route('/market/gainers-losers')
def gainers_losers():
    """Redirect to the stock screener page"""
    return redirect(url_for('screener'))

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get all stocks in the watchlist"""
    watchlist_items = Watchlist.query.filter_by(user_id='default_user').all()
    return jsonify([item.to_dict() for item in watchlist_items])

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add a stock to the watchlist"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    
    # Check if already in watchlist
    existing = Watchlist.query.filter_by(user_id='default_user', symbol=symbol).first()
    if existing:
        return jsonify({'status': 'exists', 'message': f'{symbol} is already in your watchlist'})
        
    # Add to watchlist
    new_item = Watchlist(user_id='default_user', symbol=symbol)
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'{symbol} added to watchlist', 'item': new_item.to_dict()})

@app.route('/api/watchlist/remove/<int:item_id>', methods=['DELETE'])
def remove_from_watchlist(item_id):
    """Remove a stock from the watchlist"""
    item = Watchlist.query.get(item_id)
    if not item:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404
        
    symbol = item.symbol
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'{symbol} removed from watchlist'})

@app.route('/api/watchlist/clear', methods=['DELETE'])
def clear_watchlist():
    """Clear all stocks from the watchlist"""
    try:
        # Delete all watchlist items for the default user
        Watchlist.query.filter_by(user_id='default_user').delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Watchlist cleared successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error clearing watchlist: {str(e)}'}), 500

@app.route('/api/watchlist/data', methods=['GET'])
def get_watchlist_data():
    """Get detailed data for all stocks in the watchlist"""
    watchlist_items = Watchlist.query.filter_by(user_id='default_user').all()
    
    # Gather data for all watchlist items
    watchlist_data = []
    for item in watchlist_items:
        # Fetch company data
        dataset, error = data_fetcher.compile_complete_dataset(item.symbol)
        if error:
            watchlist_data.append({
                'id': item.id,
                'symbol': item.symbol,
                'error': error
            })
            continue
            
        # Extract key metrics
        company_overview = dataset.get('company_overview', {})
        supplementary_data = dataset.get('supplementary_data', {})
        balance_sheet = dataset.get('balance_sheet', {})
        
        # Format market cap
        market_cap = 'N/A'
        if company_overview and 'MarketCapitalization' in company_overview:
            market_cap_val = int(company_overview['MarketCapitalization'])
            if market_cap_val >= 1_000_000_000:
                market_cap = f"${market_cap_val / 1_000_000_000:.2f}B"
            elif market_cap_val >= 1_000_000:
                market_cap = f"${market_cap_val / 1_000_000:.2f}M"
            else:
                market_cap = f"${market_cap_val / 1_000:.2f}K"
        
        # Compile stock data
        stock_data = {
            'id': item.id,
            'symbol': item.symbol,
            'name': company_overview.get('Name', 'N/A'),
            'sector': company_overview.get('Sector', 'N/A'),
            'price': dataset.get('global_quote', {}).get('05. price', 'N/A'),
            'change_percent': dataset.get('global_quote', {}).get('10. change percent', 'N/A'),
            'market_cap': market_cap,
            'current_ratio': company_overview.get('CurrentRatio', 'N/A'),
            'institutional_ownership': company_overview.get('PercentInstitutions', 'N/A'),
            'insider_ownership': company_overview.get('PercentInsiders', 'N/A'),
            'current_volume': supplementary_data.get('current_volume', 'N/A'),
            'relative_volume': supplementary_data.get('relative_volume', 'N/A'),
            'short_float': supplementary_data.get('short_float', 'N/A'),
            'float': supplementary_data.get('float', 'N/A')
        }
        
        # Get intangible assets if available
        if balance_sheet and 'annualReports' in balance_sheet and balance_sheet['annualReports']:
            latest_report = balance_sheet['annualReports'][0]
            if 'intangibleAssets' in latest_report:
                intangible_assets = int(latest_report['intangibleAssets'])
                if intangible_assets >= 1_000_000_000:
                    stock_data['intangible_assets'] = f"${intangible_assets / 1_000_000_000:.2f}B"
                elif intangible_assets >= 1_000_000:
                    stock_data['intangible_assets'] = f"${intangible_assets / 1_000_000:.2f}M"
                else:
                    stock_data['intangible_assets'] = f"${intangible_assets / 1_000:.2f}K"
            else:
                stock_data['intangible_assets'] = 'N/A'
        else:
            stock_data['intangible_assets'] = 'N/A'
            
        watchlist_data.append(stock_data)
        
    return jsonify(watchlist_data)

@app.route('/api/gainers-losers', methods=['GET'])
def get_gainers_losers_data():
    """Fetch top gainers and losers data from Alpha Vantage"""
    try:
        # Initialize parameters for API call
        params = {
            "function": "TOP_GAINERS_LOSERS",
            "apikey": data_fetcher.api_key
        }
        
        # Make the API request
        data, error = data_fetcher._make_request(params)
        
        if error:
            return jsonify({"error": error}), 400
            
        if not data or not all(key in data for key in ['top_gainers', 'top_losers', 'most_actively_traded']):
            return jsonify({"error": "Invalid data format received from API"}), 400
        
        # Process the data to include additional fields
        processed_data = {
            'top_gainers': [],
            'top_losers': [],
            'most_active': []
        }
        
        # Process gainers
        for item in data.get('top_gainers', []):
            processed_item = _process_market_movers_item(item)
            processed_data['top_gainers'].append(processed_item)
            
        # Process losers
        for item in data.get('top_losers', []):
            processed_item = _process_market_movers_item(item)
            processed_data['top_losers'].append(processed_item)
            
        # Process most active
        for item in data.get('most_actively_traded', []):
            processed_item = _process_market_movers_item(item)
            processed_data['most_active'].append(processed_item)
        
        return jsonify(processed_data)
        
    except Exception as e:
        print(f"Error fetching gainers/losers data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def _process_market_movers_item(item):
    """Process a market mover item to add formatted fields"""
    processed = item.copy()
    
    # Format change amount
    if 'change_amount' in item:
        try:
            change_float = float(item['change_amount'])
            processed['change_formatted'] = f"{change_float:+.2f}"
        except (ValueError, TypeError):
            processed['change_formatted'] = item['change_amount']
    
    # Format change percentage
    if 'change_percentage' in item:
        try:
            # Remove % character if present
            pct_str = item['change_percentage'].replace('%', '')
            pct_float = float(pct_str)
            processed['change_pct_formatted'] = f"{pct_float:+.2f}%"
        except (ValueError, TypeError, AttributeError):
            processed['change_pct_formatted'] = item['change_percentage']
    
    # Format volume
    if 'volume' in item:
        try:
            volume = int(item['volume'])
            if volume >= 1_000_000:
                processed['volume_formatted'] = f"{volume / 1_000_000:.2f}M"
            elif volume >= 1_000:
                processed['volume_formatted'] = f"{volume / 1_000:.2f}K"
            else:
                processed['volume_formatted'] = f"{volume}"
        except (ValueError, TypeError):
            processed['volume_formatted'] = item['volume']
    
    return processed

def extract_float_value(value_str):
    """Extract numerical value from formatted string"""
    if value_str == "N/A" or value_str == "None" or not value_str:
        return 0
    
    if isinstance(value_str, (int, float)):
        return float(value_str)
        
    # Handle string values
    if isinstance(value_str, str):
        value_str = value_str.replace(',', '').replace('%', '')
        match = re.search(r'([-+]?\d*\.\d+|\d+)', value_str)
        if match:
            return float(match.group(0))
    
    return 0

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form.get('ticker', '').upper()
    # Always set use_mock to False, ignoring whatever was passed
    use_mock = False
    disable_charts = request.form.get('disable_charts', 'false').lower() == 'true'
    
    try:
        print(f"Starting analysis for ticker: {ticker} (mock: {use_mock}, disable_charts: {disable_charts})")
        
        if not ticker:
            return jsonify({'error': 'No ticker symbol provided'})
        
        # Use the comprehensive dataset compiler
        dataset, error = data_fetcher.compile_complete_dataset(ticker)
        if error:
            print(f"Error compiling dataset: {error}")
            return jsonify({
                'error': error,
                'company_data': {
                    'name': ticker,
                    'description': f"Error retrieving data: {error}"
                },
                'charts': {}
            })
        
        # Check if we have time series data, which is essential
        time_series_data = dataset.get('time_series')
        if not isinstance(time_series_data, pd.DataFrame) or time_series_data.empty:
            print("Empty time series data received")
            return jsonify({
                'error': 'No time series data found',
                'company_data': {
                    'name': ticker,
                    'description': "No price history data available for this ticker."
                },
                'charts': {}
            })
        
        # Extract supplementary data
        company_overview = dataset.get('company_overview', {})
        supplementary_data = dataset.get('supplementary_data', {})
        balance_sheet = dataset.get('balance_sheet', {})
        income_statement = dataset.get('income_statement', {})
        insider_transactions = dataset.get('insider_transactions', {})
        global_quote = dataset.get('global_quote', {})
        
        # Initialize data dictionary with enhanced structure
        data = {
            'price_data': time_series_data,
            'financial_data': {},
            'market_data': {},
            'insider_data': {'transactions': []},
            'calculated_metrics': {},
            'ownership_data': {}
        }
        
        # Process company overview data
        if company_overview and isinstance(company_overview, dict):
            # Extract financial metrics with safe conversion
            data['financial_data'] = {
                'current_ratio': extract_float_value(company_overview.get('CurrentRatio', 0)),
                'current_ratio_formatted': company_overview.get('CurrentRatioFormatted', 'N/A'),
                'debt_to_equity': extract_float_value(company_overview.get('DebtToEquityRatio', 0)),
                'profit_margin': extract_float_value(company_overview.get('ProfitMargin', 0)),
                'roe': extract_float_value(company_overview.get('ReturnOnEquityTTM', 0)),
                'eps': extract_float_value(company_overview.get('EPS', 0)),
                'pe_ratio': extract_float_value(company_overview.get('PERatio', 0)),
                'beta': extract_float_value(company_overview.get('Beta', 0)),
                'dividend_yield': extract_float_value(company_overview.get('DividendYield', 0)),
                'market_cap': extract_float_value(company_overview.get('MarketCapitalization', 0)),
                'market_cap_formatted': company_overview.get('MarketCapFormatted', 'N/A')
            }
            
            # Extract ownership data
            data['ownership_data'] = {
                'insider_ownership': company_overview.get('InsiderOwnership', 'N/A'),
                'institutional_ownership': company_overview.get('InstitutionalOwnership', 'N/A'),
                'float': company_overview.get('FloatFormatted', 'N/A'),
                'shares_outstanding': company_overview.get('SharesOutstanding', 'N/A')
            }
            
            # Add market cap formatted value
            if 'MarketCapFormatted' in company_overview:
                data['financial_data']['market_cap_formatted'] = company_overview['MarketCapFormatted']
            
            # Add ownership data
            if 'InstitutionalOwnership' in company_overview:
                data['financial_data']['institutional_ownership'] = company_overview['InstitutionalOwnership']
                
            if 'InsiderOwnership' in company_overview:
                data['financial_data']['insider_ownership'] = company_overview['InsiderOwnership']
            
            # Add float data
            if 'FloatFormatted' in company_overview:
                data['financial_data']['float'] = company_overview['FloatFormatted']
            
            # Add current ratio
            if 'CurrentRatioFormatted' in company_overview:
                data['financial_data']['current_ratio_formatted'] = company_overview['CurrentRatioFormatted']
            
            # If company_overview contains pre-formatted values, use them directly
            if 'ProfitMargin' in company_overview and isinstance(company_overview['ProfitMargin'], str) and '%' in company_overview['ProfitMargin']:
                data['financial_data']['profit_margin_formatted'] = company_overview['ProfitMargin']
                
            if 'ReturnOnEquityTTM' in company_overview and isinstance(company_overview['ReturnOnEquityTTM'], str) and '%' in company_overview['ReturnOnEquityTTM']:
                data['financial_data']['roe_formatted'] = company_overview['ReturnOnEquityTTM']
                
            if 'GrossMargin' in company_overview:
                data['financial_data']['gross_margin'] = company_overview['GrossMargin']
                
            # Direct copy of 52-week range if available
            if '52WeekRange' in company_overview:
                data['market_data']['52_week_range'] = company_overview['52WeekRange']
        
        # Process financial metrics from calculated metrics
        if 'calculated_metrics' in dataset and isinstance(dataset['calculated_metrics'], dict):
            calculated = dataset['calculated_metrics']
            data['financial_data'].update({
                'profit_margin': calculated.get('profit_margin', 0),
                'gross_margin': calculated.get('gross_margin', 0),
                'return_on_assets': calculated.get('return_on_assets', 0),
                'return_on_equity': calculated.get('return_on_equity', 0),
                'debt_to_equity': calculated.get('debt_to_equity', 0),
                'free_cash_flow': calculated.get('free_cash_flow', 0),
                'cash_flow_to_revenue': calculated.get('cash_flow_to_revenue', 0)
            })
        
        # Process supplementary data
        if supplementary_data and isinstance(supplementary_data, dict):
            # Add volume metrics
            if 'current_volume' in supplementary_data:
                data['market_data']['current_volume'] = supplementary_data['current_volume']
                
            if 'average_volume' in supplementary_data:
                data['market_data']['average_volume'] = supplementary_data['average_volume']
                
            if 'relative_volume' in supplementary_data:
                data['market_data']['relative_volume'] = supplementary_data['relative_volume']
                
            # Add 52-week high/low data
            if '52_week_high' in supplementary_data:
                data['market_data']['52_week_high'] = supplementary_data['52_week_high']
                
            if '52_week_low' in supplementary_data:
                data['market_data']['52_week_low'] = supplementary_data['52_week_low']
            
            # Add ownership metrics
            if 'short_float' in supplementary_data:
                data['ownership_data']['short_float'] = supplementary_data['short_float']
                data['financial_data']['short_float'] = supplementary_data['short_float']
                
            if 'float' in supplementary_data:
                data['ownership_data']['float'] = supplementary_data['float']
            
            # Add other supplementary financial metrics
            data['financial_data'].update({
                'peg_ratio': supplementary_data.get('peg_ratio', 'N/A'),
                'forward_pe': supplementary_data.get('forward_pe', 'N/A'),
                'operating_margin': supplementary_data.get('operating_margin', 'N/A'),
                'revenue_per_share': supplementary_data.get('revenue_per_share', 'N/A'),
                'enterprise_value': supplementary_data.get('enterprise_value', 'N/A'),
                'current_ratio': supplementary_data.get('current_ratio', data['financial_data'].get('current_ratio', 'N/A')),
                'cash_flow_to_revenue': data['financial_data'].get('cash_flow_to_revenue', 'N/A')
            })
        
        # Process balance sheet data for intangible assets and other balance sheet metrics
        if balance_sheet and isinstance(balance_sheet, dict):
            data['financial_data']['intangible_assets'] = balance_sheet.get('IntangibleAssetsFormatted', 'N/A')
            
            # Add additional balance sheet metrics if available
            if 'annualReports' in balance_sheet and balance_sheet['annualReports']:
                latest_report = balance_sheet['annualReports'][0]
                # Format values for display
                for key in ['totalAssets', 'totalLiabilities', 'totalShareholderEquity', 'longTermDebt']:
                    if key in latest_report:
                        # Format key for display (e.g., totalAssets -> TotalAssets)
                        formatted_key = key[0].upper() + key[1:]
                        try:
                            value = float(latest_report[key])
                            data['financial_data'][formatted_key] = format_number_with_suffix(value)
                        except (ValueError, TypeError):
                            data['financial_data'][formatted_key] = 'N/A'
        
        # Process market data from global quote
        if global_quote and isinstance(global_quote, dict):
            data['market_data'] = {
                'price': global_quote.get('05. price', 'N/A'),
                'change': global_quote.get('09. change', 'N/A'),
                'change_percent': global_quote.get('10. change percent', 'N/A'),
                'volume': global_quote.get('06. volume', 'N/A'),
                'previous_close': global_quote.get('08. previous close', 'N/A')
            }
        
        # Process insider transactions
        if insider_transactions and isinstance(insider_transactions, dict) and 'transactions' in insider_transactions:
            transactions = insider_transactions['transactions']
            if transactions:
                # Sort by date (most recent first)
                sorted_transactions = sorted(transactions, 
                                           key=lambda x: x.get('transactionDate', ''), 
                                           reverse=True)
                
                # Get last 10 transactions
                recent_transactions = sorted_transactions[:10]
                
                # Count buys and sells
                buys = sum(1 for t in recent_transactions if t.get('transactionType', '').lower() == 'buy')
                sells = sum(1 for t in recent_transactions if t.get('transactionType', '').lower() == 'sell')
                
                data['insider_data'] = {
                    'transactions': recent_transactions,
                    'summary': {
                        'recent_transactions': len(recent_transactions),
                        'buys': buys,
                        'sells': sells,
                        'buy_sell_ratio': f"{buys/sells:.2f}" if sells > 0 else "∞"
                    }
                }
        
        # Create visualizations with proper error handling
        chart_json = {}
        try:
            if not disable_charts:
                # Prepare charts with more detailed error handling
                charts = {}
                
                # Helper function to safely create chart
                def safe_create_chart(create_func, data):
                    try:
                        return create_func(data)
                    except Exception as e:
                        print(f"Error creating chart with {create_func.__name__}: {str(e)}")
                        return None
                
                # Create each chart with error handling
                charts['summary'] = safe_create_chart(visualizer.create_summary_chart, data)
                charts['price'] = safe_create_chart(visualizer.create_price_chart, time_series_data)
                charts['technical'] = safe_create_chart(visualizer.create_technical_chart, time_series_data)
                charts['volume'] = safe_create_chart(visualizer.create_volume_chart, time_series_data)
                charts['financial'] = safe_create_chart(visualizer.create_financial_chart, data['financial_data'])
                
                # Convert charts to JSON with proper error handling for each chart
                for key, chart in charts.items():
                    if chart:
                        try:
                            # Convert to JSON string first for validation
                            chart_json_str = chart.to_json()
                            
                            # Print debugging info
                            print(f"Chart {key} JSON length: {len(chart_json_str)}")
                            if len(chart_json_str) > 1000:
                                print(f"Chart {key} JSON snippet: {chart_json_str[:100]}...")
                            else:
                                print(f"Chart {key} JSON: {chart_json_str}")
                            
                            # Verify it's valid JSON by parsing it
                            chart_data = json.loads(chart_json_str)
                            
                            # Print the structure of the chart data for debugging
                            print(f"Chart {key} data structure: {'data' in chart_data}, {'layout' in chart_data}")
                            if 'data' in chart_data:
                                print(f"Chart {key} data length: {len(chart_data['data'])}")
                            if 'layout' in chart_data:
                                print(f"Chart {key} layout keys: {', '.join(chart_data['layout'].keys() if isinstance(chart_data['layout'], dict) else 'Not a dict')}")
                            
                            # Store in the response dictionary
                            chart_json[key] = chart_data
                        except Exception as e:
                            print(f"Error converting chart {key} to JSON: {str(e)}")
                            # Continue with other charts instead of failing
                    else:
                        print(f"No chart data for {key} chart")
            else:
                print("Charts disabled by user request")
        except Exception as e:
            print(f"Error creating visualizations: {str(e)}")
            print(traceback.format_exc())
        
        # Prepare company data with enhanced information
        company_data = {
            'name': company_overview.get('Name', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'description': company_overview.get('Description', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'sector': company_overview.get('Sector', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'industry': company_overview.get('Industry', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'market_cap': company_overview.get('MarketCapFormatted', company_overview.get('MarketCapitalization', 'N/A')) if company_overview and isinstance(company_overview, dict) else 'N/A',
            'pe_ratio': company_overview.get('PERatio', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'eps': company_overview.get('EPS', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'dividend_yield': company_overview.get('DividendYield', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'beta': company_overview.get('Beta', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            '52_week_high': supplementary_data.get('52_week_high', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A',
            '52_week_low': supplementary_data.get('52_week_low', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A',
            'insider_activity': data['insider_data']['summary'] if 'summary' in data['insider_data'] else None,
            
            # Additional metrics from calculations with formatted display
            'profit_margin': data['financial_data'].get('profit_margin_formatted', 
                                                      data['financial_data'].get('profit_margin', 'N/A')),
            'gross_margin': data['financial_data'].get('gross_margin', 'N/A'),
            'revenue_per_share': supplementary_data.get('revenue_per_share', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A',
            'return_on_equity': data['financial_data'].get('roe_formatted', 
                                                         data['financial_data'].get('return_on_equity', 'N/A')),
            'return_on_assets': data['financial_data'].get('return_on_assets', 'N/A'),
            'operating_margin': supplementary_data.get('operating_margin', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A',
            'free_cash_flow': data['financial_data'].get('free_cash_flow', 'N/A'),
            'peg_ratio': company_overview.get('PEGRatioFormatted', supplementary_data.get('peg_ratio', 'N/A')) if company_overview and isinstance(company_overview, dict) else (supplementary_data.get('peg_ratio', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A'),
            'forward_pe': company_overview.get('ForwardPEFormatted', supplementary_data.get('forward_pe', 'N/A')) if company_overview and isinstance(company_overview, dict) else (supplementary_data.get('forward_pe', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A'),
            'current_ratio': data['financial_data'].get('current_ratio_formatted', 
                                                     str(data['financial_data'].get('current_ratio', supplementary_data.get('current_ratio', 'N/A')))),
            'current_volume': data['market_data'].get('current_volume', 'N/A'),
            'average_volume': data['market_data'].get('average_volume', 'N/A'),
            'relative_volume': data['market_data'].get('relative_volume', 'N/A'),
            
            # Ownership metrics
            'intangible_assets': data['financial_data'].get('intangible_assets', 'N/A'),
            'insider_ownership': company_overview.get('InsiderOwnership', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'institutional_ownership': company_overview.get('InstitutionalOwnership', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'float': company_overview.get('FloatFormatted', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'short_float': supplementary_data.get('short_float', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A',
            
            # Additional balance sheet metrics
            'total_assets': data['financial_data'].get('TotalAssets', 'N/A'),
            'total_liabilities': data['financial_data'].get('TotalLiabilities', 'N/A'),
            'shareholder_equity': data['financial_data'].get('TotalShareholderEquity', 'N/A'),
            'long_term_debt': data['financial_data'].get('LongTermDebt', 'N/A'),
            
            # Cash flow metrics
            'cash_flow_to_revenue': data['financial_data'].get('cash_flow_to_revenue', 'N/A'),
            
            # Enterprise value
            'enterprise_value': data['financial_data'].get('enterprise_value', 
                                                        supplementary_data.get('enterprise_value', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A'),
            
            # Debt to equity ratio
            'debt_to_equity': data['financial_data'].get('debt_to_equity', 'N/A'),
            
            # Add explicit fields for frontend with different naming
            'marketCap': company_overview.get('MarketCapFormatted', company_overview.get('MarketCapitalization', 'N/A')) if company_overview and isinstance(company_overview, dict) else 'N/A',
            'institutionalOwnership': company_overview.get('InstitutionalOwnership', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'insiderOwnership': company_overview.get('InsiderOwnership', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A',
            'currentRatio': data['financial_data'].get('current_ratio_formatted', str(data['financial_data'].get('current_ratio', 'N/A'))),
            'intangibleAssets': balance_sheet.get('IntangibleAssetsFormatted', 'N/A') if balance_sheet and isinstance(balance_sheet, dict) else 'N/A',
            'pegRatio': company_overview.get('PEGRatioFormatted', supplementary_data.get('peg_ratio', 'N/A')) if company_overview and isinstance(company_overview, dict) else (supplementary_data.get('peg_ratio', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A'),
            'forwardPE': company_overview.get('ForwardPEFormatted', supplementary_data.get('forward_pe', 'N/A')) if company_overview and isinstance(company_overview, dict) else (supplementary_data.get('forward_pe', 'N/A') if supplementary_data and isinstance(supplementary_data, dict) else 'N/A'),
            'dividendYield': company_overview.get('DividendYield', 'N/A') if company_overview and isinstance(company_overview, dict) else 'N/A'
        }
        
        # Print debug information for fields we're having trouble with
        print("\nDEBUG - Key fields values:")
        print(f"EPS: {company_data['eps']}")
        print(f"PEG Ratio: {company_data['pegRatio']}")
        print(f"Forward P/E: {company_data['forwardPE']}")
        print(f"Dividend Yield: {company_data['dividendYield']}")
        print(f"Market Cap: {company_data['marketCap']}")
        print(f"Current Ratio: {company_data['currentRatio']}")
        print(f"Float: {company_data['float']}")
        print(f"Short Float: {company_data['short_float']}")
        print(f"Institutional Ownership: {company_data['institutionalOwnership']}")
        print(f"Insider Ownership: {company_data['insiderOwnership']}")
        print(f"Intangible Assets: {company_data['intangibleAssets']}")
        
        # Check raw data sources for the fields we're having trouble with
        print("\nDEBUG - Raw data sources:")
        if company_overview and isinstance(company_overview, dict):
            print(f"PERatio in company_overview: {company_overview.get('PERatio', 'Not found')}")
            print(f"EPS in company_overview: {company_overview.get('EPS', 'Not found')}")
            print(f"DividendYield in company_overview: {company_overview.get('DividendYield', 'Not found')}")
            print(f"InsiderOwnership in company_overview: {company_overview.get('InsiderOwnership', 'Not found')}")
            print(f"InstitutionalOwnership in company_overview: {company_overview.get('InstitutionalOwnership', 'Not found')}")
            print(f"FloatFormatted in company_overview: {company_overview.get('FloatFormatted', 'Not found')}")
            
        if supplementary_data and isinstance(supplementary_data, dict):
            print(f"peg_ratio in supplementary_data: {supplementary_data.get('peg_ratio', 'Not found')}")
            print(f"forward_pe in supplementary_data: {supplementary_data.get('forward_pe', 'Not found')}")
            print(f"short_float in supplementary_data: {supplementary_data.get('short_float', 'Not found')}")
        
        if balance_sheet and isinstance(balance_sheet, dict):
            print(f"IntangibleAssetsFormatted in balance_sheet: {balance_sheet.get('IntangibleAssetsFormatted', 'Not found')}")
        
        if 'financial_data' in data:
            print(f"current_ratio_formatted in financial_data: {data['financial_data'].get('current_ratio_formatted', 'Not found')}")
        
        # If we have high and low but no range, create the range
        if 'market_data' in data and '52_week_range' not in data['market_data'] and company_data['52_week_high'] != 'N/A' and company_data['52_week_low'] != 'N/A':
            try:
                company_data['52_week_range'] = f"{company_data['52_week_low']} - {company_data['52_week_high']}"
            except Exception as e:
                print(f"Error creating 52-week range: {e}")
                company_data['52_week_range'] = 'N/A'
        else:
            # Ensure the field exists in the response
            if '52_week_range' not in company_data:
                company_data['52_week_range'] = 'N/A'
        
        # If we have market data from global quote, use it
        if 'market_data' in data and data['market_data']:
            current_price = data['market_data'].get('price', 'N/A')
            daily_change = data['market_data'].get('change', 'N/A')
            daily_change_pct = data['market_data'].get('change_percent', 'N/A')
            
            company_data.update({
                'current_price': current_price,
                'daily_change': daily_change,
                'daily_change_pct': daily_change_pct
            })
        
        # Prepare the final response
        response_data = {
            'charts': chart_json,
            'company_data': company_data
        }
        
        # Helper function to make sure data is JSON serializable
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(i) for i in obj]
            elif isinstance(obj, (int, float)):
                return obj
            elif obj is None:
                return None
            else:
                # Convert any other types to strings
                return str(obj)
        
        # Make sure the response is JSON serializable
        try:
            # Clean up the data first
            response_data['company_data'] = clean_for_json(response_data['company_data'])
            
            # Test serialization before returning
            json.dumps(response_data)
            return jsonify(response_data)
        except Exception as e:
            print(f"Error serializing response: {str(e)}")
            # Return a simplified response that will definitely serialize
            return jsonify({
                'error': f'Error serializing response: {str(e)}',
                'company_data': {
                    'name': company_data.get('name', ticker),
                    'description': company_data.get('description', 'Data retrieved but could not be displayed properly.')
                },
                'charts': {}
            })
        
    except Exception as e:
        print(f"Unexpected error in analyze route: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Error processing request: {str(e)}',
            'company_data': {
                'name': ticker,
                'description': f"An unexpected error occurred: {str(e)}"
            },
            'charts': {}
        })

def format_number_with_suffix(number):
    """Format large numbers with K, M, B suffixes"""
    if number >= 1_000_000_000:
        return f"${number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"${number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"${number / 1_000:.2f}K"
    else:
        return f"${number:.2f}"

if __name__ == '__main__':
    app.run(debug=True) 