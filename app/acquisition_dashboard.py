import pandas as pd
import streamlit as st
from datetime import datetime
from typing import List, Dict
import base64
import json

# Configure Streamlit page
st.set_page_config(
    page_title="SaaSQuatch Pro | Acquisition Intelligence",
    page_icon="🦄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved UI
st.markdown("""
<style>
    .css-18e3th9 { padding: 2rem 5rem; }
    .st-b7 { color: #4f46e5; }
    .st-c0 { background-color: #4f46e5; }
    .st-ck { border-color: #4f46e5; }
    .metric-card {
        border-radius: 8px;
        padding: 1rem;
        background: black;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .company-card {
        border-radius: 8px;
        padding: 1.5rem;
        background: black;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        transition: all 0.2s;
    }
    .company-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .positive-signal {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #10b981;
    }
    .warning-signal {
        background-color: #ffedd5;
        color: #9a3412;
        padding: 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #f97316;
    }
    .neutral-signal {
        background-color: #e0e7ff;
        color: #3730a3;
        padding: 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #6366f1;
    }
    .score-hot {
        color: #d97706;
        font-weight: 700;
    }
    .score-warm {
        color: #2563eb;
        font-weight: 700;
    }
    .score-cold {
        color: #6b7280;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

class AcquisitionTarget:
    def __init__(self, data: Dict):
        self.id = data['id']
        self.company = data['company']
        self.industry = data['industry']
        self.location = data['location']
        self.employees = data['employees']
        self.revenue = data['revenue']
        self.ebitda = data['ebitda']
        self.year_founded = data['yearFounded']
        self.owner_age = data['ownerAge']
        self.asking_price = data['askingPrice']
        self.score = data['score']
        self.signals = data['signals']
        
    def get_score_class(self):
        if self.score >= 80:
            return "score-hot", "Hot"
        elif self.score >= 50:
            return "score-warm", "Warm"
        return "score-cold", "Cold"
    
    def calculate_metrics(self):
        ebitda_margin = (self.ebitda / self.revenue) * 100 if self.revenue > 0 else 0
        multiple = self.asking_price / self.ebitda if self.ebitda > 0 else 0
        business_age = datetime.now().year - self.year_founded
        return {
            "ebitda_margin": ebitda_margin,
            "multiple": multiple,
            "business_age": business_age
        }

class AcquisitionScorer:
    @staticmethod
    def calculate_score(target: Dict) -> int:
        score = 0
        
        # Owner readiness (30 points)
        owner_age = target['ownerAge']
        if owner_age >= 60: score += 30
        elif owner_age >= 55: score += 20
        elif owner_age >= 50: score += 10
        
        # Financial health (30 points)
        ebitda_margin = (target['ebitda'] / target['revenue']) * 100 if target['revenue'] > 0 else 0
        if ebitda_margin >= 25: score += 30
        elif ebitda_margin >= 20: score += 25
        elif ebitda_margin >= 15: score += 20
        elif ebitda_margin >= 10: score += 10
        
        # Valuation reasonableness (20 points)
        multiple = target['askingPrice'] / target['ebitda'] if target['ebitda'] > 0 else 0
        if multiple <= 4: score += 20
        elif multiple <= 5: score += 15
        elif multiple <= 6: score += 10
        elif multiple <= 8: score += 5
        
        # Business stability (20 points)
        business_age = datetime.now().year - target['yearFounded']
        if business_age >= 10: score += 10
        elif business_age >= 5: score += 5
        
        if target['employees'] >= 50: score += 10
        elif target['employees'] >= 20: score += 5
        
        return min(100, score)
    
    @staticmethod
    def generate_signals(target: Dict) -> List[Dict]:
        signals = []
        
        # Owner signals
        if target['ownerAge'] >= 60:
            signals.append({
                'type': 'positive',
                'text': f'Owner at retirement age ({target["ownerAge"]}) - highly motivated'
            })
        elif target['ownerAge'] >= 55:
            signals.append({
                'type': 'positive',
                'text': f'Owner approaching retirement ({target["ownerAge"]})'
            })
        else:
            signals.append({
                'type': 'warning',
                'text': f'Young owner ({target["ownerAge"]}) - unlikely to sell soon'
            })
        
        # Financial signals
        ebitda_margin = (target['ebitda'] / target['revenue']) * 100 if target['revenue'] > 0 else 0
        if ebitda_margin >= 25:
            signals.append({
                'type': 'positive',
                'text': f'Exceptional {ebitda_margin:.1f}% EBITDA margin'
            })
        elif ebitda_margin >= 20:
            signals.append({
                'type': 'positive',
                'text': f'Strong {ebitda_margin:.1f}% EBITDA margin'
            })
        elif ebitda_margin < 15:
            signals.append({
                'type': 'warning',
                'text': f'Below average {ebitda_margin:.1f}% EBITDA margin'
            })
        
        # Valuation signals
        multiple = target['askingPrice'] / target['ebitda'] if target['ebitda'] > 0 else 0
        if multiple <= 4:
            signals.append({
                'type': 'positive',
                'text': f'Attractive valuation at {multiple:.1f}x EBITDA'
            })
        elif multiple <= 5:
            signals.append({
                'type': 'neutral',
                'text': f'Fair valuation at {multiple:.1f}x EBITDA'
            })
        elif multiple > 6:
            signals.append({
                'type': 'warning',
                'text': f'High valuation at {multiple:.1f}x EBITDA'
            })
        
        return signals

def load_sample_data():
    sample_data = [
        {
            "id": 1,
            "company": "CloudSync Solutions",
            "industry": "SaaS",
            "location": "Austin, TX",
            "employees": 85,
            "revenue": 12000000,
            "ebitda": 3600000,
            "yearFounded": 2015,
            "ownerAge": 58,
            "askingPrice": 48000000
        },
        {
            "id": 2,
            "company": "MedTech Innovations",
            "industry": "Healthcare",
            "location": "Boston, MA",
            "employees": 120,
            "revenue": 18000000,
            "ebitda": 2700000,
            "yearFounded": 2012,
            "ownerAge": 52,
            "askingPrice": 35000000
        },
        {
            "id": 3,
            "company": "Digital Commerce Pro",
            "industry": "E-commerce",
            "location": "Miami, FL",
            "employees": 45,
            "revenue": 8500000,
            "ebitda": 1700000,
            "yearFounded": 2018,
            "ownerAge": 42,
            "askingPrice": 12000000
        },
        {
            "id": 4,
            "company": "Industrial Supply Co",
            "industry": "Manufacturing",
            "location": "Cleveland, OH",
            "employees": 200,
            "revenue": 32000000,
            "ebitda": 4800000,
            "yearFounded": 1998,
            "ownerAge": 65,
            "askingPrice": 38000000
        },
        {
            "id": 5,
            "company": "TechServe Partners",
            "industry": "Professional Services",
            "location": "Denver, CO",
            "employees": 150,
            "revenue": 22000000,
            "ebitda": 3300000,
            "yearFounded": 2010,
            "ownerAge": 55,
            "askingPrice": 28000000
        }
    ]
    
    # Enhance with scores and signals
    for company in sample_data:
        company['score'] = AcquisitionScorer.calculate_score(company)
        company['signals'] = AcquisitionScorer.generate_signals(company)
    
    return [AcquisitionTarget(company) for company in sample_data]

def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href

def main():
    st.title("🦄 SaaSQuatch Acquisition Intelligence")
    st.markdown("Identify and prioritize high-value acquisition targets with AI-driven scoring")
    
    # Load data
    targets = load_sample_data()
    
        # Sidebar filters
    st.sidebar.header("Filters")
    score_filter = st.sidebar.selectbox(
        "Acquisition Score",
        ["All", "Hot (80+)", "Warm (50-79)", "Cold (<50)"],
        index=0
    )
    industry_filter = st.sidebar.selectbox(
        "Industry",
        ["All"] + sorted(list(set([t.industry for t in targets])))
    )
    revenue_filter = st.sidebar.selectbox(
        "Revenue Range",
        ["All", "$1M - $5M", "$5M - $10M", "$10M - $25M", "$25M+"]
    )
    
    # Apply filters
    filtered_targets = targets.copy()
    if score_filter != "All":
        min_score = 80 if score_filter.startswith("Hot") else 50 if score_filter.startswith("Warm") else 0
        max_score = 100 if score_filter.startswith("Hot") else 79 if score_filter.startswith("Warm") else 49
        filtered_targets = [t for t in filtered_targets if min_score <= t.score <= max_score]
    
    if industry_filter != "All":
        filtered_targets = [t for t in filtered_targets if t.industry == industry_filter]
    
    if revenue_filter != "All":
        rev_ranges = {
            "$1M - $5M": (1e6, 5e6),
            "$5M - $10M": (5e6, 10e6),
            "$10M - $25M": (10e6, 25e6),
            "$25M+": (25e6, float('inf'))
        }
        min_rev, max_rev = rev_ranges[revenue_filter]
        filtered_targets = [t for t in filtered_targets if min_rev <= t.revenue < max_rev]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Targets</h3>
            <h1>{len(filtered_targets)}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        hot_leads = len([t for t in filtered_targets if t.score >= 80])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Hot Leads (80+)</h3>
            <h1>{hot_leads}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        avg_score = sum(t.score for t in filtered_targets) / len(filtered_targets) if filtered_targets else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Score</h3>
            <h1>{avg_score:.1f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Target cards
    for target in sorted(filtered_targets, key=lambda x: x.score, reverse=True):
        score_class, score_label = target.get_score_class()
        metrics = target.calculate_metrics()

        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(target.company)
                st.caption(f"{target.industry} • {target.location} • {target.employees} employees")
            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <h3 class="{score_class}">{target.score}</h3>
                    <p style="color: #6b7280; font-size: 0.875rem;">{score_label}</p>
                </div>
                """, unsafe_allow_html=True)

            # Financial metrics using columns
            cols = st.columns(3)
            metrics_data = [
                (f"${target.revenue/1e6:.1f}M", "Revenue"),
                (f"{metrics['ebitda_margin']:.1f}%", "EBITDA Margin"),
                (f"{metrics['multiple']:.1f}x", "Multiple")
            ]

            for col, (value, label) in zip(cols, metrics_data):
                with col:
                    st.metric(label, value)

            # Acquisition signals
            st.subheader("Acquisition Signals", divider=True)
            for signal in target.signals:
                if signal['type'] == 'positive':
                    st.success(signal['text'])
                elif signal['type'] == 'warning':
                    st.warning(signal['text'])
                else:
                    st.info(signal['text'])

            # Action buttons
            contact_col, analysis_col = st.columns(2)
            with contact_col:
                if st.button(f"Contact {target.company}", key=f"contact_{target.id}"):
                    st.success(f"Contact initiated with {target.company}!")
            with analysis_col:
                if st.button("View Full Analysis", key=f"analysis_{target.id}"):
                    st.session_state['selected_company'] = target.company
                    st.rerun()
    
    # Export data
    st.sidebar.markdown("---")
    st.sidebar.header("Export Data")
    if st.sidebar.button("Export to CSV"):
        df = pd.DataFrame([{
            "Company": t.company,
            "Industry": t.industry,
            "Location": t.location,
            "Revenue": t.revenue,
            "EBITDA": t.ebitda,
            "EBITDA Margin": (t.ebitda / t.revenue * 100) if t.revenue > 0 else 0,
            "Multiple": (t.asking_price / t.ebitda) if t.ebitda > 0 else 0,
            "Score": t.score,
            "Status": t.get_score_class()[1],
            "Owner Age": t.owner_age,
            "Asking Price": t.asking_price
        } for t in filtered_targets])
        st.sidebar.markdown(create_download_link(df, "acquisition_targets.csv"), unsafe_allow_html=True)
    
    # Company detail view
    if 'selected_company' in st.session_state:
        target = next((t for t in targets if t.company == st.session_state['selected_company']), None)
        metrics = target.calculate_metrics()
        
        st.markdown("---")
        st.markdown(f"## 🏢 {target.company} - Detailed Analysis")
        st.markdown(f"**Industry:** {target.industry} | **Location:** {target.location} | **Employees:** {target.employees}")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Financial Overview")
            st.markdown(f"""
            - **Revenue:** ${target.revenue/1e6:.1f}M
            - **EBITDA:** ${target.ebitda/1e6:.1f}M
            - **EBITDA Margin:** {metrics['ebitda_margin']:.1f}%
            - **Asking Price:** ${target.asking_price/1e6:.1f}M
            - **Valuation Multiple:** {metrics['multiple']:.1f}x
            """)
            
            st.markdown("### Business Details")
            st.markdown(f"""
            - **Year Founded:** {target.year_founded}
            - **Business Age:** {metrics['business_age']} years
            - **Owner Age:** {target.owner_age}
            """)
        
        with col2:
            st.markdown("### Acquisition Signals")
            for signal in target.signals:
                if signal['type'] == 'positive':
                    st.markdown(f'<div class="positive-signal">✓ {signal["text"]}</div>', unsafe_allow_html=True)
                elif signal['type'] == 'warning':
                    st.markdown(f'<div class="warning-signal">! {signal["text"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="neutral-signal">• {signal["text"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### Recommended Actions")
            st.markdown("""
            1. **Initial Outreach:** Personalized email focusing on owner's situation
            2. **Valuation Discussion:** Prepare comparables analysis
            3. **Due Diligence:** Review customer concentration
            """)
        
        if st.button("← Back to List"):
            del st.session_state['selected_company']
            st.experimental_rerun()

        if target is None:
            st.error("Company not found in records")
            del st.session_state['selected_company']
            st.experimental_rerun()
        else:
            metrics = target.calculate_metrics()

if __name__ == "__main__":
    main()