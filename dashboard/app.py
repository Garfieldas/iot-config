import os
from datetime import date, datetime, time, timedelta
from pathlib import Path

from flask import Flask, render_template, request
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
    return render_template("pages/home.html", title="Dashboard")


def _dashboard_context(interval: str) -> dict:
    intervals = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "12h": timedelta(hours=12),
        "24h": timedelta(hours=24),
    }
    duration = intervals.get(interval, intervals["6h"])
    now = datetime.now().astimezone()
    today_start = datetime.combine(date.today(), time.min, tzinfo=now.tzinfo)
    start = max(today_start, now - duration)

    measurements = (
        Measurement.query.filter(
            Measurement.measured_at >= start,
            Measurement.measured_at <= now,
        )
        .order_by(Measurement.measured_at.asc())
        .all()
    )
    latest = measurements[-1] if measurements else None
    temperatures = [measurement.temperature for measurement in measurements]
    humidities = [measurement.humidity for measurement in measurements]
    chart_measurements = measurements[-48:]

    def average(values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    def value_or_dash(value: float | None, decimals: int = 1) -> str:
        return f"{value:.{decimals}f}" if value is not None else "—"

    chart_max = max(
        [measurement.temperature for measurement in chart_measurements]
        + [measurement.humidity for measurement in chart_measurements]
        + [1]
    )
    return {
        "interval": interval if interval in intervals else "6h",
        "intervals": intervals,
        "latest": latest,
        "measurement_count": len(measurements),
        "temperature_average": value_or_dash(average(temperatures)),
        "humidity_average": value_or_dash(average(humidities)),
        "temperature_min": value_or_dash(min(temperatures) if temperatures else None),
        "temperature_max": value_or_dash(max(temperatures) if temperatures else None),
        "humidity_min": value_or_dash(min(humidities) if humidities else None),
        "humidity_max": value_or_dash(max(humidities) if humidities else None),
        "chart_measurements": chart_measurements,
        "chart_max": chart_max,
        "updated_at": now.strftime("%H:%M"),
        "today": now.strftime("%A, %d %B %Y"),
    }


@app.get("/dashboard/data")
def dashboard_data():
    return render_template(
        "pages/_dashboard_data.html",
        **_dashboard_context(request.args.get("interval", "6h")),
    )

if __name__ == '__main__':
    app.run(debug=True)