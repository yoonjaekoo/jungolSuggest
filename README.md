# 정올 문제 추천기 (Jungol Recommender)

정올(jungol.co.kr) 온라인 저지 문제를 크롤링하여 난이도, 태그별로 필터링하고 개인 맞춤형 문제를 추천해주는 GUI 기반 추천 시스템입니다.

---

## 주요 기능

- **문제 크롤링**: 정올 사이트에서 전체 문제 목록을 자동으로 수집합니다.
- **맞춤 추천**: 태그, 난이도 범위, 추천 모드(랜덤/순차/쉬운순/어려운순)를 조합하여 문제를 추천합니다.
- **진행 상황 추적**: 푼 문제, 즐겨찾기, 최근 추천 이력을 관리합니다.
- **검색**: 문제 번호, 제목, 태그로 문제를 검색할 수 있습니다.
- **통계**: 전체 문제 수, 푼 문제 비율, 난이도별 분포 등의 통계를 확인합니다.
- **캐시 시스템**: 24시간 동안 유효한 JSON 캐시로 반복 크롤링을 방지합니다.

---

## 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. GUI 실행

```bash
python main.py
```

### 3. 전체 크롤링만 실행 (터미널)

```bash
python run_full_crawl.py
```

---

## 프로젝트 구조

```
jungol_recommender/
├── main.py                          # 프로젝트 진입점
├── run_full_crawl.py                # 전체 크롤링 실행 스크립트
├── requirements.txt                 # 의존성 목록
├── jungol_recommender.db           # SQLite 데이터베이스
├── cache/
│   └── problems_cache.json         # 크롤링 데이터 JSON 캐시
├── controllers/
│   └── main_controller.py          # 메인 컨트롤러 (MVC-C)
├── models/
│   └── app_model.py                # 애플리케이션 상태 및 비즈니스 로직 (MVC-M)
├── views/
│   ├── main_view.py                # 메인 레이아웃 (사이드바 + 콘텐츠 영역)
│   ├── frames/
│   │   ├── dashboard_frame.py      # 대시보드 (진행 현황 요약)
│   │   ├── recommend_frame.py      # 추천 화면
│   │   ├── search_frame.py         # 검색 화면
│   │   ├── stats_frame.py          # 통계 화면
│   │   └── settings_frame.py       # 설정 화면
│   └── components/
│       ├── tag_selector.py         # 태그 선택 컴포넌트
│       ├── tier_selector.py        # 난이도 선택 컴포넌트
│       └── recommendation_controls.py # 추천 설정 컴포넌트
├── services/
│   ├── cache_service.py            # JSON 캐시 관리
│   └── crawler_service.py          # 크롤링 + 캐시 + DB 저장 조율
├── crawler/
│   └── jungol_crawler.py           # 정올 사이트 HTTP 크롤러
└── database/
    └── database.py                 # SQLite 데이터베이스 관리
```

---

## 아키텍처 (MVC 패턴)

```
main.py → MainController (컨트롤러)
             ├── AppModel (모델): 상태 관리, 필터링, 추천 로직
             └── MainView (뷰): GUI 레이아웃 및 사용자 인터페이스
```

| 레이어 | 역할 |
|--------|------|
| **Controller** | 루트 윈도우 생성, Model과 View 연결, 앱 생명주기 관리 |
| **Model** | 문제 데이터, 사용자 선택 상태, 필터링 및 추천 알고리즘 관리 |
| **View** | 사이드바 내비게이션과 5개 탭 화면 구성 |
| **Service** | 크롤링, 캐시, DB 저장 로직 조율 |
| **Data** | HTTP 크롤링(JungolCrawler)과 SQLite 저장(DatabaseService) |

---

## 사용법

1. 앱 실행 시 자동으로 캐시를 확인하고, 없으면 정올에서 문제를 크롤링합니다.
2. **사이드바**에서 원하는 화면으로 이동합니다.
3. **추천** 탭에서 태그와 난이도 범위를 설정하고 "추천 받기" 버튼을 클릭합니다.
4. 추천된 문제의 상세 정보를 확인하고:
   - **해결 완료**: 메모와 함께 푼 문제로 기록합니다.
   - **즐겨찾기**: 관심 문제로 저장합니다.
   - **정올에서 열기**: 브라우저에서 문제 페이지를 엽니다.

---

## 추천 모드

| 모드 | 설명 |
|------|------|
| 랜덤 | 필터링된 문제에서 무작위 선택 |
| 순차 | 난이도순으로 다음 문제 선택 |
| 쉬운순 | 가장 쉬운 문제부터 추천 |
| 어려운순 | 가장 어려운 문제부터 추천 |

---

## 제외 옵션

- 푼 문제 제외
- 즐겨찾기한 문제 제외
- 최근 추천한 문제 제외
- 난이도 정보가 없는 문제 제외

---

## 난이도 체계

브론즈(Bronze) → 실버(Silver) → 골드(Gold) → 플래티넘(Platinum) → 다이아몬드(Diamond) → 루비(Ruby)

각 등급은 V(가장 쉬움) → I(가장 어려움)까지 5단계로 구분됩니다 (총 30단계).

---

## 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `customtkinter` | ≥5.2.0 | 모던 GUI 프레임워크 (다크 모드 지원) |
| `requests` | ≥2.28.0 | HTTP 요청 (크롤링) |
| `beautifulsoup4` | ≥4.11.0 | HTML 파싱 |
| `playwright` | ≥1.40.0 | 브라우저 자동화 (향후 확장용) |
| `Pillow` | ≥10.0.0 | 이미지 처리 (향후 확장용) |

---

## 데이터베이스 테이블

| 테이블 | 설명 |
|--------|------|
| `problems` | 문제 기본 정보 (번호, 제목, 저자, 난이도, 태그, 링크) |
| `solved_problems` | 푼 문제 기록 (문제 번호, 해결 날짜, 메모) |
| `favorites` | 즐겨찾기 목록 (문제 번호, 추가 날짜) |
| `recent_recommendations` | 최근 추천 이력 (문제 번호, 추천 시간) |

---

## 라이선스

이 프로젝트는 학습 및 개인 사용 목적으로 제작되었습니다.
