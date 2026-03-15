# 3D 맵 엔진과 부가정보 오버레이 계층 분리 관점의 스택 추천

## 핵심 관점

기획 방향에서 중요한 기준은 **"3D 맵 엔진"과 "부가정보 오버레이 계층"을 분리해서 본다**는 점이다.

- 3D 공간 자체가 핵심 UX인지
- 지도 위에 얹는 정보 레이어와 상호작용이 핵심인지
- 데이터 카탈로그형 탐색 서비스인지

이 기준으로 보면 아래 3개 선택지가 가장 유력하다.

## 결론

가장 추천하는 우선순위는 다음과 같다.

1. `CesiumJS`: 진짜 3D 지도, 디지털트윈, 공간 시각화 중심
2. `MapLibre GL JS + deck.gl`: 웹서비스형 UI와 데이터 오버레이 중심
3. `TerriaJS`: 데이터 카탈로그, 레이어 탐색, 공공/기관형 포털 중심

## 후보별 정리

### 1. CesiumJS

추천 상황:

- 건물, 지형, 시설물, 이동체를 입체적으로 보여줘야 할 때
- "맵 위에 정보 표시" 수준이 아니라, 공간 자체가 3D 씬이어야 할 때
- 디지털트윈, 관제, 시뮬레이션, 시설 관리, 스마트시티 성격의 서비스일 때

적합한 이유:

- `3D Tiles` 기반 대규모 3D 지리 데이터 렌더링에 강하다.
- 타일 단위 `feature picking`과 속성 접근이 가능해 객체 클릭 후 상세 패널을 붙이는 패턴이 잘 맞는다.
- 지형, 건물, 시설, 이동체를 3차원 공간 안에서 다루는 UX에 적합하다.

주의:

- 일반 웹 프런트엔드 팀 기준으로 `MapLibre`보다 러닝커브가 높다.
- 단순히 "3D처럼 보이는 지도" 정도라면 과한 선택일 수 있다.

판단:

기획 의도가 **"3D 스타일"이 아니라 "3D 공간 자체가 핵심 UX"** 라면 `CesiumJS`가 1순위다.

### 2. MapLibre GL JS + deck.gl

추천 상황:

- 지도는 웹서비스처럼 매끈하게 운영하고 싶을 때
- 그 위에 포인트, 라인, 폴리곤, 아이콘, 라벨, 카드형 정보, 히트맵, 집계 시각화를 많이 얹을 예정일 때
- 부가정보가 많은 서비스일 때
- 예시: 매물, 상권, 물류, 운영현황, 관광정보, 이벤트 맵

적합한 이유:

- `MapLibre GL JS`는 WebGL 기반 지도 렌더링 라이브러리다.
- `3D terrain`과 `custom layer`를 지원한다.
- `deck.gl`과 함께 쓰면 대량 데이터 시각화 레이어 구성이 강하고, `MapLibre`와 자연스럽게 결합된다.

장점:

- 제품형 웹서비스 UI/UX를 만들기 좋다.
- React 프런트엔드와 궁합이 좋다.
- 3D 느낌, 정보 시각화, 상호작용 사이의 균형이 좋다.

한계:

- `CesiumJS` 같은 정통 3D 지구/디지털트윈 스택은 아니다.
- 복잡한 3D 객체나 정밀 공간 표현은 추가 보완이 필요하다.

판단:

**"3D 스타일 맵에 부가정보를 배치해 보여주는 웹서비스"** 라면 이 조합이 가장 현실적이다.
특히 **정보 오버레이가 주인공인 서비스**라면 `MapLibre + deck.gl`이 가장 무난하다.

### 3. TerriaJS

추천 상황:

- 여러 데이터셋을 카탈로그 형태로 관리할 때
- 사용자가 레이어를 켜고 끄고 비교하며 탐색하는 서비스일 때
- 공공/기관형 포털, 데이터 허브, 운영 포털 성격일 때

적합한 이유:

- `TerriaJS`는 `Cesium` 계열 기반의 데이터 탐색형 프레임워크다.
- `catalog item` 중심 구조가 강하다.
- `3D Tiles`도 카탈로그 아이템으로 연결할 수 있다.

한계:

- 완전히 커스텀한 소비자향 서비스 UX를 만들기에는 제약이 있을 수 있다.
- 제품형 프런트엔드보다는 플랫폼/포털 쪽 성격이 강하다.

판단:

