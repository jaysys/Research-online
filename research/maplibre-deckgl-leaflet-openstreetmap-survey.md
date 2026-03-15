# MapLibre, deck.gl, Leaflet, OpenStreetMap 조사

작성일: 2026-03-16

## 한 줄 결론

- `MapLibre`는 현대적인 웹 지도 렌더러다.
- `deck.gl`은 대용량 공간 데이터 시각화 오버레이다.
- `Leaflet`은 가볍고 단순한 2D 지도 UI 라이브러리다.
- `OpenStreetMap`은 지도 엔진이 아니라 오픈 지도 데이터와 그 생태계다.

실무에서는 이 네 개를 같은 레벨의 후보로 보면 안 된다.  
보통은 **`MapLibre 또는 Leaflet`를 베이스맵 렌더러로 고르고**, 필요하면 **`deck.gl`을 오버레이로 붙이고**, **`OpenStreetMap` 데이터/타일/지오코딩 서비스는 별도 정책에 맞게 사용**하는 식으로 조합한다.

## 역할 구분

### 1. MapLibre

- 브라우저에서 `WebGL` 기반으로 지도를 렌더링하는 오픈소스 라이브러리
- `vector tile`, `style spec`, `pitch`, `bearing`, `terrain`, `custom layer` 같은 현대적 지도 기능에 강함
- `MapLibre Style Spec` 기반으로 스타일 JSON을 다룰 수 있어 제품형 지도 UI에 적합
- `deck.gl`과의 결합성이 좋음

적합한 상황:

- 지도 자체가 제품 UX의 중심일 때
- 벡터 타일 기반으로 빠른 스타일 변경이 필요할 때
- 회전, 기울기, 3D 느낌, 라벨 제어가 중요할 때
- 향후 자체 타일 서버나 외부 벡터 타일 서비스로 확장할 때

주의:

- 타일 스타일, 소스, 폰트, 글리프 같은 지도 인프라 이해가 필요하다
- 단순 핀 몇 개 찍는 용도라면 러닝커브 대비 과할 수 있다

### 2. deck.gl

- `WebGL/WebGPU` 기반의 고성능 데이터 시각화 프레임워크
- 포인트, 라인, 폴리곤, 아이콘, 텍스트, 히트맵, 집계, `MVT`, `Trips`, `Hexagon` 같은 레이어가 강점
- 지도 엔진 자체라기보다 지도 위에 얹는 고성능 시각화 레이어에 가깝다
- `MapLibre`와 함께 쓰면 카메라 동기화와 레이어 인터리빙이 가능하다

적합한 상황:

- 수천~수백만 개 객체를 브라우저에서 시각화해야 할 때
- 시계열 이동, 밀도, 집계, 대시보드형 공간 분석이 중요할 때
- 지도보다 데이터 레이어가 핵심일 때

주의:

- 단순한 마커/팝업 중심 앱에는 무겁다
- 베이스맵 없이도 쓸 수 있지만, 일반적인 서비스에서는 보통 `MapLibre` 같은 지도 렌더러와 같이 쓴다

### 3. Leaflet

- 가볍고 단순한 오픈소스 2D 지도 라이브러리
- `TileLayer`, `Marker`, `Popup`, `Polygon`, `GeoJSON`, `WMS` 같은 기본 기능을 빠르게 붙이기 좋다
- 플러그인 생태계가 넓고 입문 난이도가 낮다
- 작은 번들 크기와 단순한 API가 장점

적합한 상황:

- 빠른 프로토타입
- 관리형 어드민 지도
- 복잡한 3D/벡터 타일 없이 2D 상호작용만 필요할 때
- GIS 전문기능보다 서비스 화면에 가까운 단순 지도일 때

주의:

- 대량 객체 렌더링과 고급 스타일링은 `MapLibre + deck.gl`보다 불리하다
- 현대적인 벡터 타일 기반 지도 제품으로 가면 구조적 한계가 빨리 온다

### 4. OpenStreetMap

- 오픈 라이선스 기반의 전 세계 지도 데이터 프로젝트
- 라이브러리가 아니라 데이터와 서비스 생태계
- 직접 쓸 수 있는 것은 크게 `지도 데이터`, `타일`, `Nominatim 지오코딩`, `Overpass API` 등으로 나뉜다

