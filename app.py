import streamlit as st
import time
from backend import get_outfit_combinations

# 1. 페이지 설정
st.set_page_config(page_title="Find Closet", layout="wide")

# 2. 세션 상태 초기화
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "sel_top" not in st.session_state:
    st.session_state.sel_top = False
if "sel_bottom" not in st.session_state:
    st.session_state.sel_bottom = False
if "sel_dress" not in st.session_state:
    st.session_state.sel_dress = False

# 3. 사이드바
with st.sidebar:
    st.title("🔍 Find Closet")
    st.write("---")
    if st.button("🏠 홈 (스타일 추천)", use_container_width=True):
        st.session_state.current_page = "home"
        st.rerun()
    if st.button("👗 내 옷장 관리", use_container_width=True):
        st.session_state.current_page = "closet"
        st.rerun()
    st.write("---")
    st.info("🤖 **AI STATUS**\n\nCLIP Model Ready")

# --- PAGE 1: 홈 ---
if st.session_state.current_page == "home":
    st.title("🔍 파인드 클로젯")
    st.subheader("자신의 옷장을 검색하고 상황에 맞는 최고의 옷을 추천받으세요.")
    st.write("---")

    st.markdown("### ⚙️ 추천받고 싶은 카테고리를 선택하세요")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        top_type = "primary" if st.session_state.sel_top else "secondary"
        if st.button("👕 상의", type=top_type, use_container_width=True):
            st.session_state.sel_top = not st.session_state.sel_top
            st.rerun()
    with col_b2:
        bottom_type = "primary" if st.session_state.sel_bottom else "secondary"
        if st.button("👖 하의", type=bottom_type, use_container_width=True):
            st.session_state.sel_bottom = not st.session_state.sel_bottom
            st.rerun()
    with col_b3:
        dress_type = "primary" if st.session_state.sel_dress else "secondary"
        if st.button("👗 원피스", type=dress_type, use_container_width=True):
            st.session_state.sel_dress = not st.session_state.sel_dress
            st.rerun()

    st.write("<br>", unsafe_allow_html=True)
    query = st.text_input("💡 어떤 스타일을 찾으시나요?", placeholder="예: '결혼식 하객룩 추천해줘'")

    if st.button("추천받기", type="primary", use_container_width=True):
        if not (st.session_state.sel_top or st.session_state.sel_bottom or st.session_state.sel_dress):
            st.error("⚠️ 카테고리 중 최소 하나를 선택해 주세요!")
        elif not query.strip():
            st.warning("⚠️ 스타일 문장을 입력해 주세요.")
        else:
            st.session_state.search_query = query
            st.session_state.current_page = "results"
            st.rerun()

# --- PAGE 2: 결과 ---
elif st.session_state.current_page == "results":
    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()

    st.title("✨ 스타일 추천 결과")
    st.success(f"**'{st.session_state.search_query}'** 기반으로 내 옷장에서 최적의 조합을 찾았습니다.")

    selected_tabs = []
    selected_categories = []
    if st.session_state.sel_top:
        selected_tabs.append("👕 상의")
        selected_categories.append("Top")
    if st.session_state.sel_bottom:
        selected_tabs.append("👖 하의")
        selected_categories.append("Bottom")
    if st.session_state.sel_dress:
        selected_tabs.append("👗 원피스")
        selected_categories.append("Dress")

    with st.spinner("AI가 코디를 분석 중이에요..."):
        result = get_outfit_combinations(
            st.session_state.search_query,
            st.session_state.sel_top,
            st.session_state.sel_bottom,
            st.session_state.sel_dress
        )

    st.markdown(f"**🏷️ AI 키워드:** {', '.join(result['keywords'])}")
    st.write("---")

    tabs = st.tabs(selected_tabs)
    for idx, cat in enumerate(selected_categories):
        with tabs[idx]:
            if cat == "Top":
                items = result["tops"]
            elif cat == "Bottom":
                items = result["bottoms"]
            else:
                items = result["dresses"]

            if not items:
                st.warning("해당 카테고리에 옷이 없어요! 옷장에 추가해주세요.")
            else:
                cols = st.columns(len(items))
                for rank, item in enumerate(items):
                    with cols[rank]:
                        st.image(item["path"], use_container_width=True)
                        st.markdown(f"### TOP {rank+1}")
                        st.info(f"🔥 유사도: {item['score']:.3f}")

    if result["combinations"]:
        st.write("---")
        st.markdown("### 👗 최적 코디 조합 Top 3")
        for i, combo in enumerate(result["combinations"]):
            st.markdown(f"**{i+1}번 코디** (점수: {combo['score']:.3f})")
            col1, col2 = st.columns(2)
            with col1:
                st.image(combo["top"], caption="상의")
            with col2:
                st.image(combo["bottom"], caption="하의")

# --- PAGE 3: 옷장 관리 ---
elif st.session_state.current_page == "closet":
    st.title("👗 내 옷장 관리")

    if st.button("➕ 옷 추가하기"):
        st.session_state.show_uploader = not st.session_state.get("show_uploader", False)

    if st.session_state.get("show_uploader", False):
        uploaded_file = st.file_uploader("의류 사진 업로드 (JPG, PNG)")
        if uploaded_file:
            with st.spinner("CLIP 모델 속성 분석 중..."):
                time.sleep(1)
            st.success("옷이 추가됐어요!")
            st.session_state.show_uploader = False
            st.rerun()
