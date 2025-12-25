"""Status card component for displaying budget status"""

import streamlit as st
from typing import Dict, Any
from app.utils.formatting import format_percentage


def render_status_card(summary: Dict[str, Any]):
    """
    Render status card with usage rate and status indicator
    
    Args:
        summary: Summary data from API
    """
    usage_rate = summary["usage_rate"]
    status = summary["status"]
    status_message = summary["status_message"]
    status_color = summary["status_color"]
    
    # Map status color to Streamlit color
    color_map = {
        "green": "🟢",
        "yellow": "🟡",
        "red": "🔴"
    }
    
    emoji = color_map.get(status_color, "⚪")
    
    # Display status with large text
    st.markdown(f"### {emoji} 状態: {status}")
    
    # Progress bar for usage rate
    progress_value = min(usage_rate / 100, 1.0)
    st.progress(progress_value)
    
    # Usage rate
    st.markdown(f"**使用率:** {format_percentage(usage_rate)}")
    
    # Status message with appropriate styling
    if status_color == "green":
        st.success(status_message)
    elif status_color == "yellow":
        st.warning(status_message)
    elif status_color == "red":
        st.error(status_message)
    else:
        st.info(status_message)
