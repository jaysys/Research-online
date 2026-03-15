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
- Backend: `PostGIS`, tile server, API 서버
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
