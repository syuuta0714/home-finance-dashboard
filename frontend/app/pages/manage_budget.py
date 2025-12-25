"""Manage budget page - form to set monthly budgets"""

import streamlit as st
from app.api_client import api_client, APIError
from app.utils.validation import (
    validate_month,
    validate_amount,
    validate_category,
    get_categories
)
from app.utils.formatting import get_current_month, format_month, format_currency


def render():
    """Render the manage budget page"""
    st.title("💰 予算管理")
    
    st.markdown("月別・カテゴリ別の予算を設定します。")
    
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
    
    st.markdown(f"### {format_month(selected_month)} の予算設定")
    
    # Load existing budgets for the month
    existing_budgets = {}
    try:
        with st.spinner("既存の予算を読み込み中..."):
            budgets = api_client.get_budgets(month=selected_month)
            for budget in budgets:
                existing_budgets[budget["category"]] = budget
    except APIError as e:
        st.warning(f"⚠️ 既存予算の取得に失敗しました: {e.message}")
    except Exception as e:
        st.warning(f"⚠️ 予期しないエラーが発生しました: {str(e)}")
    
    # Display total budget if exists
    if existing_budgets:
        total_budget = sum(b["amount"] for b in existing_budgets.values())
        st.info(f"📊 現在の予算合計: {format_currency(total_budget)}")
    
    st.divider()
    
    # Budget input form for each category
    categories = get_categories()
    budget_inputs = {}
    
    st.markdown("#### カテゴリ別予算入力")
    
    for category in categories:
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown(f"**{category}**")
        
        with col2:
            # Get existing amount or default to 0
            existing_amount = existing_budgets.get(category, {}).get("amount", 0)
            
            budget_inputs[category] = st.number_input(
                f"金額（円）",
                min_value=0,
                value=existing_amount,
                step=1000,
                key=f"budget_{category}",
                label_visibility="collapsed"
            )
    
    # Calculate total
    total_input = sum(budget_inputs.values())
    st.markdown(f"**合計予算:** {format_currency(total_input)}")
    
    st.divider()
    
    # Submit button
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 予算を保存", use_container_width=True, type="primary"):
            # Validate and save budgets
            errors = []
            success_count = 0
            
            for category, amount in budget_inputs.items():
                # Validate amount
                is_valid, error_msg = validate_amount(amount)
                if not is_valid:
                    errors.append(f"{category}: {error_msg}")
                    continue
                
                # Skip if amount is 0 and no existing budget
                if amount == 0 and category not in existing_budgets:
                    continue
                
                # Save budget
                try:
                    with st.spinner(f"{category}を保存中..."):
                        result = api_client.create_budget(
                            month=selected_month,
                            category=category,
                            amount=amount
                        )
                    success_count += 1
                
                except APIError as e:
                    errors.append(f"{category}: {e.message}")
                
                except Exception as e:
                    errors.append(f"{category}: {str(e)}")
            
            # Display results
            if errors:
                st.error("❌ 一部の予算の保存に失敗しました:")
                for error in errors:
                    st.error(error)
            
            if success_count > 0:
                st.success(f"✅ {success_count}件の予算を保存しました！")
                st.balloons()
                
                # Suggest next action
                st.info("💡 ダッシュボードで集計を確認できます")
                
                # Reload page to show updated budgets
                st.rerun()
    
    with col2:
        if st.button("🔄 リセット", use_container_width=True):
            st.rerun()
    
    # Display existing budgets in detail
    if existing_budgets:
        st.divider()
        st.markdown("### 📋 登録済み予算")
        
        for category in categories:
            if category in existing_budgets:
                budget = existing_budgets[category]
                
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.text(category)
                
                with col2:
                    st.text(format_currency(budget["amount"]))
                
                with col3:
                    st.caption(f"更新: {budget['updated_at'][:10]}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_budget_{budget['id']}", help="削除"):
                        try:
                            api_client.delete_budget(budget["id"])
                            st.success("削除しました")
                            st.rerun()
                        except APIError as e:
                            st.error(f"削除に失敗しました: {e.message}")
                
                st.divider()