중요한 점:

- `OpenStreetMap` 데이터는 열려 있지만, `openstreetmap.org`가 제공하는 공용 타일 서버와 공용 API는 무제한 운영용 서비스가 아니다
- 상용/대규모 서비스는 보통 외부 타일 제공자나 자체 호스팅을 고려해야 한다

## 관계를 한 번에 보면

| 항목 | 역할 | 강점 | 약점 | 보통 함께 쓰는 것 |
|---|---|---|---|---|
| `MapLibre` | 지도 렌더러 | 벡터 타일, 스타일링, 회전/기울기, 제품형 지도 UX | 지도 인프라 이해 필요 | `deck.gl`, OSM 기반 타일/스타일 |
| `deck.gl` | 고성능 시각화 오버레이 | 대량 데이터, 분석형 레이어, GPU 렌더링 | 단순 지도엔 과함 | `MapLibre` |
| `Leaflet` | 경량 2D 지도 라이브러리 | 쉽고 빠름, 플러그인 풍부 | 대규모/고급 시각화 한계 | OSM 래스터 타일 |
| `OpenStreetMap` | 오픈 지도 데이터/생태계 | 데이터 개방성, 범용성, 생태계 규모 | 공용 서비스는 정책 제약 큼 | `MapLibre`, `Leaflet`, 자체 타일 서버 |

## 무엇을 선택해야 하나

### A. 현대적인 웹 지도 서비스

추천:

- `MapLibre + deck.gl + OSM 기반 벡터 타일 또는 상용 타일 서비스`

이 조합이 맞는 경우:

- 지도 위에 많은 데이터를 얹어야 한다
- 필터, hover, 선택, 애니메이션, 집계 시각화가 중요하다
- 제품형 UI와 확장성을 모두 챙겨야 한다

### B. 빠른 프로토타입 또는 단순 운영 툴

추천:

- `Leaflet + OSM 기반 래스터 타일`

이 조합이 맞는 경우:

- 마커, 폴리곤, 팝업 중심이다
- 2D 지도면 충분하다
- 구현 속도와 단순성이 가장 중요하다

### C. 지도보다 데이터 시각화가 핵심

추천:

- `MapLibre + deck.gl`

이 조합이 맞는 경우:

- 선박, 차량, 이동 경로, 밀도, 셀 집계, 대량 포인트를 보여줘야 한다
- 라벨/베이스맵과 데이터 레이어의 시각적 조합이 중요하다

## 실무 관점 비교

### 개발 난이도

- 가장 쉬움: `Leaflet`
- 중간: `MapLibre`
- 가장 높음: `MapLibre + deck.gl`

### 대량 데이터 처리

- 가장 약함: `Leaflet`
- 중간 이상: `MapLibre`
- 가장 강함: `deck.gl`

### 제품형 지도 UX

- 가장 유리함: `MapLibre`
- 데이터 시각화 확장까지 포함하면: `MapLibre + deck.gl`
- 단순 UI는 충분하지만 확장성은 낮음: `Leaflet`

### 운영 확장성

- 장기적으로 가장 안정적인 축: `MapLibre` 중심 구조
- 소규모/내부용이면 `Leaflet`도 충분

## OpenStreetMap 사용 시 반드시 알아둘 점

### 1. 데이터와 타일 서버는 다르다

- `OSM 데이터`는 `ODbL` 기반으로 사용할 수 있다
- 하지만 `tile.openstreetmap.org` 공용 타일 서버는 커뮤니티 운영 자원이라 사용 정책을 지켜야 한다

### 2. 공용 타일 서버는 운영 서비스 기본값으로 보면 안 된다

공식 타일 정책상 주의할 점:

- 정확한 타일 URL 사용
- 명확한 출처 표기 필요
- 대량 선로딩, 스크래핑, 오프라인 저장 금지
- 서비스 품질 보장 없음

실무 해석:

- 데모, 테스트, 소규모 트래픽은 가능할 수 있다
- 운영 서비스, 상용 서비스, 고트래픽 서비스는 외부 타일 제공자 또는 자체 호스팅 검토가 현실적이다

