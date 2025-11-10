"""
Betty AI Assistant - Admin Dashboard

This page provides analytics and insights from user feedback
to help improve Betty's performance and capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.feedback_manager import feedback_manager

# Page configuration
st.set_page_config(
    page_title="Betty Admin Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching main app styling
st.markdown("""
<style>
    /* Modern styling consistent with main app */
    .stMetric {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
    }

    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    }

    /* Enhanced button styling */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Sidebar improvements */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafc 0%, #ffffff 100%);
    }

    /* Enhanced expanders */
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-weight: 500;
        background: #f7fafc;
    }

    /* Success/Info/Warning message enhancements */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Navigation Header
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        padding: 1.25rem 1.75rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 16px rgba(255, 107, 107, 0.2), 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 2.2rem;
            font-weight: 700;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            letter-spacing: -0.02em;
        ">
            📊 Admin Dashboard
        </h1>
        <p style="
            color: rgba(255, 255, 255, 0.95);
            margin: 0.75rem 0 0 0;
            font-size: 1.05rem;
            font-weight: 400;
            line-height: 1.5;
        ">
            Analytics and Performance Insights for Betty AI
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding-top: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Betty Chat", 
                 use_container_width=True, 
                 type="primary",
                 help="Return to main chat interface"):
        st.switch_page("betty_app.py")