"서비스"라기보다 **데이터 포털 / 탐색 플랫폼** 성격이라면 강한 선택지다.

## 실무 추천안

### A안. 가장 현실적인 선택

`MapLibre GL JS + deck.gl + OSM 기반 타일`

이 조합으로 다음 구성이 용이하다.

- 기본 지도
- 3D terrain / pitch / rotation
- 부가정보 레이어
- 클릭 / 호버 상세 패널
- 클러스터링 / 히트맵 / 애니메이션

적합한 서비스:

- 부동산
- 관광 / 지역정보
- 물류 / 배송 현황
- 상권 / 매장 분석
- 운영 대시보드형 지도

### B안. 3D 몰입감이 핵심일 때

`CesiumJS`

적합한 서비스:

- 건물 단위 선택
- 시설물 속성 조회
- 드론 / 차량 / 센서 이동 시각화
- 디지털트윈 / 관제 / 시뮬레이션

### C안. 포털형 / 기관형일 때

`TerriaJS`

적합한 서비스:

- 여러 데이터 소스 통합 제공
- 사용자가 데이터셋을 선택해서 탐색
- 레이어 중심 UX

## 현재 상황 기준 추천

질문이 **"3D 스타일 + 부가정보 배치 + 웹서비스"** 라는 조건에 가깝다면 1차 추천은 다음과 같다.

`MapLibre GL JS + deck.gl + React`

이유:

- 3D 느낌을 줄 수 있다.
- 정보 배치와 상호작용 UI를 설계하기 쉽다.
- 웹서비스 제품화에 유리하다.
- 과도하게 무거운 디지털트윈 스택으로 가지 않아도 된다.

다만 아래 조건이면 바로 `CesiumJS`로 가는 편이 낫다.

- 건물 / 객체 자체가 3D 모델이어야 한다.
- 지형 / 시설 / 경로를 3차원으로 정밀하게 봐야 한다.
- 디지털트윈 / 관제 성격이다.

## 추천 아키텍처 예시

### 웹서비스형

- Frontend: `React + MapLibre GL JS + deck.gl`
- Map / Data: `OpenStreetMap` 기반 타일, `GeoJSON`, `vector tile`
- Backend: `FastAPI + SQLite`, 정적 파일 서빙, 필요 시 경량 타일 서빙
- UI: 우측 상세 패널, hover tooltip, 필터, 시계열 토글

### 디지털트윈형

- Frontend: `React + CesiumJS`
- 3D Data: `3D Tiles`, terrain
- Backend: 공간 DB + 실시간 이벤트 API
- UI: 객체 선택, 속성 패널, 레이어 제어, 타임라인

## 한 줄 추천

- 정보 서비스형: `MapLibre + deck.gl`
- 정통 3D / 공간 시각화형: `CesiumJS`
- 데이터 포털형: `TerriaJS`

## 참고 링크

- CesiumJS 문서: <https://cesium.com/learn/cesiumjs/ref-doc/index.html>
- Cesium3DTileset 문서: <https://cesium.com/learn/cesiumjs/ref-doc/Cesium3DTileset.html>
- MapLibre GL JS 3D Terrain 예제: <https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/>
- deck.gl MapLibre 연동 문서: <https://deck.gl/docs/developer-guide/base-maps/using-with-maplibre>
- TerriaJS 문서: <https://docs.terria.io/guide/>

## 프로토타입 기준 개발계획

### 1. 개발 목표

본 프로토타입의 목표는 **3D 스타일의 웹 지도 위에 부가정보를 배치하여 보여주는 웹서비스**를 빠르게 검증하는 것이다.

핵심 검증 대상은 다음과 같다.

- 지도 기반 UX가 유효한지
- 부가정보 오버레이 방식이 적절한지
- 우측 상세패널, hover tooltip, 필터, 시계열 토글이 실제 사용 흐름에서 자연스러운지
- 향후 운영형 구조로 확장 가능한지

따라서 이 단계에서는 운영형 고성능 구조보다 **구축 난이도와 개발 속도**를 우선한다.

### 2. 프로토타입 아키텍처

#### Frontend

- Python 웹프레임워크 기반 템플릿
- `MapLibre GL JS`
- `deck.gl`

#### Map / Data

- `OpenStreetMap` 기반 타일
- `GeoJSON` 중심 데이터 제공
- 필요 시 일부 정적 `vector tile` 연계 검토

#### Backend

- `FastAPI`
- `SQLite`
- 필요 시 정적 파일 및 경량 타일 서빙

