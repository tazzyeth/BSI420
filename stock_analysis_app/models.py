from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), default='default_user')  # For future user authentication
    symbol = db.Column(db.String(20), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Watchlist {self.symbol}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date_added': self.date_added.strftime('%Y-%m-%d %H:%M:%S'),
            'notes': self.notes
        } 