with col3:
    st.markdown("""
    <div style="padding-top: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Admin Dashboard", 
                 use_container_width=True, 
                 type="secondary",
                 disabled=True,
                 help="You are currently here"):
        pass

# Password protection for admin access
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.warning("🔒 Admin access required")
    password = st.text_input("Enter admin password:", type="password")
    if st.button("Login"):
        # In production, use proper authentication
        if password == "Tnd0011!!":  # Change this to a secure password
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Invalid password")
    st.stop()

# Main dashboard content
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")
    
    # Current Page Indicator
    st.markdown("#### 📍 Current Page")
    st.error("📊 **Admin Dashboard** - Analytics")
    
    st.markdown("---")
    
    # Time period selector
    st.markdown("#### 📅 Analysis Period")
    period_options = {
        "Last 7 days": 7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "All time": 365
    }

    selected_period = st.selectbox(
        "Select timeframe",
        options=list(period_options.keys()),
        index=1,  # Default to 30 days
        help="Choose the time period for analytics data"
    )

    days = period_options[selected_period]

    # Refresh data
    st.markdown("#### 🔄 Data Controls")
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    
    # Quick navigation help
    st.markdown("#### 📊 Dashboard Sections")
    with st.expander("📋 What's on this page"):
        st.markdown("""
        **Overview Metrics** - Key performance indicators
        
        **Feedback Breakdown** - User satisfaction data
        
        **Trends Over Time** - Historical patterns
        
        **Quality Analysis** - Response quality metrics
        
        **Improvement Opportunities** - Areas for enhancement
        
        **Recent Feedback** - Detailed feedback data
        """)
    
    st.markdown("---")
    st.caption("📊 Betty Admin Dashboard")
    st.caption("Monitor performance & user feedback")

# Get feedback data
try:
    summary = feedback_manager.get_feedback_summary(days=days)
    recent_feedback = feedback_manager.get_recent_feedback(limit=100)
    improvement_opportunities = feedback_manager.get_improvement_opportunities()
    
    # Convert to DataFrames for easier manipulation
    if recent_feedback:
        df_feedback = pd.DataFrame(recent_feedback)
        df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
    else:
        df_feedback = pd.DataFrame()
    
except Exception as e:
    st.error(f"Error loading feedback data: {e}")
    st.stop()

# === OVERVIEW METRICS ===
st.header("📈 Overview Metrics")

if summary['overall_metrics']['total_feedback'] > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_feedback = summary['overall_metrics']['total_feedback']
        st.metric("Total Feedback", f"{total_feedback:,}")
    
    with col2:
        avg_quality = summary['overall_metrics']['avg_quality']
        st.metric("Avg Quality Score", f"{avg_quality:.2f}/1.0")
    
    with col3:
        avg_obt = summary['overall_metrics']['avg_obt_compliance']
        st.metric("OBT Compliance", f"{avg_obt:.2f}/1.0")
    
    with col4:
        thumbs_up = summary['feedback_counts'].get('thumbs_up', {}).get('count', 0)
        thumbs_down = summary['feedback_counts'].get('thumbs_down', {}).get('count', 0)
        satisfaction_rate = (thumbs_up / (thumbs_up + thumbs_down) * 100) if (thumbs_up + thumbs_down) > 0 else 0
        st.metric("Satisfaction Rate", f"{satisfaction_rate:.1f}%")

else:
    st.info("No feedback data available for the selected period.")
    st.stop()

# === FEEDBACK BREAKDOWN ===
st.header("👍👎 Feedback Breakdown")

col1, col2 = st.columns(2)

with col1:
    # Feedback pie chart
    if summary['feedback_counts']:
        feedback_data = []
        for feedback_type, data in summary['feedback_counts'].items():
            feedback_data.append({
                'type': '👍 Positive' if feedback_type == 'thumbs_up' else '👎 Negative',
                'count': data['count']
            })
        
        df_pie = pd.DataFrame(feedback_data)
        fig_pie = px.pie(
            df_pie, 
            values='count', 
            names='type',
            title="Feedback Distribution",
            color_discrete_map={'👍 Positive': '#00C851', '👎 Negative': '#FF4444'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Quality metrics comparison
    if summary['feedback_counts']:
        metrics_data = []
        for feedback_type, data in summary['feedback_counts'].items():
            metrics_data.append({
                'Feedback Type': '👍 Positive' if feedback_type == 'thumbs_up' else '👎 Negative',
                'Quality Score': data['avg_quality'],
                'OBT Compliance': data['avg_obt_compliance']
            })
        
        df_metrics = pd.DataFrame(metrics_data)
        fig_bar = px.bar(
            df_metrics, 
            x='Feedback Type', 
            y=['Quality Score', 'OBT Compliance'],
            title="Quality Metrics by Feedback Type",
            barmode='group'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# === TRENDS OVER TIME ===
if not df_feedback.empty and len(df_feedback) > 1:
    st.header("📊 Trends Over Time")
    
    # Daily feedback counts
    df_feedback['date'] = df_feedback['timestamp'].dt.date
    daily_counts = df_feedback.groupby(['date', 'feedback_type']).size().reset_index(name='count')
    
    fig_trend = px.line(
        daily_counts, 
        x='date', 
        y='count', 
        color='feedback_type',
        title="Daily Feedback Trends",
        labels={'date': 'Date', 'count': 'Number of Feedback'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# === RESPONSE QUALITY ANALYSIS ===
st.header("🎯 Response Quality Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("OBT Elements Coverage")
    obt_metrics = summary['overall_metrics']
    
    coverage_data = {
        'Element': ['Outcomes', 'KPIs', 'GPS Tiers'],
        'Coverage %': [
            obt_metrics['outcome_percentage'],
            obt_metrics['kpi_percentage'],
            obt_metrics['gps_tier_percentage']
        ]
    }
    
    df_coverage = pd.DataFrame(coverage_data)
    fig_coverage = px.bar(
        df_coverage, 
        x='Element', 
        y='Coverage %',
        title="OBT Elements in Responses",
        color='Coverage %',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_coverage, use_container_width=True)

with col2:
    if not df_feedback.empty:
        st.subheader("Quality Score Distribution")
        fig_hist = px.histogram(
            df_feedback, 
            x='response_quality_score',
            title="Response Quality Score Distribution",
            nbins=20,
            labels={'response_quality_score': 'Quality Score'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# === IMPROVEMENT OPPORTUNITIES ===
st.header("🔧 Improvement Opportunities")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Recent Negative Feedback")
    negative_feedback = improvement_opportunities['negative_feedback']
    
    if negative_feedback:
        for i, feedback in enumerate(negative_feedback[:5]):  # Show top 5
            with st.expander(f"Feedback #{i+1} - {feedback['timestamp'][:10]}"):
                st.write("**User Question:**")
                st.write(feedback['user_message'][:200] + "..." if len(feedback['user_message']) > 200 else feedback['user_message'])
                st.write("**Betty's Response:**")
                st.write(feedback['betty_response'][:300] + "..." if len(feedback['betty_response']) > 300 else feedback['betty_response'])
                if feedback['feedback_details']:
                    st.write("**User Feedback:**")
                    st.write(feedback['feedback_details'])
                st.write(f"**Quality Score:** {feedback['response_quality_score']:.2f}")
                st.write(f"**OBT Compliance:** {feedback['obt_compliance_score']:.2f}")
    else:
        st.info("No negative feedback in the selected period. Great job! 🎉")

with col2:
    st.subheader("Low-Scoring Responses")
    low_scoring = improvement_opportunities['low_scoring_responses']
    
    if low_scoring:
        for i, response in enumerate(low_scoring[:5]):  # Show top 5
            with st.expander(f"Response #{i+1} - Score: {response['response_quality_score']:.2f}"):
                st.write("**User Question:**")
                st.write(response['user_message'][:200] + "..." if len(response['user_message']) > 200 else response['user_message'])
                st.write("**Betty's Response:**")
                st.write(response['betty_response'][:300] + "..." if len(response['betty_response']) > 300 else response['betty_response'])
                st.write(f"**Quality Score:** {response['response_quality_score']:.2f}")
                st.write(f"**OBT Compliance:** {response['obt_compliance_score']:.2f}")
    else:
        st.info("No low-scoring responses found. Betty is performing well! ✨")

# === RECENT FEEDBACK TABLE ===
st.header("📋 Recent Feedback Details")

if not df_feedback.empty:
    # Create a filtered view of recent feedback
    display_df = df_feedback[['timestamp', 'feedback_type', 'response_quality_score', 
                             'obt_compliance_score', 'contains_outcome', 'contains_kpi', 
                             'contains_gps_tier']].copy()
    
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['feedback_type'] = display_df['feedback_type'].map({
        'thumbs_up': '👍 Positive',
        'thumbs_down': '👎 Negative'
    })
    
    # Rename columns for better display
    display_df.columns = ['Timestamp', 'Feedback', 'Quality Score', 'OBT Score', 
                         'Has Outcome', 'Has KPI', 'Has GPS Tier']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Download link for full data
    csv = df_feedback.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Dataset",
        data=csv,
        file_name=f"betty_feedback_{selected_period.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

else:
    st.info("No detailed feedback data available.")

# === FOOTER ===
st.markdown("---")
st.caption(f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("💡 Use this data to identify patterns and improve Betty's responses!")