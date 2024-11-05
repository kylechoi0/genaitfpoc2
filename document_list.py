import streamlit as st
import requests
from datetime import datetime

# API 키 설정
KNOWLEDGE_API_KEY = st.secrets["KNOWLEDGE_API_KEY"]

def get_document_list(dataset_id, page=1, limit=20):
    """지식 데이터셋의 문서 리스트를 조회하는 함수"""
    try:
        headers = {
            'Authorization': f'Bearer {KNOWLEDGE_API_KEY}'
        }
        
        params = {
            'page': page,
            'limit': limit
        }
        
        response = requests.get(
            f'https://mir-api.52g.ai/v1/datasets/{dataset_id}/documents',
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"문서 리스트 조회 실패: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"문서 리스트 조회 중 오류 발생: {str(e)}")
        return None

def delete_document(dataset_id, document_id):
    """문서를 삭제하는 함수"""
    try:
        headers = {
            'Authorization': f'Bearer {KNOWLEDGE_API_KEY}'
        }
        
        response = requests.delete(
            f'https://mir-api.52g.ai/v1/datasets/{dataset_id}/documents/{document_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"문서 삭제 실패: {response.text}")
            return False
            
    except Exception as e:
        st.error(f"문서 삭제 중 오류 발생: {str(e)}")
        return False

def show_document_list_modal(dataset_id):
    """문서 리스트를 모달로 표시하는 함수"""
    # 스타일 적용
    st.markdown("""
        <style>
        .doc-modal {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .doc-table {
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .pagination {
            text-align: center;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("### 📚 저장된 문서 리스트")
        
        # 현재 페이지 상태 관리
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        # 페이지 크기 선택
        limit = st.selectbox("페이지당 문서 수", [10, 20, 50], index=1)
        
        # 문서 리스트 조회
        doc_list = get_document_list(dataset_id, st.session_state.current_page, limit)
        
        if doc_list and 'data' in doc_list:
            # 문서 정보를 테이블로 표시
            for doc in doc_list['data']:
                with st.expander(f"📄 {doc['name']}"):
                    col1, col2, col3 = st.columns([2,2,1])
                    with col1:
                        status = "✅ 완료" if doc['indexing_status'] == 'completed' else "⏳ 처리 중"
                        st.write(f"상태: {status}")
                    with col2:
                        created_at = datetime.fromtimestamp(doc['created_at']).strftime('%Y-%m-%d %H:%M')
                        st.write(f"생성일: {created_at}")
                    with col3:
                        if st.button("🗑 삭제", key=f"del_{doc['id']}"):
                            if delete_document(dataset_id, doc['id']):
                                st.success("문서가 삭제되었습니다.")
                                st.rerun()
            
            # 페이지네이션
            total_pages = (doc_list['total'] - 1) // limit + 1
            col1, col2, col3 = st.columns([1,2,1])
            
            with col2:
                st.markdown(f"<div class='pagination'>페이지 {st.session_state.current_page}/{total_pages} (총 {doc_list['total']}개)</div>", unsafe_allow_html=True)
            
            # 페이지 이동 버튼
            col1, col2, col3, col4 = st.columns([1,1,1,1])
            with col2:
                if st.session_state.current_page > 1:
                    if st.button("◀ 이전"):
                        st.session_state.current_page -= 1
                        st.rerun()
            with col3:
                if st.session_state.current_page < total_pages:
                    if st.button("다음 ▶"):
                        st.session_state.current_page += 1
                        st.rerun()
        else:
            st.info("저장된 문서가 없습니다.")
        
        # 모달 닫기 버튼
        if st.button("닫기", key="close_modal"):
            st.session_state.show_modal = False
            st.rerun() 