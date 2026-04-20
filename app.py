import streamlit as st
import pandas as pd
import os
import urllib.parse

# 페이지 기본 설정
st.set_page_config(
    page_title="서구 착한가게 안내",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 적용 (세련된 카드 그리드 UI)
st.markdown("""
<style>
    /* 메인 배경색 */
    .stApp {
        background-color: #f9fafb;
    }
    
    /* 카드 컨테이너 스타일 */
    .store-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
        border: 1px solid #f3f4f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .store-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
    }
    
    /* 카테고리 뱃지 */
    .store-category {
        align-self: flex-start;
        padding: 4px 12px;
        background-color: #f3f4f6;
        color: #4b5563;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    /* 가게 이름 */
    .store-name {
        font-size: 1.25rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    /* 주소 및 연락처 정보 */
    .store-info {
        font-size: 0.9rem;
        color: #4b5563;
        margin-bottom: 6px;
        display: flex;
        align-items: flex-start;
        line-height: 1.5;
    }
    
    /* 남은 공간을 밀어서 하단 버튼이 항상 밑에 고정되게 함 */
    .spacer {
        flex-grow: 1;
    }
    
    /* 비고(노트) 뱃지 */
    .note-badge {
        display: inline-block;
        padding: 4px 10px;
        background-color: #e0f2fe;
        color: #0369a1;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 8px;
        margin-bottom: 16px;
    }
    
    /* 카카오맵 버튼 */
    .map-btn {
        display: block;
        margin-top: auto;
        padding: 12px 16px;
        background-color: #fee500; /* 카카오 공식 옐로우 */
        color: #191919;
        text-decoration: none !important;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        transition: background-color 0.2s;
        text-align: center;
        width: 100%;
        border: none;
    }
    .map-btn:hover {
        background-color: #f4dc00;
        color: #191919;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = "seogu_stores.csv"
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')
    
    df = df.fillna("")
    return df

def main():
    st.markdown("<h1 style='text-align: center; color: #111827; margin-bottom: 10px;'>🏪 광주 서구 착한가게 안내</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; font-size: 1.1rem; margin-bottom: 30px;'>우리 동네 가성비 좋고 친절한 착한가게들을 만나보세요.</p>", unsafe_allow_html=True)

    df = load_data()

    if df.empty:
        st.error("⚠️ 데이터 파일을 찾을 수 없습니다. (seogu_stores.csv 파일이 현재 폴더에 있는지 확인해주세요)")
        return

    # 사이드바 설정 (검색 및 필터)
    with st.sidebar:
        st.markdown("### 🔍 검색 및 필터")
        search_query = st.text_input("키워드 검색", placeholder="가게명 또는 주소 입력...")
        st.markdown("---")
        categories = ["전체"] + sorted([c for c in df['category'].unique() if c])
        selected_category = st.radio("카테고리 선택", categories)

    # 데이터 필터링 로직
    filtered_df = df.copy()
    
    if selected_category != "전체":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
    if search_query:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_query, case=False, na=False) |
            filtered_df['address'].str.contains(search_query, case=False, na=False)
        ]

    st.markdown(f"**총 {len(filtered_df)}개**의 착한가게가 검색되었습니다.")

    # 3열(Grid)로 카드 배치
    if len(filtered_df) > 0:
        cols_per_row = 3
        
        for i in range(0, len(filtered_df), cols_per_row):
            cols = st.columns(cols_per_row)
            chunk = filtered_df.iloc[i:i+cols_per_row]
            
            for idx, (_, row) in enumerate(chunk.iterrows()):
                category = row.get('category', '')
                name = row.get('name', '')
                address = row.get('address', '')
                phone = row.get('phone', '')
                if not phone or phone == '없음' or phone == '번호없음':
                    phone = "번호 없음"
                note = row.get('note', '')
                
                # 구 정보 추출 (없으면 기본값 서구)
                sigungu = row.get('sigungu', '서구')
                if pd.isna(sigungu) or not str(sigungu).strip():
                    sigungu = "서구"
                
                # 법인 기호 등 검색에 방해되는 문자 제거
                clean_name = name.replace("㈜", "").replace("(주)", "").replace("(유)", "").strip()
                if not clean_name:
                    clean_name = name
                
                # 카카오맵 검색 URL 생성
                # 주소가 통째로 들어가면 카카오맵이 주소 검색으로 인식해 상호명이 안 뜨거나, 문자열이 너무 길어 오류가 남.
                # "광주광역시 + 구 + 상호명" 형태로 검색하여 상호명이 정확히 노출되도록 개선.
                search_keyword = f"광주광역시 {sigungu} {clean_name}"
                encoded_keyword = urllib.parse.quote(search_keyword)
                kakao_map_url = f"https://map.kakao.com/link/search/{encoded_keyword}"
                
                note_html = f'<div class="note-badge">✨ {note}</div>' if note else '<div class="spacer"></div>'
                spacer_html = '<div class="spacer"></div>' if note else ''
                
                # 파이썬 들여쓰기로 인해 마크다운 파서가 HTML을 코드 블록으로 인식하는 것을 방지하기 위해 좌측 정렬
                card_html = f"""<div class="store-card">
<div class="store-category">{category}</div>
<div class="store-name">{name}</div>
<div class="store-info">📍 {address}</div>
<div class="store-info">📞 {phone}</div>
{spacer_html}
{note_html}
<a href="{kakao_map_url}" target="_blank" class="map-btn">🚀 카카오맵으로 위치 보기</a>
</div>"""
                cols[idx].markdown(card_html, unsafe_allow_html=True)
            
            # 행(row) 구분을 위한 여백
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
    else:
        st.info("검색 결과가 없습니다. 다른 키워드로 검색해 보세요.")

if __name__ == "__main__":
    main()
