import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import re

class Visualizer:
    def __init__(self):
        self.colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }

    def create_price_chart(self, df):
        """Create price history chart with candlesticks and volume"""
        if not isinstance(df, pd.DataFrame) or df.empty:
            return None

        # Create subplots: 2 rows, 1 column, shared x-axis
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, 
                           row_heights=[0.7, 0.3],
                           subplot_titles=('Price History', 'Volume'))

        # Add moving averages if available
        has_ma = 'MA20' in df.columns and 'MA50' in df.columns
        
        # Candlestick chart for price history
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color=self.colors['success'],  # Green for increasing
            decreasing_line_color=self.colors['danger'],   # Red for decreasing
        ), row=1, col=1)
        
        # Add moving averages to the price chart
        if has_ma:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MA20'],
                name='20-day MA',
                line=dict(color='rgba(66, 133, 244, 0.7)', width=1)
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MA50'],
                name='50-day MA',
                line=dict(color='rgba(219, 68, 55, 0.7)', width=1)
            ), row=1, col=1)
        
        # Add Bollinger Bands if available
        if 'upper_band' in df.columns and 'lower_band' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['upper_band'],
                name='Upper BB',
                line=dict(color='rgba(173, 216, 230, 0.7)', width=1, dash='dash'),
                showlegend=True
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['lower_band'],
                name='Lower BB',
                line=dict(color='rgba(173, 216, 230, 0.7)', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(173, 216, 230, 0.1)',
                showlegend=True
            ), row=1, col=1)

        # Volume bars for volume history - color based on price change
        colors = ['green' if row['close'] >= row['open'] else 'red' 
                 for index, row in df.iterrows()]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            marker_line_width=0,
            opacity=0.7
        ), row=2, col=1)
        
        # Add moving average for volume if available
        if 'avg_volume' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['avg_volume'],
                name='Avg Volume',
                line=dict(color='black', width=1)
            ), row=2, col=1)

        # Calculate price statistics for the annotation
        if not df.empty:
            current_price = df['close'].iloc[-1]
            price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
            price_change_pct = (price_change / df['close'].iloc[-2]) * 100
            fifty_day_avg = df['MA50'].iloc[-1] if has_ma else None
            
            # Add annotation with price info
            annotation_text = f"Current: ${current_price:.2f}<br>"
            annotation_text += f"Change: ${price_change:.2f} ({price_change_pct:.2f}%)<br>"
            if fifty_day_avg:
                annotation_text += f"50-day MA: ${fifty_day_avg:.2f}"
                
            fig.add_annotation(
                x=0.05,
                y=0.95,
                xref="paper",
                yref="paper",
                text=annotation_text,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="black",
                borderwidth=1,
                borderpad=4,
                font=dict(size=10),
                align="left"
            )

        # Update layout for better appearance
        fig.update_layout(
            title='Price History with Volume',
            yaxis_title='Price',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False,
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=60, t=80, b=40)
        )
        
        # Make price axis more readable
        fig.update_yaxes(
            tickprefix='$',
            showgrid=True,
            gridwidth=0.2,
            gridcolor='lightgray',
            row=1, col=1
        )
        
        # Add button for timeframe selection
        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(
                            args=[{'visible': [True, True, True, True, True, True]}],
                            label="All Data",
                            method="update"
                        ),
                        dict(
                            args=[{'xaxis.range': [df.index[-90], df.index[-1]]}],
                            label="3 Months",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df.index[-30], df.index[-1]]}],
                            label="1 Month",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df.index[-7], df.index[-1]]}],
                            label="1 Week",
                            method="relayout"
                        ),
                    ]),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                ),
            ]
        )

        return fig

    def create_technical_chart(self, df):
        """Create technical indicators chart with enhanced indicators"""
        if not isinstance(df, pd.DataFrame) or df.empty:
            return None

        # Create figure with multiple subplots
        fig = make_subplots(rows=4, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           row_heights=[0.4, 0.2, 0.2, 0.2],
                           subplot_titles=('Price & Moving Averages', 'RSI/StochRSI', 'MACD', 'Volume'))

        # Price and moving averages
        fig.add_trace(go.Scatter(
            x=df.index, y=df['close'],
            name='Price',
            line=dict(color=self.colors['primary'], width=1.5)
        ), row=1, col=1)

        # Add moving averages if available
        if 'MA20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA20'],
                name='20-day MA',
                line=dict(color=self.colors['success'], width=1)
            ), row=1, col=1)

        if 'MA50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA50'],
                name='50-day MA',
                line=dict(color=self.colors['warning'], width=1)
            ), row=1, col=1)
            
        if 'MA200' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA200'],
                name='200-day MA',
                line=dict(color=self.colors['danger'], width=1)
            ), row=1, col=1)
        
        # Add Bollinger Bands if available
        if 'upper_band' in df.columns and 'lower_band' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['upper_band'],
                name='Upper BB',
                line=dict(color='rgba(173, 216, 230, 0.7)', width=1, dash='dash')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['lower_band'],
                name='Lower BB',
                line=dict(color='rgba(173, 216, 230, 0.7)', width=1, dash='dash'),
                fill='tonexty'
            ), row=1, col=1)

        # RSI or StochRSI in second row
        if 'fastk' in df.columns and 'fastd' in df.columns:
            # Use StochRSI if available
            fig.add_trace(go.Scatter(
                x=df.index, y=df['fastk'],
                name='FastK',
                line=dict(color=self.colors['primary'])
            ), row=2, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['fastd'],
                name='FastD',
                line=dict(color=self.colors['danger'])
            ), row=2, col=1)
            
            fig.update_yaxes(title_text="StochRSI", row=2, col=1)
        elif 'RSI' in df.columns:
            # Fallback to RSI if StochRSI not available
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI'],
                name='RSI',
                line=dict(color=self.colors['primary'])
            ), row=2, col=1)
            
            fig.update_yaxes(title_text="RSI", row=2, col=1)
        
        # Add reference lines for RSI/StochRSI
        fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=1, row=2, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=1, row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="gray", line_width=1, row=2, col=1)

        # MACD in third row
        if 'MACD' in df.columns and 'MACD_signal' in df.columns and 'MACD_hist' in df.columns:
            # MACD Line
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD'],
                name='MACD',
                line=dict(color=self.colors['primary'])
            ), row=3, col=1)
            
            # Signal Line
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD_signal'],
                name='Signal',
                line=dict(color=self.colors['danger'])
            ), row=3, col=1)
            
            # Histogram
            colors = ['green' if val >= 0 else 'red' for val in df['MACD_hist'].fillna(0)]
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_hist'],
                name='Histogram',
                marker_color=colors
            ), row=3, col=1)
            
            fig.update_yaxes(title_text="MACD", row=3, col=1)
        elif 'apo' in df.columns:
            # APO if MACD not available
            fig.add_trace(go.Scatter(
                x=df.index, y=df['apo'],
                name='APO',
                line=dict(color=self.colors['primary'])
            ), row=3, col=1)
            
            # Add zero line
            fig.add_hline(y=0, line_dash="solid", line_color="gray", line_width=1, row=3, col=1)
            
            fig.update_yaxes(title_text="APO", row=3, col=1)

        # Volume with relative volume in fourth row
        if 'volume' in df.columns:
            colors = ['green' if df['close'].iloc[i] >= (df['close'].iloc[i-1] if i > 0 else df['close'].iloc[0]) 
                    else 'red' for i in range(len(df))]
            
            fig.add_trace(go.Bar(
                x=df.index, y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ), row=4, col=1)
            
            if 'avg_volume' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['avg_volume'],
                    name='Avg Volume',
                    line=dict(color='black', width=1)
                ), row=4, col=1)
            
            fig.update_yaxes(title_text="Volume", row=4, col=1)

        # Update layout for better appearance
        fig.update_layout(
            title='Technical Analysis',
            height=800,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=60, t=80, b=40)
        )
        
        # Suppress auto-ranging on price chart
        last_month = df.iloc[-30:] if len(df) > 30 else df
        y_min = last_month['low'].min() * 0.98
        y_max = last_month['high'].max() * 1.02
        fig.update_yaxes(range=[y_min, y_max], row=1, col=1)
        
        # Make axis more readable
        fig.update_xaxes(
            rangeslider_visible=False,
            showgrid=True,
            gridwidth=0.2,
            gridcolor='lightgray'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=0.2,
            gridcolor='lightgray'
        )

        return fig

    def create_volume_chart(self, df):
        """Create volume analysis chart"""
        if not isinstance(df, pd.DataFrame) or df.empty:
            return None

        # Calculate relative volume
        df['avg_volume'] = df['volume'].rolling(window=20).mean()
        df['relative_volume'] = df['volume'] / df['avg_volume']

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.5, 0.5])

        # Volume bars
        colors = ['red' if row['close'] < row['open'] else 'green' 
                 for index, row in df.iterrows()]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker_color=colors
        ), row=1, col=1)

        # Average volume line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['avg_volume'],
            name='20-day Average',
            line=dict(color=self.colors['primary'])
        ), row=1, col=1)

        # Relative volume
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['relative_volume'],
            name='Relative Volume',
            marker_color=self.colors['info']
        ), row=2, col=1)

        fig.update_layout(
            title='Volume Analysis',
            height=600,
            showlegend=True
        )

        return fig

    def _extract_float_from_string(self, value):
        """Extract float value from string that may contain % or other characters"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if not isinstance(value, str) or value == 'N/A':
            return 0.0
            
        # Extract number portion using regex
        match = re.search(r'([-+]?\d*\.?\d+)', value.replace(',', ''))
        if match:
            extracted = float(match.group(1))
            # If it's a percentage, convert to decimal
            if '%' in value:
                return extracted
            return extracted
        return 0.0

    def create_financial_chart(self, financial_data):
        """Create financial metrics chart"""
        if not financial_data or not isinstance(financial_data, dict):
            return None

        # Extract metrics with safe conversion
        metrics = {
            'Current Ratio': self._extract_float_from_string(financial_data.get('current_ratio', 0)),
            'Debt to Equity': self._extract_float_from_string(financial_data.get('debt_to_equity', 0)),
            'Profit Margin': self._extract_float_from_string(financial_data.get('profit_margin', 0)),
            'ROE': self._extract_float_from_string(financial_data.get('roe', 0))
        }

        fig = go.Figure(data=[
            go.Bar(
                x=list(metrics.keys()),
                y=list(metrics.values()),
                marker_color=self.colors['primary']
            )
        ])

        fig.update_layout(
            title='Financial Metrics',
            height=400,
            showlegend=False
        )

        return fig

    def create_ownership_chart(self, ownership_data):
        """Create ownership structure chart"""
        if not ownership_data or not isinstance(ownership_data, dict):
            return None

        # Extract ownership percentages with safe conversion
        institutional = self._extract_float_from_string(ownership_data.get('institutional_ownership', 0))
        insider = self._extract_float_from_string(ownership_data.get('insider_ownership', 0))
        
        # Ensure values are reasonable percentages
        institutional = min(institutional, 100)
        insider = min(insider, 100)
        
        # Calculate public float, ensuring we don't go negative
        public = max(0, 100 - (institutional + insider))

        labels = ['Institutional', 'Insider', 'Public']
        values = [institutional, insider, public]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker_colors=[self.colors['primary'], self.colors['success'], self.colors['info']]
        )])

        fig.update_layout(
            title='Ownership Structure',
            height=400,
            showlegend=True
        )

        return fig

    def create_insider_chart(self, insider_data):
        """Create insider activity chart"""
        if not insider_data or 'transactions' not in insider_data:
            return None

        # Process insider transactions
        transactions = insider_data['transactions']
        df = pd.DataFrame(transactions)
        
        if df.empty:
            return None

        # Count buys and sells
        buy_count = len(df[df['transactionType'].str.lower() == 'buy'])
        sell_count = len(df[df['transactionType'].str.lower() == 'sell'])

        fig = go.Figure(data=[
            go.Bar(
                x=['Buys', 'Sells'],
                y=[buy_count, sell_count],
                marker_color=[self.colors['success'], self.colors['danger']]
            )
        ])

        fig.update_layout(
            title='Recent Insider Activity',
            height=400,
            showlegend=False
        )

        return fig

    def create_summary_chart(self, data):
        """Create summary dashboard chart"""
        if not data or not isinstance(data, dict):
            return None

        # Create a figure with multiple subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Price History', 'Volume', 'Price Performance', 'Financial Metrics'),
            specs=[[{"type": "candlestick"}, {"type": "bar"}],
                  [{"type": "scatter"}, {"type": "bar"}]]
        )

        # Add price history
        if 'price_data' in data and isinstance(data['price_data'], pd.DataFrame):
            df = data['price_data']
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price'
            ), row=1, col=1)

            # Add volume
            colors = ['green' if row['close'] >= row['open'] else 'red' 
                     for index, row in df.iterrows()]
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color=colors
            ), row=1, col=2)
            
            # Add price performance chart (instead of ownership)
            # Calculate daily returns
            if len(df) > 20:
                # Get the last 30 days of data
                recent_df = df.iloc[-30:]
                
                # Calculate daily returns
                if 'daily_return' not in recent_df.columns:
                    recent_df['daily_return'] = recent_df['close'].pct_change() * 100
                
                # Plot cumulative performance
                base = 100
                cumulative = [base]
                for ret in recent_df['daily_return'].fillna(0).values[1:]:
                    cumulative.append(cumulative[-1] * (1 + ret/100))
                
                fig.add_trace(go.Scatter(
                    x=recent_df.index,
                    y=cumulative,
                    name='30-Day Performance',
                    line=dict(color=self.colors['primary'], width=2)
                ), row=2, col=1)
                
                # Add reference line at 100 (starting value)
                fig.add_hline(
                    y=base, 
                    line_dash="dash", 
                    line_color="gray", 
                    row=2, 
                    col=1
                )

        # Add financial metrics
        if 'financial_data' in data and isinstance(data['financial_data'], dict):
            financial = data['financial_data']
            metrics = {
                'Current Ratio': self._extract_float_from_string(financial.get('current_ratio', 0)),
                'Debt/Equity': self._extract_float_from_string(financial.get('debt_to_equity', 0)),
                'Profit Margin': self._extract_float_from_string(financial.get('profit_margin', 0))
            }
            
            fig.add_trace(go.Bar(
                x=list(metrics.keys()),
                y=list(metrics.values()),
                name='Financial Metrics',
                marker_color=self.colors['info']
            ), row=2, col=2)

        fig.update_layout(
            title='Stock Analysis Summary',
            height=800,
            showlegend=True
        )

        return fig

    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs)) 