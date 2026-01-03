"""Manage budget page - form to set monthly budgets"""

import streamlit as st
from app.api_client import api_client, APIError
from app.utils.validation import validate_month
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
    
    # Load categories and existing budgets
    try:
        with st.spinner("カテゴリーと既存予算を読み込み中..."):
            categories_data = api_client.get_categories()
            monthly_budgets = api_client.get_monthly_budgets(month=selected_month)
    except APIError as e:
        st.error(f"❌ データの取得に失敗しました: {e.message}")
        return
    except Exception as e:
        st.error(f"❌ 予期しないエラーが発生しました: {str(e)}")
        return
    
    # Create mapping from category ID to name and existing budgets
    category_map = {cat["id"]: cat["name"] for cat in categories_data if cat.get("is_active", True)}
    existing_budgets = {b["category_id"]: b for b in monthly_budgets}
    
    # Display total budget if exists
    if existing_budgets:
        total_budget = sum(b["amount"] for b in existing_budgets.values())
        st.info(f"📊 現在の予算合計: {format_currency(total_budget)}")
    
    st.divider()
    
    # Budget input form for each category
    budget_inputs = {}
    
    st.markdown("#### カテゴリ別予算入力")
    
    for category_id in sorted(category_map.keys()):
        category_name = category_map[category_id]
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown(f"**{category_name}**")
        
        with col2:
            # Get existing amount or default to 0
            existing_amount = existing_budgets.get(category_id, {}).get("amount", 0)
            
            budget_inputs[category_id] = st.number_input(
                f"金額（円）",
                min_value=0,
                value=existing_amount,
                step=1000,
                key=f"budget_{category_id}",
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
            
            for category_id, amount in budget_inputs.items():
                # Skip if amount is 0 and no existing budget
                if amount == 0 and category_id not in existing_budgets:
                    continue
                
                # Save budget
                try:
                    with st.spinner(f"{category_map[category_id]}を保存中..."):
                        result = api_client.create_monthly_budget(
                            month=selected_month,
                            category_id=category_id,
                            amount=amount
                        )
                    success_count += 1
                
                except APIError as e:
                    errors.append(f"{category_map[category_id]}: {e.message}")
                
                except Exception as e:
                    errors.append(f"{category_map[category_id]}: {str(e)}")
            
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
        
        for category_id in sorted(category_map.keys()):
            if category_id in existing_budgets:
                budget = existing_budgets[category_id]
                category_name = category_map[category_id]
                
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.text(category_name)
                
                with col2:
                    st.text(format_currency(budget["amount"]))
                
                with col3:
                    st.caption(f"更新: {budget.get('updated_at', 'N/A')[:10]}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_budget_{budget['id']}", help="削除"):
                        try:
                            api_client.delete_monthly_budget(budget["id"])
                            st.success("削除しました")
                            st.rerun()
                        except APIError as e:
                            st.error(f"削除に失敗しました: {e.message}")
                
                st.divider()