#### UI

- 우측 상세패널
- hover tooltip
- 필터
- 시계열 토글

### 3. 왜 SQLite를 쓰는가

프로토타입 단계에서 `PostGIS`까지 도입하면 다음 부담이 생긴다.

- DB 설치 및 운영 복잡도 증가
- 공간 스키마 설계 부담 증가
- 타일 생성과 운영 아키텍처까지 함께 검토해야 하는 부담 증가

반면 `SQLite`는 아래 장점이 있다.

- 별도 DB 서버 없이 파일 기반으로 바로 사용 가능
- 개발환경 구성이 단순함
- 샘플 데이터 적재와 수정이 빠름
- Python 백엔드와 연결이 간단함
- PoC와 프로토타입 배포가 쉬움

즉 이번 단계에서는 **DB 엔진 성능 검증보다 UX와 기능 검증이 핵심**이므로 `SQLite`가 더 적합하다.

추가로 실무 관점에서는 `SQLite` 단독보다 **`SQLite + SpatiaLite` 검토**가 더 자연스러운 확장 경로다. 다만 이번 계획서는 사용자의 요청에 맞춰 `SQLite` 중심으로 정리한다.

### 4. 프로토타입 구조의 핵심 원칙

#### 4.1 지도 데이터는 가볍게

- 초기에는 `GeoJSON` 파일 또는 `SQLite`에 저장된 좌표/속성 데이터를 API로 제공
- 지도에 필요한 최소 속성만 응답
- 대용량 데이터는 프로토타입 범위에서 제외하거나 샘플링

#### 4.2 상세정보는 별도 조회

- 지도 목록 응답에서는 `id`, `name`, `type`, `status`, `coord` 정도만 사용
- 우측 패널 상세정보는 별도 API로 조회

#### 4.3 시계열은 단순 구조로 설계

- `feature master` 테이블
- `feature_timeseries` 테이블
- 기간 필터와 토글 중심으로 우선 구현

#### 4.4 3D는 "정통 3D"가 아니라 "3D 스타일"

- `MapLibre`의 `pitch`와 `bearing`
- `fill-extrusion`
- `deck.gl` 레이어

위 요소를 활용해 3D 느낌을 구현하고, 정밀 3D 객체 모델링은 범위에서 제외한다.

### 5. 권장 기술스택

#### 5.1 Frontend

지도 및 시각화:

- `MapLibre GL JS`
- `deck.gl`

화면 구현:

- Python 서버 템플릿 렌더링 또는
- 정적 HTML + JS 조합

프로토타입 단계에서는 복잡한 SPA보다 **Python 서버 + HTML/JS 템플릿 구조**가 더 빠르다.

#### 5.2 Backend

추천:

- `FastAPI`
- `SQLite`

이유:

- API 작성이 빠름
- Swagger / OpenAPI 기반 테스트가 편함
- Python 데이터 처리와 연계가 쉬움

대안:

- `Flask`도 가능하지만, API 중심 프로토타입이면 `FastAPI`가 더 효율적이다.

#### 5.3 DB

권장 테이블:

- `features`
- `feature_details`
- `feature_timeseries`
- `categories`
- `regions`

예시 컬럼:

`features`

- `id`
- `name`
- `type`
- `status`
- `latitude`
- `longitude`
- `height`
- `summary`

`feature_details`

- `feature_id`
- `description`
- `image_url`
- `metadata_json`

`feature_timeseries`

- `id`
- `feature_id`
- `record_date`
- `metric_name`
- `metric_value`

프로토타입에서는 `geometry` 컬럼보다 **위도/경도 중심 구조**가 구현 속도 측면에서 유리하다.

### 6. 데이터 제공 방식

#### 6.1 1차 방식

- `SQLite`에서 조회
- API가 `GeoJSON` 형태로 변환해서 반환

예시 엔드포인트:

- `GET /api/features`
- `GET /api/features/{id}`
- `GET /api/features/{id}/timeseries`

이 방식이 가장 단순하다.

#### 6.2 2차 방식

- 자주 바뀌지 않는 레이어는 정적 `GeoJSON` 파일로 배포
- 상세 조회만 `SQLite` API 사용

이 방식은 구현 속도 측면에서 더 유리할 수 있다.

#### 6.3 vector tile은 필수 아님

이번 단계는 성능 최적화보다 UX 검증이 우선이므로 **`GeoJSON` 중심으로 시작**하는 것이 적절하다.

