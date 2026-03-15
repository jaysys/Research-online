# 폴리곤 관리 시나리오 및 API 설계

## 1. 시나리오 3. 폴리곤 수정

1. 저장된 polygon 선택
2. 편집 모드 진입
3. vertex 이동 또는 속성 수정
4. 저장
5. DB update 수행

## 2. 시나리오 4. 폴리곤 삭제

1. 저장된 polygon 선택
2. 삭제 버튼 클릭
3. 삭제 확인
4. DB에서 삭제 또는 비활성 처리

---

## 3. API 설계

### 도면 조회

`GET /api/drawings`

### 특정 도면 조회

`GET /api/drawings/{drawing_id}`

### 도면별 폴리곤 목록 조회

`GET /api/drawings/{drawing_id}/polygons`

### 폴리곤 상세 조회

`GET /api/polygons/{polygon_id}`

### 폴리곤 생성

`POST /api/polygons`

Request 예시:

```json
{
  "drawing_id": 1,
  "name": "구역 A",
  "description": "관리 대상 영역",
  "polygon": {
    "type": "Polygon",
    "coordinates": [
      [
        [127.001, 37.501],
        [127.002, 37.501],
        [127.002, 37.502],
        [127.001, 37.502],
        [127.001, 37.501]
      ]
    ]
  }
}
```

### 폴리곤 수정

`PUT /api/polygons/{polygon_id}`

### 폴리곤 삭제

`DELETE /api/polygons/{polygon_id}`

### PostGIS 확장 시 추가 API 후보

`GET /api/polygons/search?intersects_bbox=minX,minY,maxX,maxY`

`POST /api/polygons/query/intersections`

용도:

- 화면 bbox 기준 polygon 빠른 검색
- 특정 polygon과 겹치는 영역 조회
- 포함, 교차, 인접 등 공간 조건 검색

---

## 4. 화면 구성

### 메인 화면

- 중앙: 도면/지도 표시 영역
- 좌측 또는 상단: 도구바
- 우측: 상세정보 패널
- 하단 또는 패널 내: 폴리곤 목록

도구바 항목:

- 그리기
- 수정
- 삭제
- 선택

### 도구바 기능

- 선택 모드
- 다각형 그리기 모드
- 편집 모드
- 삭제 모드

### 상세패널

- 영역명
- 설명
- 생성일/수정일
- 상태
- 좌표 보기
- 저장/수정/삭제 액션

---

## 5. 개발 단계 계획

### Phase 1. 요구사항 정리

- 도면 종류 정의
- 좌표 체계 정의
- polygon 입력 방식 정의
- 저장 속성 정의
- 화면 와이어프레임 정의

산출물:

- 요구사항 정의서
- 화면 설계서
- 데이터 항목 정의서

### Phase 2. 기본 환경 구축

- FastAPI 프로젝트 생성
- SQLite DB 스키마 생성
- 도면 표출 화면 구성
- 기본 MapLibre 연동

산출물:

- 개발환경
- 기본 실행 화면
- 샘플 데이터 구조

### Phase 3. 핵심 MVP 기능 구현

- polygon draw 기능
- polygon 저장 API
- polygon 목록 조회 API
- polygon 재표출 기능
- 상세정보 패널

산출물:

- 생성/조회 가능한 MVP

### Phase 4. 관리 기능 구현

- polygon 수정 기능
- polygon 삭제 기능
- 속성 편집 기능
- 목록 관리 기능

산출물:

- 관리 기능 포함 MVP

### Phase 5. 검증 및 안정화

- 예외처리
- 저장 검증
- 좌표 오류 처리
- UI 개선

산출물:

- 시연 가능한 MVP 버전

---

## 6. WBS

### 1) 기획

- 요구사항 정리
- 사용자 시나리오 정리
- 도면/영역 모델 정의
- 와이어프레임 작성

### 2) 환경 구축

- FastAPI 세팅
- SQLite 세팅
- 기본 프런트 화면 구성

### 3) 도면 표출

- MapLibre 화면 구성
- 도면 또는 배경 레이어 연결
- 줌/이동 기능 구성

### 4) 폴리곤 기능

- polygon draw
- polygon edit
- polygon select
- polygon delete

### 5) API 개발

- polygon 생성 API
- polygon 조회 API
- polygon 수정 API
- polygon 삭제 API

### 6) UI 개발

- 도구바
- 우측 상세패널
- 저장 팝업/폼
- 목록 화면

### 7) 테스트

- 저장/조회 테스트
- 좌표 정합성 테스트
- 수정/삭제 테스트
- 사용자 흐름 점검

---

## 7. MVP 성공 기준

MVP는 아래가 되면 성공입니다.

- 사용자가 웹 도면에서 영역을 직접 지정할 수 있다
- 지정한 영역이 polygon 형태로 저장된다
- 저장된 polygon을 다시 불러와 화면에 표시할 수 있다
- polygon의 이름/설명 등 기본 속성을 관리할 수 있다
- polygon 수정과 삭제가 가능하다

즉, 성공 기준은 **"영역 지정 → 저장 → 재조회 → 관리"**가 한 흐름으로 완성되는 것입니다.

---

## 8. 향후 확장 방향

- SQLite → PostGIS 전환
- 공간 교차/포함/중첩 질의 추가
- 다중 사용자 권한 관리
- 도면 버전 관리
- polygon 이력 관리
- 스타일/상태별 시각화
- 이미지 업로드 및 annotation 확장
- 실시간 협업 편집

### PostGIS 도입 시 기대 효과

- `ST_Intersects`, `ST_Contains`, `ST_Within` 기반 공간 질의 지원
- `GIST` 인덱스를 통한 대량 polygon 검색 성능 개선
- polygon 외에 point, line, multipolygon 확장 용이
- vector tile 또는 분석 파이프라인과의 연계가 쉬워짐

### PostGIS 전환 기준

- polygon 수가 증가해 전체 GeoJSON 재조회 비용이 커질 때
- 단순 CRUD를 넘어 교차/포함/거리 기반 검색이 필요할 때
- 다수 사용자가 동시에 편집하거나 조회하는 운영 환경으로 넘어갈 때

### PostGIS 전환 후 데이터 모델 예시

`polygons` 테이블에 아래 컬럼을 추가하는 방식이 현실적이다.

- `geom geometry(Polygon, 4326)`
- `properties_json jsonb`
- `created_at timestamp`
- `updated_at timestamp`

MVP의 `polygon_json` 응답 구조는 유지하고, 내부 저장과 질의만 PostGIS로 바꾸면 프런트 변경을 최소화할 수 있다.

---

## 9. 한 줄 정리

이번 MVP는 아래 문장으로 정리할 수 있습니다.

> 웹에 표출된 도면에서 사용자가 영역을 선택하거나 직접 polygon을 작성하고, 해당 polygon 좌표와 속성정보를 SQLite DB에 저장·조회·수정·삭제할 수 있는 관리형 프로토타입을 구축한다.
