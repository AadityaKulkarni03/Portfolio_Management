from flask import Flask, render_template, request
import pandas as pd
import os
from portfolio_analytics.classes.market_data import MarketData
from portfolio_analytics.classes.portfolio_decomposer import PortfolioDecomposer

app = Flask(__name__)

# Paths for portfolio_analytics data

DB_PATH = os.path.abspath("Portfolio-Analytics/portfolio_analytics/data/stocks.db")
META_PATH = os.path.abspath("Portfolio-Analytics/portfolio_analytics/data/etf_metadata.json")

# Initialize MarketData
market_data = MarketData(db_name=DB_PATH, meta_file=META_PATH)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]
    if file.filename == "":
        return "No selected file"

    # Save the file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Read the CSV/XLS file
    df = pd.read_csv(filepath) if file.filename.endswith(".csv") else pd.read_excel(filepath)

    # Process Portfolio
    portfolio_analyzer = PortfolioDecomposer(port=df, market_data=market_data)
    decomposed_stocks = portfolio_analyzer.decompose_stocks()
    decomposed_sectors = portfolio_analyzer.decompose_sectors()

    # Reset index to start from 1
    decomposed_stocks.index += 1
    decomposed_sectors.index += 1

    return render_template(
        "results.html",
        stocks=decomposed_stocks.to_html(classes="table"),
        sectors=decomposed_sectors.to_html(classes="table"),
    )

if __name__ == "__main__":
    app.run(debug=True)
