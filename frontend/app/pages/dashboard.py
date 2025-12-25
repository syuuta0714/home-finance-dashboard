"""Dashboard page - displays monthly summary"""

import streamlit as st
import time
from datetime import datetime
from app.api_client import api_client, APIError
from app.components.summary_card import render_summary_card
from app.components.status_card import render_status_card
from app.utils.formatting import format_month, get_current_month
from app.config import settings


def render():
    """Render the dashboard page"""
    st.title("🏠 ダッシュボード")
    
    # Month selector
    col1, col2 = st.columns([3, 1])
    with col1:
        current_month = get_current_month()
        selected_month = st.text_input(
            "表示月",
            value=current_month,
            help="YYYY-MM形式で入力してください（例: 2025-12）"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🔄 更新", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Fetch and display summary
    try:
        # Show loading spinner
        with st.spinner("データを読み込み中..."):
            summary = api_client.get_summary(month=selected_month if selected_month else None)
        
        # Display month header
        display_month = selected_month if selected_month else current_month
        st.markdown(f"## {format_month(display_month)} の集計")
        
        # Render summary card
        render_summary_card(summary)
        
        st.divider()
        
        # Render status card
        render_status_card(summary)
        
        # Auto-refresh functionality
        if settings.auto_refresh_interval > 0:
            st.caption(f"⏱️ {settings.auto_refresh_interval}秒ごとに自動更新")
            
            # Use a placeholder for countdown
            placeholder = st.empty()
            
            # Countdown and auto-refresh
            for remaining in range(settings.auto_refresh_interval, 0, -1):
                placeholder.caption(f"次の更新まで: {remaining}秒")
                time.sleep(1)
            
            # Trigger rerun
            st.rerun()
    
    except APIError as e:
        st.error(f"❌ エラーが発生しました: {e.message}")
        if e.detail:
            st.error(f"詳細: {e.detail}")
        
        # Show retry button
        if st.button("🔄 再試行"):
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ 予期しないエラーが発生しました: {str(e)}")
        
        # Show retry button
        if st.button("🔄 再試行"):
            st.rerun()

