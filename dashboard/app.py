import os
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER', 'gendalf')}:"
    f"{os.getenv('POSTGRES_PASSWORD', '1230')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', '5433')}/"
    f"{os.getenv('POSTGRES_DB', 'esp_db')}",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Measurement(db.Model):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    humidity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    context: dict = {
        "title": "8G Dashboard",
    }
    return render_template('pages/home.html', **context)

if __name__ == '__main__':
    app.run(debug=True)