import os

# No need for dotenv import which is causing errors
# from dotenv import load_dotenv
# load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Alpha Vantage API settings
    ALPHA_VANTAGE_API_KEY = "2HHU95B8Y27E8VNY"  # Updated API key
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    API_TIMEOUT = 30  # Timeout for API requests in seconds
    
    # Application settings
    REQUESTS_PER_MINUTE = 75    # Premium tier limit
    CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)
    USE_MOCK_DATA = True  # Use mock data when API calls fail
    USE_ADVANCED_INDICATORS = True  # Enable advanced technical indicators 