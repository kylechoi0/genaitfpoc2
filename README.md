# GS E&R POC #2

이 프로젝트는 GS E&R의 설비 매뉴얼 에이전트를 위한 Streamlit 기반의 웹 애플리케이션입니다. 사용자는 다양한 파일을 업로드하고, AI를 통해 질문을 하며, 대화 내용을 저장하고 관리할 수 있습니다.

## 기능

- 사용자와 에이전트 간의 대화 표시
- 파일 업로드 및 자동 전처리
- 최근 대화 기록 관리
- 사업장 선택 및 관련 데이터셋 사용
- API를 통한 AI 응답 생성

## 설치

1. 이 저장소를 클론합니다:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. 필요한 패키지를 설치합니다:

   ```bash
   pip install -r requirements.txt
   ```

3. `.streamlit/secrets.toml` 파일을 생성하고, `secrets.toml.example` 파일을 참고하여 API 키와 데이터셋 ID를 설정합니다.

## 사용법

1. 애플리케이션을 실행합니다:

   ```bash
   streamlit run main.py
   ```

2. 웹 브라우저에서 `http://localhost:8501`에 접속하여 애플리케이션을 사용합니다.

## 파일 구조

```
your-repo-name/
│
├── main.py                  # 메인 애플리케이션 파일
├── file_preprocessing.py     # 파일 전처리 모듈
├── document_list.py          # 문서 리스트 조회 모듈
├── utils/                    # 유틸리티 함수들
│   └── session_state.py      # 세션 상태 관리 모듈
├── .gitignore               # Git에 포함되지 않을 파일 목록
├── requirements.txt         # 필요한 패키지 목록
└── .streamlit/
    ├── secrets.toml        # API 키 및 비밀 정보 (비공개)
    └── secrets.toml.example # secrets.toml의 예시
```

## 문의

- GS E&R 52g Crew Kyle (최정규 주임 / kyle@52g.team)
