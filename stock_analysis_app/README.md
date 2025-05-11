# Stock Analysis Application with Watchlist Feature

A comprehensive stock analysis web application that allows users to analyze stocks and manage a personal watchlist.

## Features

- **Stock Analysis**: Analyze individual stocks with detailed financial metrics, price charts, and technical indicators
- **Watchlist Management**: Add, view, and remove stocks from your watchlist
- **Data Visualization**: View charts and graphs of stock performance
- **Intangible Assets Analysis**: Track and analyze intangible assets for companies
- **Mobile Responsive**: Works on desktop and mobile devices

## Setup Instructions

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your web browser and navigate to `http://localhost:5000`

## Using the Watchlist Feature

### Adding Stocks to Your Watchlist

You can add stocks to your watchlist in two ways:
1. From the analysis page: After analyzing a stock, click the "Add to Watchlist" button
2. From the watchlist page: Enter a ticker symbol in the "Add" field

### Viewing Your Watchlist

Navigate to the watchlist page by clicking "Watchlist" in the navigation bar or the "View Your Watchlist" button on the home page.

### Managing Your Watchlist

- **View Details**: Click on any stock symbol in your watchlist to analyze it
- **Remove Stocks**: Click the trash icon next to a stock to remove it from your watchlist
- **Refresh Data**: Click the "Refresh Data" button to update all stocks in your watchlist

## Technical Details

- The application uses Flask as the web framework
- Data is stored in a SQLite database using SQLAlchemy
- Stock data is fetched from various financial APIs
- The watchlist data persists between sessions

## Database Schema

The watchlist feature uses a simple database schema:

```
Watchlist
- id: Integer (Primary Key)
- user_id: String (for future user authentication)
- symbol: String (stock ticker symbol)
- date_added: DateTime
- notes: Text (optional notes about the stock)
```

## API Key

The application uses the Alpha Vantage API. The API key is already configured in the application. Note that the free tier has a limit of 25 API requests per day.

## Technologies Used

- Flask (Python web framework)
- Plotly (Interactive charts)
- Bootstrap (UI framework)
- Alpha Vantage API (Stock market data)
- Pandas (Data processing)
- NumPy (Numerical computations)

## Project Structure

```
stock_analysis_app/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Custom CSS
│   └── js/
│       └── main.js        # JavaScript for interactive elements
├── templates/             # HTML templates
│   ├── base.html          # Base template with common elements
│   └── home.html          # Home page
└── modules/               # Python modules
    ├── data_fetcher.py    # Functions for fetching data from APIs
    └── visualizer.py      # Functions for creating visualizations
``` 