### 7. 화면 설계 방향

#### 7.1 메인 지도

- `OSM` 기반 베이스맵
- `pitch`와 `bearing` 적용
- 필요 시 건물 `extrusion`
- `deck.gl` 레이어 오버레이

#### 7.2 hover tooltip

표시 항목 예:

- 이름
- 유형
- 현재 상태
- 핵심 수치 1개

#### 7.3 우측 상세패널

표시 항목 예:

- 기본 정보
- 카테고리
- 요약 설명
- 수치 정보
- 최근 변화
- 시계열 차트
- 관련 링크 / 이미지

#### 7.4 필터

프로토타입에서는 필터를 과하게 늘리지 않고 아래 수준으로 제한한다.

- 유형
- 상태
- 기간
- 지역

#### 7.5 시계열 토글

초기에는 복잡한 재생형 플레이어보다 아래 정도가 현실적이다.

- 날짜 선택
- 기간 토글
- 최근 7일 / 30일 / 전체

### 8. API 설계안

프로토타입 기준 최소 API는 아래 정도면 충분하다.

- `GET /api/features`
  - 조건: 유형, 상태, 지역, 기간
- `GET /api/features/{id}`
- `GET /api/features/{id}/timeseries`
- `GET /api/filters`
- `GET /api/search?q=...`

초기에는 범용 API 플랫폼보다 **화면에 필요한 API를 맞춤형으로 작성**하는 편이 빠르다.

### 9. 개발 단계 계획

#### Phase 1. 요구사항 / 와이어프레임

목표:

- 지도 위 객체 정의
- 우측 패널 정보 구조 정의
- hover / click 동작 정의
- 필터 항목 정의
- 시계열 표현 방식 정의

산출물:

- 화면 와이어프레임
- 데이터 항목 정의서
- 이벤트 흐름 정의서

#### Phase 2. 기본 프로토타입 구축

목표:

- `FastAPI` 프로젝트 구성
- `SQLite` 스키마 생성 및 샘플 데이터 적재
- `MapLibre` 기반 기본 지도 화면 구성
- `GET /api/features`, `GET /api/features/{id}` 구현
- 지도 클릭 시 우측 패널 연동

산출물:

- 실행 가능한 최소 기능 데모
- 샘플 데이터셋
- 기본 조회 API

#### Phase 3. 상호작용 고도화

목표:

- hover tooltip 추가
- 필터 UI와 API 연동
- 검색 기능 추가
- 시계열 토글과 차트 연동

산출물:

- 주요 사용자 흐름이 연결된 인터랙션 데모
- 필터 / 검색 / 시계열 동작 검증본

#### Phase 4. 데이터 / 표현 보강

목표:

- 건물 extrusion 또는 강조 레이어 추가
- 정적 `GeoJSON`과 API 응답 역할 분리
- 성능 저하 구간 확인
- 향후 운영형 전환 시 병목 구간 식별

산출물:

- 시각화 개선본
- 데이터 제공 방식 정리
- 운영형 확장 포인트 메모

#### Phase 5. 검증 및 다음 단계 정리

목표:

- 사용자 시나리오 기준 UX 검토
- 응답속도와 데이터량 한계 확인
- `PostGIS` 또는 `SpatiaLite` 전환 필요 시점 정리

산출물:

- 프로토타입 검증 리포트
- 운영형 전환 조건
- 다음 버전 우선순위

### 10. 운영형 전환 기준

아래 조건이 나타나면 `SQLite` 중심 구조에서 운영형 아키텍처 전환을 검토한다.

- 데이터 건수와 동시 요청이 크게 증가할 때
- 공간 필터, 반경 검색, 폴리곤 교차 등 공간 질의가 많아질 때
- 다수 편집자 또는 배치 파이프라인이 붙을 때
- 벡터 타일 생성과 캐싱 전략이 필요할 때

이 시점의 현실적인 다음 선택지는 다음 두 가지다.

- 경량 확장: `SQLite + SpatiaLite`
- 운영형 확장: `PostGIS + tile pipeline`

### 한 줄 정리

프로토타입 단계에서는 **`MapLibre GL JS + deck.gl + FastAPI + SQLite`** 조합으로 빠르게 UX와 기능을 검증하고, 공간 질의와 운영 복잡도가 커지는 시점에 `SpatiaLite` 또는 `PostGIS`로 확장하는 전략이 가장 현실적이다.
