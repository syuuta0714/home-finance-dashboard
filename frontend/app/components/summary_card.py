"""Summary card component for displaying financial metrics"""

import streamlit as st
from typing import Dict, Any
from app.utils.formatting import (
    format_currency,
    format_percentage,
    format_days_remaining,
    format_per_day_budget
)


def render_summary_card(summary: Dict[str, Any]):
    """
    Render summary card with financial metrics
    
    Args:
        summary: Summary data from API
    """
    # Main metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📊 予算合計",
            value=format_currency(summary["total_budget"])
        )
    
    with col2:
        st.metric(
            label="💸 使用合計",
            value=format_currency(summary["total_spent"])
        )
    
    with col3:
        remaining = summary["remaining"]
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric(
            label="💰 残額",
            value=format_currency(remaining),
            delta=None
        )
    
    st.divider()
    
    # Secondary metrics
    col4, col5 = st.columns(2)
    
    with col4:
        st.metric(
            label="📅 残日数",
            value=format_days_remaining(summary["remaining_days"])
        )
    
    with col5:
        per_day = summary.get("per_day_budget")
        st.metric(
            label="💵 1日あたり残予算",
            value=format_per_day_budget(per_day)
        )
