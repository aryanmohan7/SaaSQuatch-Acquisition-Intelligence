# SaaSQuatch Acquisition Intelligence Dashboard

![Dashboard Screenshot](Dashboard Screenshot.jpg)

> AI-powered M&A target identification system for private equity and corporate development teams

## Features

- **Smart Scoring Algorithm**
  - 0-100 acquisition score based on 4 key dimensions
  - Weighted evaluation of owner readiness, financial health, valuation, and business stability
  - Clear classification (Hot/Warm/Cold) with visual indicators

- **Interactive Discovery**
  - Dynamic filtering by score range, industry, and revenue
  - Sortable target list prioritized by acquisition potential
  - Detailed company profile view with key metrics

- **Actionable Intelligence**
  - Automated signal detection (positive/neutral/warning)
  - Custom financial metrics (EBITDA margin, valuation multiples)
  - One-click contact initiation workflow

- **Data Operations**
  - CSV export functionality
  - Sample dataset included
  - Easy integration with real data sources

## Setup & Installation

### Prerequisites
- Python 3.8+
- Streamlit
- Pandas

```bash
# Clone the repository
git clone https://github.com/yourusername/SaaSQuatch-Acquisition-Intelligence.git

# Navigate to project directory
cd SaaSQuatch-Acquisition-Intelligence

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app/acquisition_dashboard.py
