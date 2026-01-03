"""Expense statistics page - view expense statistics by category"""

import streamlit as st
from app.api_client import api_client, APIError
from app.utils.validation import validate_month
from app.utils.formatting import get_current_month, format_month, format_currency
import pandas as pd


def render():
    """Render the expense statistics page"""
    st.title("📊 支出統計")
    
    st.markdown("カテゴリ別の支出統計を確認します。")
    
    # Month selection
    current_month = get_current_month()
    selected_month = st.text_input(
        "対象月 *",
        value=current_month,
        help="YYYY-MM形式で入力してください（例: 2025-12）"
    )
    
    # Validate month
    is_valid_month, month_error = validate_month(selected_month)
    if not is_valid_month:
        st.error(f"❌ {month_error}")
        return
    
    st.markdown(f"### {format_month(selected_month)} の支出統計")
    
    # Load data
    try:
        with st.spinner("データを読み込み中..."):
            # Get expense statistics
            expense_stats = api_client.get_expense_statistics(selected_month)
            # Get categories for name mapping
            categories_data = api_client.get_categories()
    except APIError as e:
        st.error(f"❌ データの取得に失敗しました: {e.message}")
        return
    except Exception as e:
        st.error(f"❌ 予期しないエラーが発生しました: {str(e)}")
        return
    
    # Create category mapping
    category_map = {cat["id"]: cat["name"] for cat in categories_data}
    
    if not expense_stats:
        st.info("📭 この月の支出がまだ登録されていません")
        return
    
    # Calculate totals
    total_expenses = sum(expense_stats.values())
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 総支出", format_currency(total_expenses))
    
    with col2:
        st.metric("📋 カテゴリ数", len(expense_stats))
    
    with col3:
        avg_per_category = total_expenses // len(expense_stats) if expense_stats else 0
        st.metric("📊 平均支出", format_currency(avg_per_category))
    
    st.divider()
    
    # Prepare data for visualization
    categories_display = []
    amounts = []
    
    for category_id in sorted(expense_stats.keys()):
        amount = expense_stats[category_id]
        category_name = category_map.get(category_id, category_id)
        categories_display.append(category_name)
        amounts.append(amount)
    
    # Create DataFrame for charts
    df_chart = pd.DataFrame({
        "カテゴリ": categories_display,
        "金額": amounts
    })
    
    # Create pie chart using Streamlit
    st.markdown("#### 📊 支出構成（円グラフ）")
    st.bar_chart(df_chart.set_index("カテゴリ"), height=400)
    
    st.divider()
    
    # Display detailed table
    st.markdown("#### 📋 詳細一覧")
    
    # Create table data
    table_data = []
    for category_id in sorted(expense_stats.keys()):
        amount = expense_stats[category_id]
        category_name = category_map.get(category_id, category_id)
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        
        table_data.append({
            "カテゴリ": category_name,
            "金額": format_currency(amount),
            "割合": f"{percentage:.1f}%"
        })
    
    # Display as table
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Display expenses by category
    st.markdown("#### 📝 カテゴリ別支出詳細")
    
    try:
        with st.spinner("支出詳細を読み込み中..."):
            all_expenses = api_client.get_expenses(month=selected_month)
    except APIError as e:
        st.warning(f"⚠️ 支出詳細の取得に失敗しました: {e.message}")
        return
    except Exception as e:
        st.warning(f"⚠️ 予期しないエラーが発生しました: {str(e)}")
        return
    
    # Group expenses by category
    expenses_by_category = {}
    for expense in all_expenses:
        category_id = expense["category"]
        if category_id not in expenses_by_category:
            expenses_by_category[category_id] = []
        expenses_by_category[category_id].append(expense)
    
    # Display expenses for each category
    for category_id in sorted(expenses_by_category.keys()):
        category_name = category_map.get(category_id, category_id)
        category_total = expense_stats.get(category_id, 0)
        
        with st.expander(f"🏷️ {category_name} (¥{category_total:,})"):
            expenses = expenses_by_category[category_id]
            
            # Sort by date (most recent first)
            expenses_sorted = sorted(expenses, key=lambda x: x["date"], reverse=True)
            
            for expense in expenses_sorted:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.text(expense["date"])
                
                with col2:
                    st.text(f"¥{expense['amount']:,}")
                
                with col3:
                    st.caption(f"ID: {expense['id']}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_expense_{expense['id']}", help="削除"):
                        try:
                            api_client.delete_expense(expense["id"])
                            st.success("削除しました")
                            st.rerun()
                        except APIError as e:
                            st.error(f"削除に失敗しました: {e.message}")
                
                if expense.get("memo"):
                    st.caption(f"📝 {expense['memo']}")
                
                st.divider()

