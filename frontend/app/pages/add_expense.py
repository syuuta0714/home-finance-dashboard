"""Add expense page - form to add new expenses"""

import streamlit as st
from datetime import date
from app.api_client import api_client, APIError
from app.utils.validation import (
    validate_date,
    validate_amount,
    validate_category,
    validate_memo,
    get_categories
)
from app.utils.formatting import get_current_date


def render():
    """Render the add expense page"""
    st.title("➕ 支出追加")
    
    st.markdown("日々の支出を記録します。")
    
    # Create form
    with st.form("add_expense_form", clear_on_submit=True):
        # Category selection
        categories = get_categories()
        category = st.selectbox(
            "カテゴリ *",
            options=categories,
            help="支出のカテゴリを選択してください"
        )
        
        # Amount input
        amount = st.number_input(
            "金額（円） *",
            min_value=0,
            value=0,
            step=100,
            help="支出金額を入力してください（0以上の整数）"
        )
        
        # Date input
        current_date = get_current_date()
        expense_date = st.date_input(
            "日付 *",
            value=current_date,
            help="支出日を選択してください"
        )
        
        # Memo input (optional)
        memo = st.text_area(
            "メモ（任意）",
            max_chars=500,
            help="支出に関するメモを入力できます（最大500文字）"
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 登録", use_container_width=True)
        
        if submitted:
            # Validate inputs
            errors = []
            
            # Validate category
            is_valid, error_msg = validate_category(category)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate amount
            is_valid, error_msg = validate_amount(amount)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate date
            date_str = expense_date.strftime("%Y-%m-%d")
            is_valid, error_msg = validate_date(date_str)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate memo
            is_valid, error_msg = validate_memo(memo)
            if not is_valid:
                errors.append(error_msg)
            
            # Display validation errors
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Submit to API
                try:
                    with st.spinner("登録中..."):
                        result = api_client.create_expense(
                            date=date_str,
                            category=category,
                            amount=amount,
                            memo=memo if memo else None
                        )
                    
                    st.success(f"✅ 支出を登録しました！（ID: {result['id']}）")
                    st.balloons()
                    
                    # Show registered data
                    with st.expander("登録内容を確認"):
                        st.json(result)
                    
                    # Suggest next action
                    st.info("💡 ダッシュボードで集計を確認できます")
                
                except APIError as e:
                    st.error(f"❌ 登録に失敗しました: {e.message}")
                    if e.detail:
                        st.error(f"詳細: {e.detail}")
                
                except Exception as e:
                    st.error(f"❌ 予期しないエラーが発生しました: {str(e)}")
    
    # Display recent expenses
    st.divider()
    st.markdown("### 📋 最近の支出")
    
    try:
        with st.spinner("読み込み中..."):
            expenses = api_client.get_expenses()
        
        if expenses:
            # Sort by date (most recent first)
            expenses_sorted = sorted(expenses, key=lambda x: x["date"], reverse=True)
            
            # Display up to 10 recent expenses
            for expense in expenses_sorted[:10]:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.text(expense["date"])
                
                with col2:
                    st.text(expense["category"])
                
                with col3:
                    st.text(f"¥{expense['amount']:,}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_{expense['id']}", help="削除"):
                        try:
                            api_client.delete_expense(expense["id"])
                            st.success("削除しました")
                            st.rerun()
                        except APIError as e:
                            st.error(f"削除に失敗しました: {e.message}")
                
                if expense.get("memo"):
                    st.caption(f"📝 {expense['memo']}")
                
                st.divider()
        else:
            st.info("まだ支出が登録されていません")
    
    except APIError as e:
        st.warning(f"⚠️ 支出一覧の取得に失敗しました: {e.message}")
    
    except Exception as e:
        st.warning(f"⚠️ 予期しないエラーが発生しました: {str(e)}")

