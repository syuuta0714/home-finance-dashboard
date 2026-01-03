"""Streamlit application entry point"""

import streamlit as st
from app.config import settings

# Page configuration
st.set_page_config(
    page_title="家庭内生活費ダッシュボード",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded" if not settings.kiosk_mode else "collapsed"
)

# Apply custom CSS for kiosk mode
if settings.kiosk_mode:
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            font-size: 3rem !important;
        }
        .stMetric label {
            font-size: 1.5rem !important;
        }
        .stMetric .metric-value {
            font-size: 3rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Sidebar navigation
with st.sidebar:
    st.title("📊 ナビゲーション")
    
    if st.button("🏠 ダッシュボード", use_container_width=True):
        st.session_state.page = "dashboard"
    
    if st.button("➕ 支出追加", use_container_width=True):
        st.session_state.page = "add_expense"
    
    if st.button("💰 予算管理", use_container_width=True):
        st.session_state.page = "manage_budget"
    
    if st.button("📊 支出統計", use_container_width=True):
        st.session_state.page = "expense_statistics"
    
    st.divider()
    st.caption(f"Backend: {settings.backend_url}")
    st.caption(f"Timezone: {settings.timezone}")
    if settings.kiosk_mode:
        st.caption("🖥️ Kioskモード")

# Page routing
if st.session_state.page == "dashboard":
    from app.pages import dashboard
    dashboard.render()
elif st.session_state.page == "add_expense":
    from app.pages import add_expense
    add_expense.render()
elif st.session_state.page == "manage_budget":
    from app.pages import manage_budget
    manage_budget.render()
elif st.session_state.page == "expense_statistics":
    from app.pages import expense_statistics
    expense_statistics.render()