### 3. Nominatim 공용 지오코딩도 제한이 크다

공식 정책 기준:

- 절대 최대 `초당 1요청`
- 유효한 `Referer` 또는 `User-Agent` 필요
- 결과 캐시 필요
- 자동완성 API 용도로 사용 금지

실무 해석:

- 검색창 자동완성이나 대량 주소 변환에는 공용 `Nominatim`이 부적합하다
- 운영 서비스는 별도 지오코딩 제공자 또는 자체 호스팅 검토가 필요하다

### 4. Overpass API는 조회에는 강하지만 운영 의존은 주의

- 태그 기반 POI 검색, 영역 질의, 데이터 추출에 매우 유용
- 다만 공용 인스턴스는 사용량 가이드가 있고, 서비스 핵심 경로에 직접 의존하면 불안정할 수 있다

## 추천 조합

### 추천 1. 서비스형 웹 지도 기본안

- `MapLibre`
- `deck.gl`
- 외부 벡터 타일 서비스 또는 자체 타일 서버
- OSM 데이터는 타일/지오코딩/POI 소스로 활용

적합:

- SaaS, 운영 대시보드, 물류, 부동산, 관광, 상권 분석

### 추천 2. 내부 운영툴 / 빠른 MVP

- `Leaflet`
- OSM 기반 래스터 타일
- 필요 시 GeoJSON API

적합:

- 관리자 화면
- 현황판
- 지도 부가 기능이 메인 제품이 아닌 서비스

### 추천 3. 데이터 탐색형 시각화

- `MapLibre`
- `deck.gl`
- `MVT` 또는 집계 전처리된 API

적합:

- 이동체 트래킹
- 대량 센서 시각화
- 히트맵, 집계, 시계열 애니메이션

## 현재 기준 실무 판단

질문이 "무엇을 공부하고 어떤 조합으로 들어가야 하냐"에 가깝다면 우선순위는 아래가 가장 현실적이다.

1. `MapLibre`
2. `deck.gl`
3. `OpenStreetMap`의 데이터/정책 이해
4. `Leaflet`

이유:

- 지금 웹 지도 제품은 `MapLibre` 중심 설계가 확장성이 좋다
- 대량 데이터 시각화 수요가 있으면 `deck.gl`이 거의 표준적인 선택지다
- `OSM`은 단순 배경지도가 아니라 데이터/타일/검색 정책까지 같이 이해해야 실수하지 않는다
- `Leaflet`은 여전히 유효하지만, 단순 지도 앱이 아니면 장기 주력 스택으로는 한계가 더 빨리 보인다

## 참고 링크

- MapLibre GL JS Docs: <https://maplibre.org/maplibre-gl-js/docs>
- MapLibre Style Spec: <https://maplibre.org/maplibre-style-spec/>
- deck.gl Docs: <https://deck.gl/docs>
- deck.gl with MapLibre: <https://deck.gl/docs/developer-guide/base-maps/using-with-maplibre>
- Leaflet Homepage: <https://leafletjs.com/>
- Leaflet Quick Start: <https://leafletjs.com/examples/quick-start/>
- Leaflet API Reference: <https://leafletjs.com/reference>
- OpenStreetMap Copyright and License: <https://www.openstreetmap.org/copyright>
- OpenStreetMap Tile Usage Policy: <https://operations.osmfoundation.org/policies/tiles/>
- OpenStreetMap Nominatim Usage Policy: <https://operations.osmfoundation.org/policies/nominatim/>
- OpenStreetMap Overpass API Wiki: <https://wiki.openstreetmap.org/wiki/Overpass_API>

## 최종 요약

- `MapLibre`는 지도 엔진
- `deck.gl`은 데이터 시각화 오버레이
- `Leaflet`은 단순하고 가벼운 2D 지도 라이브러리
- `OpenStreetMap`은 데이터와 서비스 생태계

따라서 비교 대상이라기보다 **조합 대상**으로 보는 것이 맞다.  
새 서비스 기준 기본 추천은 `MapLibre + deck.gl + OSM 기반 데이터/타일 전략`이고, 단순 MVP라면 `Leaflet + OSM`이 가장 빠르다.
