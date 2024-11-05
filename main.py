import streamlit as st
import requests
import json
from datetime import datetime
import uuid
from file_preprocessing import preprocess_files  # Ensure this module is correctly implemented
import traceback
import html  # HTML 이스케이프를 위해 추가

# 필요한 라이브러리 추가
import PyPDF2
import docx2txt
import pandas as pd
import pptx
# HWP 파일 처리를 위한 라이브러리가 필요합니다.

# API URL 정의
API_URL = 'https://mir-api.52g.ai/v1'

# 페이지 설정
st.set_page_config(
    page_title="GS E&R POC #2",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사용자와 에이전트 메시지 표시 함수 정의
def display_user_message(message, timestamp):
    escaped_message = html.escape(message)
    st.markdown(f"""
    <div class="message user-message">
        <div class="message-content">
            <div class="avatar">🧑</div>
            <div class="text">{escaped_message}</div>
        </div>
        <div class="message-timestamp">{timestamp}</div>
    </div>
    """, unsafe_allow_html=True)

def display_agent_message(message, timestamp):
    escaped_message = html.escape(message)
    st.markdown(f"""
    <div class="message agent-message">
        <div class="message-content">
            <div class="avatar">🤖</div>
            <div class="text">{escaped_message}</div>
        </div>
        <div class="message-timestamp">{timestamp}</div>
    </div>
    """, unsafe_allow_html=True)

# 스타일 시트 정의
st.markdown("""
    <style>
        /* 메시지 컨테이너 스타일 */
        .message {
            display: flex;
            flex-direction: column;
            margin: 10px 0;
        }
        .user-message .message-content {
            align-self: flex-end;
            background-color: #E0F7FA; /* 사용자 메시지 배경색 */
        }
        .agent-message .message-content {
            align-self: flex-start;
            background-color: #FFF3E0; /* 에이전트 메시지 배경색 */
        }
        .message-content {
            display: flex;
            align-items: center;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        .avatar {
            margin-right: 10px;
            font-size: 1.5rem;
        }
        .text {
            display: inline-block;
        }
        .message-timestamp {
            font-size: 0.8em;
            color: gray;
            margin-top: 5px;
        }
        .user-message .message-timestamp {
            text-align: right;
        }
        .agent-message .message-timestamp {
            text-align: left;
        }

        /* 전체 컨테이너의 상단 여백 조정 */
        .main .block-container {
            padding-top: 2rem !important;
        }

        /* 새 대화 시작 버튼 스타일 */
        .sidebar .stButton > button {
            background-color: #1a73e8; /* 파란색 테마 */
            color: white;
            border: none;
            padding: 0.8rem 1.2rem;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            width: 100%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
            display: block !important;
            margin-bottom: 1rem;
        }

        .sidebar .stButton > button:hover {
            background-color: #1666c1; /* 호버 시 더 진한 파란색 */
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0,0,0,0.15);
        }

        /* 섹션 제목 스타일 */
        .section-title {
            margin-top: 1.5rem !important;
            margin-bottom: 0.8rem !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: #333333 !important;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.3rem;
        }

        /* 파일 업로드 섹션 스타일 수정 */
        .upload-section {
            display: inline-block;
            background-color: #fff9c4;
            padding: 0.4rem 0.8rem;
            margin: 0.5rem 0;
            text-align: center;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }

        /* 파일 업로더 컨테이너 스타일 */
        .stFileUploader {
            padding: 1rem;
            margin: 1rem 0;
            background-color: #fff;
            border: none;
            border-radius: 8px;
            transition: all 0.2s ease;
        }

        /* 파일 업로드 버튼 스타일 */
        .stFileUploader > label {
            display: none;
        }

        /* 처리 버튼 스타일 */
        .stForm button[type="submit"] {
            background-color: #1a73e8;
            color: white;
            border: none;
            padding: 0.6rem 1rem;
            border-radius: 5px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: background-color 0.2s, transform 0.1s, box-shadow 0.2s;
        }

        .stForm button[type="submit"]:hover {
            background-color: #1666c1;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }

        /* 파일 정보 텍스트 스타일 */
        .file-info {
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }

        /* 문서 카드 스타일 */
        .doc-card {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .doc-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }

        .doc-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
            font-size: 0.9rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .doc-info {
            font-size: 0.75rem;
            color: #666;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .doc-status {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
        }

        .status-completed {
            background-color: #e6f3e6;
            color: #2e7d32;
        }

        .status-processing {
            background-color: #fff3e0;
            color: #e65100;
        }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'dataset_id' not in st.session_state:
    st.session_state.dataset_id = None

if 'previous_plant' not in st.session_state:
    st.session_state.previous_plant = None

# 초기 세션 상태 설정
if 'dataset_id' not in st.session_state:
    try:
        st.session_state.dataset_id = st.secrets["DATASET_ID"]
    except KeyError:
        st.error('⚠️ Dataset ID가 설정되어 있지 않습니다.')
        st.stop()

if 'api_key' not in st.session_state:
    try:
        st.session_state.api_key = st.secrets["API_KEY"]
    except KeyError:
        st.error('⚠️ API 키가 설정되어 있지 않습니다.')
        st.stop()

if 'conversations' not in st.session_state:
    st.session_state.conversations = {}

if 'recent_chats' not in st.session_state:
    st.session_state.recent_chats = []

if 'conversation_id' not in st.session_state:
    # 기존 대화가 있으면 가장 최근 대화로 설정, 없으면 새로운 대화 생성
    if st.session_state.recent_chats:
        st.session_state.conversation_id = st.session_state.recent_chats[0]['id']
    else:
        new_chat_id = str(uuid.uuid4())
        st.session_state.conversation_id = new_chat_id
        st.session_state.conversations[new_chat_id] = []
        st.session_state.recent_chats.insert(0, {
            'id': new_chat_id,
            'title': "새 대화",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'messages': []
        })

# 사이드바 구성
with st.sidebar:
    # 제목 추가
    st.markdown("""
        <div style='padding: 0.8rem; background-color: #f8f9fa; border-radius: 6px; margin-bottom: 1rem;'>
            <h3 style='font-size: 1rem; color: #1a73e8; text-align: center; margin: 0;'>Gen AI TF - 설비 Manual Agent</h3>
            <div style='font-size: 0.8rem; color: #5f6368; margin-top: 0.5rem;'>
                <p style='margin: 0;'>💡 질문 예시:</p>
                <ul style='margin: 0.2rem 0; padding-left: 1rem;'>
                    <li>"~에 대해 설명해주세요"</li>
                    <li>"답변 내용으로 보고서를 작성해주세요"</li>
                    <li>"~ 대해 구글에서 검색해주세요"</li>
                    <li>"~ 대해 구글 시트로 정리해주세요"</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 새 대화 버튼
    if st.button("✨ 새 대화 시작하기", 
                key="new_chat", 
                help="새 대화를 시작합니다.",
                use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        new_chat = {
            'id': new_chat_id,
            'title': "새 대화",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'messages': []
        }
        st.session_state.recent_chats.insert(0, new_chat)
        st.session_state.conversation_id = new_chat_id
        st.session_state.conversations[new_chat_id] = []
        st.session_state['api_conversation_id'] = None  # API용 conversation_id 초기화
        st.rerun()

    # 사업장 선택 섹션
    st.markdown('<div class="section-title">🏭 사업장 선택</div>', unsafe_allow_html=True)
    selected_plant = st.radio(
        label="사업장을 선택하세요",
        options=["GS반월열병합발전", "GS구미열병합발전", "GS동해전력", "GS포천그린에너지"],
        label_visibility="collapsed"
    )

    def get_dataset_id(plant_name):
        # 매핑 딕셔너리 정의
        plant_to_key = {
            "GS포천그린에너지": "DATASET_ID_POCHEON",
            "GS동해전력": "DATASET_ID_DONGHAE",
            "GS반월열병합발전": "DATASET_ID_BANWOL",
            "GS구미열병합발전": "DATASET_ID_GUMI"
        }
        
        # 매핑된 키 가져오기
        key = plant_to_key.get(plant_name)
        if not key:
            return None
        
        return st.secrets.get(key)

    # 선택된 사업장의 dataset_id 가져오기
    dataset_id = get_dataset_id(selected_plant)

    # dataset_id가 없는 경우 처리
    if not dataset_id:
        st.error(f"{selected_plant}의 Dataset ID가 아직 설정되지 않았습니다.")
        st.stop()

    # 세션 상태에 저장
    st.session_state.dataset_id = dataset_id

    # 사업장이 변경되었을 때 이전 사업장 정보만 업데이트
    if 'previous_plant' not in st.session_state:
        st.session_state.previous_plant = selected_plant
    elif st.session_state.previous_plant != selected_plant:
        st.session_state.previous_plant = selected_plant

    # 최근 대화 섹션
    st.markdown('<div class="section-title">💬 최근 대화</div>', unsafe_allow_html=True)
    if not st.session_state.recent_chats:
        st.write("최근 대화가 없습니다.")
    else:
        for chat in st.session_state.recent_chats[:5]:
            chat_id = chat['id']
            chat_date = chat.get('date', '')
            is_selected = st.session_state.conversation_id == chat_id
            
            # 선택 버튼과 삭제 버튼을 별도로 생성
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"✅ {chat_date} ({len(st.session_state.conversations.get(chat_id, []))} 메시지)", 
                            key=f"select_{chat_id}",
                            use_container_width=True):
                    st.session_state.conversation_id = chat_id
                    st.rerun()
            
            with col2:
                if st.button("❌", key=f"delete_{chat_id}"):
                    st.session_state.recent_chats = [c for c in st.session_state.recent_chats if c['id'] != chat_id]
                    if chat_id in st.session_state.conversations:
                        del st.session_state.conversations[chat_id]
                    if st.session_state.conversation_id == chat_id:
                        if st.session_state.recent_chats:
                            st.session_state.conversation_id = st.session_state.recent_chats[0]['id']
                        else:
                            new_chat_id = str(uuid.uuid4())
                            st.session_state.conversation_id = new_chat_id
                            st.session_state.conversations[new_chat_id] = []
                            st.session_state.recent_chats.insert(0, {
                                'id': new_chat_id,
                                'title': "새 대화",
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'messages': []
                            })
                            st.session_state['api_conversation_id'] = None  # API용 conversation_id 초기화
                    st.rerun()

    # 파일 업로드 섹션 수정
    st.markdown('<div class="section-title">📁 문서 자동 전처리/업로드</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-section">배포 환경에서는 처리 속도가 느림 <br> 필요 시, 문서 메일 접수 (cjk1306@gspoge.com)</div>', unsafe_allow_html=True)
    with st.form(key='file_upload_form'):
        uploaded_files = st.file_uploader(
            "",
            type=['pdf', 'doc', 'docx', 'txt', 'md', 'ppt', 'pptx', 'hwp', 'xls', 'xlsx', 'csv'],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="file_uploader"
        )

        total_size = sum([file.size for file in uploaded_files]) if uploaded_files else 0
        files_count = len(uploaded_files) if uploaded_files else 0

        if uploaded_files:
            st.markdown(f"""
                <div class="file-info">
                    📎 {files_count}개 파일 선택됨 | 💾 총 {total_size / (1024*1024):.1f}MB
                </div>
            """, unsafe_allow_html=True)

        submit_button = st.form_submit_button(label='🗂️파일 처리 시작', use_container_width=True)

        if submit_button:
            if uploaded_files:
                # 파일 크기 검증
                invalid_files = [file.name for file in uploaded_files if file.size > 50 * 1024 * 1024]

                if invalid_files:
                    st.warning(f"⚠️ 다음 파일이 50MB를 초과합니다:\n" + "\n".join(invalid_files))
                else:
                    with st.spinner("처리 중..."):
                        try:
                            result_link = preprocess_files(uploaded_files, st.session_state.dataset_id)
                            if result_link:
                                st.success("✅ 처리 완료!")
                            else:
                                st.error("❌ 처리 실패")
                        except Exception as e:
                            st.error(f"❌ 오류 발생: {str(e)}")
            else:
                st.warning("업로드된 파일이 없습니다.")

    # 저장 문서 섹션
    st.markdown('<div class="section-title">📚 저장된 문서</div>', unsafe_allow_html=True)

    # 검색바 추가
    search_query = st.text_input("", placeholder="문서 검색...", label_visibility="collapsed")

    try:
        headers = {
            'Authorization': f'Bearer {st.secrets["KNOWLEDGE_API_KEY"]}',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            f'{API_URL}/datasets/{st.session_state.dataset_id}/documents',
            headers=headers,
            params={'page': 1, 'limit': 1000}
        )

        if response.status_code == 200:
            doc_list = response.json()
            sorted_docs = sorted(doc_list['data'], key=lambda x: x['created_at'], reverse=True)

            # 검색 필터링
            if search_query:
                sorted_docs = [doc for doc in sorted_docs if search_query.lower() in doc['name'].lower()]

            for doc in sorted_docs:
                status = "completed" if doc['indexing_status'] == 'completed' else "processing"
                status_text = "완료" if status == "completed" else "처리 중"
                status_class = "status-completed" if status == "completed" else "status-processing"
                created_at = datetime.fromtimestamp(doc['created_at']).strftime('%Y-%m-%d %H:%M')

                st.markdown(f"""
                    <div class="doc-card">
                        <div class="doc-title">{doc['name'][:50]}</div>
                        <div class="doc-info">
                            <span>{created_at} • {doc.get('word_count', 0):,}자</span>
                            <span class="doc-status {status_class}">{status_text}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"오류 발생: {str(e)}")

# 메인 화면에 대화 내용 표시
if st.session_state.conversation_id in st.session_state.conversations:
    for message in st.session_state.conversations[st.session_state.conversation_id]:
        role = message['role']
        timestamp = message.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))
        if role == 'user':
            display_user_message(message['message'], timestamp)
        else:
            display_agent_message(message['message'], timestamp)

# 자동 스크롤 위한 요소 추가
st.markdown('<div id="chat-end"></div>', unsafe_allow_html=True)
st.markdown("""
<script>
var chatEnd = document.getElementById('chat-end');
if (chatEnd) {
    chatEnd.scrollIntoView({behavior: 'smooth'});
}
</script>
""", unsafe_allow_html=True)

# 사용자 입력 받기
if prompt := st.chat_input("메시지를 입력하세요... (Enter를 눌러 전송)"):
    # conversation_id가 유효한지 확인
    if st.session_state.conversation_id not in st.session_state.conversations:
        # 유효하지 않으면 새로운 대화 생성
        new_chat_id = str(uuid.uuid4())
        st.session_state.conversation_id = new_chat_id
        st.session_state.conversations[new_chat_id] = []
        st.session_state.recent_chats.insert(0, {
            'id': new_chat_id,
            'title': "새 대화",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'messages': []
        })
        st.session_state['api_conversation_id'] = None  # API용 conversation_id 초기화

    # 사용자 메시지 표시 및 저장
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    display_user_message(prompt, timestamp)
    st.session_state.conversations[st.session_state.conversation_id].append({
        'role': 'user',
        'message': prompt,
        'timestamp': timestamp
    })

    # API 요청 부분
    assistant_placeholder = st.empty()
    answer = ''

    with st.spinner("답변을 생성 중입니다..."):
        headers = {
            'Authorization': f'Bearer {st.session_state.api_key}',
            'Content-Type': 'application/json',
        }

        data = {
            'query': prompt,
            'response_mode': 'streaming',
            'user': 'user-' + st.session_state.get('user_id', '123'),
            'inputs': {
                'location': selected_plant  # 선택된 사업장 정보 추가
            },
            'dataset_id': st.session_state.dataset_id,
            'conversation_id': st.session_state.get('api_conversation_id')  # API용 conversation_id 추가
        }

        try:
            response = requests.post(
                f'{API_URL}/chat-messages',
                headers=headers,
                json=data,
                stream=True
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        event_data = line.decode('utf-8')
                        if event_data.startswith('data:'):
                            json_data = event_data[5:].strip()
                            try:
                                event_json = json.loads(json_data)
                                event = event_json.get('event')

                                if event in ['message', 'agent_message']:
                                    answer += event_json.get('answer', '')
                                    escaped_answer = html.escape(answer)
                                    assistant_placeholder.markdown(f"""
                                    <div class="message agent-message">
                                        <div class="message-content">
                                            <div class="avatar">🤖</div>
                                            <div class="text">{escaped_answer}</div>
                                        </div>
                                        <div class="message-timestamp">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif event == 'message_end':
                                    st.session_state.conversations[st.session_state.conversation_id].append({
                                        'role': 'assistant',
                                        'message': answer,
                                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                                    })
                                    # API에서 conversation_id를 반환하면 저장
                                    api_conv_id = event_json.get('conversation_id')
                                    if api_conv_id:
                                        st.session_state['api_conversation_id'] = api_conv_id
                                    break
                            except json.JSONDecodeError:
                                continue
            else:
                st.error(f"⚠️ API 요청 실패: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ 오류 발생: {str(e)}")
            st.write(f"Error details: {traceback.format_exc()}")
