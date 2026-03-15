# 온디바이스 VLA 지능 개발 조사자료

- 갱신일: 2026-03-15
- 조사 범위: `온디바이스 VLA(Vision-Language-Action)`의 하드웨어 스택별 아키텍처, 공개 데이터셋, 학습/증류/배포 파이프라인
- 조사 기준:
  - 공개 논문, 프로젝트 페이지, 벤더 공식 문서를 우선 참고했다.
  - 빠르게 바뀌는 제품 세대와 소프트웨어 스택은 `2026-03-15 확인 기준`으로 정리했다.
  - 설계 판단에 바로 쓰이도록 `제품 카탈로그`보다 `실제 배치 가능한 조합` 중심으로 요약했다.

## 1. 핵심 결론

- 온디바이스 VLA는 `거대 단일 모델 1개`보다 `경량 VLM/VLA + 구조화 상태 + 스킬 실행기 + 안전 계층 + 로컬 메모리` 조합이 제품화 확률이 높다.
- 하드웨어 스택은 크게 `고성능 GPU형`, `중간급 NPU/CPU형`, `초저전력 가속기형`으로 나뉘며, 각 스택마다 가능한 액션 표현과 메모리 길이가 다르다.
- 데이터는 단순 시연 수보다 `멀티카메라 동기화`, `실패 로그`, `행동 표현 일관성`, `교차-로봇 정규화`가 성능을 더 크게 좌우한다.
- 학습 파이프라인은 보통 `비로봇 VLM 사전학습 -> 로봇 데이터 SFT/BC -> 액션 헤드 적응 -> 소형 모델 증류/양자화 -> 현장 리플레이 검증` 순서가 현실적이다.

## 2. 온디바이스 VLA를 어떻게 정의할 것인가

온디바이스 VLA는 아래 입력을 같은 정책 계열에서 다룬다.

- `Vision`: RGB, depth, wrist cam, stereo, segmentation, object crop
- `Language`: 작업 지시, 제약조건, 단계 힌트, 실패 복구 규칙
- `Action`: 스킬 토큰, end-effector delta pose, base velocity, gripper action

실전 배치에서는 아래 분리가 거의 필수다.

- `VLA/VLM`: 의미 해석, 고수준 행동 선택, 서브골 생성
- `Skill/Controller`: grasp, insert, push, navigate 같은 검증된 저수준 실행
- `Safety Layer`: 충돌, 속도, joint limit, 사람 접근, 금지영역 차단
- `World State / Memory`: 객체 상태, 마지막 성공 위치, 실패 원인, 재시도 횟수

즉, 온디바이스 VLA의 본질은 `클라우드 없이 모든 걸 직접 추론`하는 것이 아니라 `클라우드 없이도 임무가 끊기지 않도록 시스템을 계층화`하는 데 있다.

## 3. 하드웨어 스택별 설계 기준

### 3.1 분류 기준

하드웨어 스택은 단순 TOPS보다 아래 조합으로 봐야 한다.

- 지속 가능한 추론 지연
- 메모리 대역폭과 VRAM/DRAM 용량
- 열 스로틀링 이후 성능 유지
- 배포 런타임 성숙도
- ROS 2, 카메라, 센서 드라이버와의 통합 난이도
- 양자화, 비전 인코더, 멀티카메라 파이프라인 지원

### 3.2 하드웨어 스택별 권장 아키텍처

| 하드웨어 계층 | 대표 스택 | 권장 모델 구조 | 권장 액션 표현 | 적합한 임무 | 주요 제약 |
| --- | --- | --- | --- | --- | --- |
| 고성능 GPU형 | NVIDIA Jetson AGX Orin / Orin NX + CUDA + TensorRT + Isaac ROS | 소형~중형 VLM/VLA, 비전 인코더 + LLM + action head, 멀티카메라 | 스킬 토큰, delta pose, base command 혼합 | 모바일 매니퓰레이터, 다단계 조작, 현장 복구 | 전력/열, 모델 메모리, 최적화 공수 |
| 중간급 CPU/NPU형 | Intel Core Ultra + OpenVINO, Apple Silicon + Core ML/MLX | 경량 VLM + 분리형 action head, 짧은 컨텍스트 | 스킬 선택, waypoint, 짧은 horizon delta | 데스크탑 로봇, 실내 서비스, 연구용 스테이션 | 멀티카메라와 긴 컨텍스트 한계 |
| 모바일 SoC형 | Qualcomm RB5/RB6/QCS 계열 + QNN/SNPE | 더 작은 VLM 또는 perception + language planner + skill policy 분리 | 스킬 토큰, FSM 기반 파라미터 | 배터리 기반 저전력 로봇, 고정된 과업 | 모델 크기, 디버깅 도구, 메모리 |
| 초저전력 가속기형 | Google Coral Edge TPU, Hailo, NXP i.MX 8M Plus NPU | perception 전용 + 규칙/소형 정책 | 스킬 호출, 안전/감지 보조 | 안전 감시, detector, 추종, 보조 인식 | 범용 VLA 직접 탑재는 사실상 어려움 |

## 4. 스택별 상세 메모

### 4.1 NVIDIA Jetson 계열

공식 Jetson 문서와 Isaac ROS/TensorRT 계열을 기준으로 보면, 현재 온디바이스 VLA 실험과 제품화 후보 중 가장 현실적인 축은 여전히 NVIDIA다.

- 강점
  - CUDA, TensorRT, Isaac ROS, 멀티카메라 파이프라인이 비교적 성숙했다.
  - 비전 인코더와 action head를 같은 GPU 메모리 위에서 돌리기 쉽다.
  - 로보틱스용 perception, SLAM, compression, transport 계층 연동 사례가 많다.
- 권장 구조
  - `camera encoder -> compact VLM/VLA -> action decoder`
  - 저수준은 별도 ROS 2 node 또는 MCU controller로 분리
  - 긴 언어 컨텍스트 대신 `구조화 상태 저장소 + 짧은 프롬프트`
- 적합한 액션 표현
  - `skill token + pose delta + gripper`
  - base가 있는 경우 `subgoal pose + local planner`
- 주의점
  - 멀티카메라와 VLM을 동시에 돌리면 열과 메모리 병목이 빨리 온다.
  - 프레임 해상도와 컨텍스트 길이를 먼저 고정하지 않으면 실시간성을 잃기 쉽다.

### 4.2 Intel Core Ultra / OpenVINO 계열

Intel OpenVINO 스택은 CPU/GPU/NPU 혼합 배치와 산업용 x86 환경 통합이 장점이다.

- 강점
  - 산업 PC, AMR, x86 기반 제어기와 결합이 쉽다.
  - OpenVINO로 vision encoder, detector, segmentation 계열 최적화가 비교적 안정적이다.
  - 로컬 서버형 로봇 스테이션에 배치하기 쉽다.
- 권장 구조
  - perception과 world-state는 OpenVINO 최적화 모델
  - 언어/의도 해석은 작은 LLM 또는 템플릿 기반 planner
  - action policy는 짧은 horizon BC head로 별도 분리
- 적합한 임무
  - 고정 셀 조작, bin-picking 보조, 실내 물류 스테이션
- 주의점
  - GPU형 대비 초장기 컨텍스트나 큰 멀티모달 모델 배치는 제한적이다.
  - 모델을 쪼개 배치하지 않으면 지연 분산이 커진다.

### 4.3 Apple Silicon 계열

Apple은 Core ML과 Apple Silicon의 메모리 구조상 소형 멀티모달 모델 실험에 유리하지만, 로봇 현장 배치용 드라이버/ROS 통합은 NVIDIA나 x86 산업 환경보다 약하다.

- 강점
  - unified memory와 on-device inference 효율이 좋아 연구용 프로토타이핑에 유리하다.
  - Core ML, MLX 기반 소형 모델 압축/실험 사이클이 빠르다.
- 권장 구조
  - 학습·검증 스테이션 또는 휴대형 데모 장비
  - 실제 로봇은 별도 제어기와 연결하고, Apple 장비는 고수준 추론만 담당
- 주의점
  - 산업 현장 센서/로봇 드라이버 통합은 별도 공수가 필요하다.
  - 완전 독립형 모바일 로봇 본체 컴퓨팅 스택으로는 제한적이다.

### 4.4 Qualcomm Robotics / 모바일 SoC 계열

Qualcomm 계열은 전력 효율은 좋지만, 범용 VLA를 한 번에 올리기보다 `planner + skill policy + detector` 분해형이 현실적이다.

- 강점
  - 배터리 기반 플랫폼에서 전력 대비 추론 효율이 좋다.
  - 카메라 ISP, 영상 파이프라인, 모바일 통합이 강하다.
- 권장 구조
  - 언어는 작은 planner
  - perception은 NPU 최적화 detector/segmenter
  - 실행은 스킬 라이브러리와 FSM
- 적합한 임무
  - 순찰, 점검, 고정 절차형 업무
- 주의점
  - 범용 VLA보다는 `제약된 과업 전용 에이전트` 방향이 적합하다.

### 4.5 Edge TPU / Hailo / NXP 저전력 계열

이 계열은 엄밀히 말해 `온디바이스 VLA 본체`보다 `온디바이스 인식/안전 보조`에 적합하다.

- 적합한 역할
  - 사람/장애물 감지
  - 특정 물체 검출
  - 자유공간/안전 감시
  - 상태 감지용 서브모듈
- 비권장 역할
  - 긴 언어 지시를 직접 이해하는 범용 VLA
  - 멀티카메라 기반 장기 조작 정책

따라서 이 계층은 `메인 VLA 연산기`가 아니라 `safety co-processor` 또는 `perception offload`로 보는 편이 맞다.

## 5. 하드웨어 계층별 권장 시스템 청사진

### 5.1 고성능 GPU형 청사진

- 센서: `front RGB + wrist RGB + depth + joint + base odom`
- 모델: `vision encoder + 3B~7B급 경량 VLM/VLA 또는 더 작은 action model`
- 메모리: 최근 수 초 영상 특징 + 구조화 상태
- 실행: 고수준 1~5 Hz, 저수준 50~200 Hz
- 액션: `pick/place/open/navigate/retry` + pose delta
- 권장 임무: 다단계 조작, 서랍/문, 간단한 이동 조작 복합 과업

### 5.2 중간급 NPU/CPU형 청사진

- 센서: `single or dual RGB + optional depth`
- 모델: `detector/segmenter + 작은 language planner + action head`
- 메모리: 상태 테이블과 직전 실패 이력만 유지
- 실행: 고수준 0.5~2 Hz, 저수준 별도 controller
- 액션: 스킬 선택, waypoint, 짧은 delta
- 권장 임무: 좁은 조작 셀, 서비스형 정형 과업

### 5.3 초저전력형 청사진

- 센서: `single RGB + safety sensor`
- 모델: detector/classifier 중심
- 메모리: 거의 없음 또는 FSM 상태만 유지
- 실행: 규칙 기반 플로우
- 액션: 안전 정지, 특정 스킬 호출, 알림
- 권장 임무: 보조 인식, 감시, 경량 트리거

## 6. 공개 데이터셋과 벤치마크

### 6.1 데이터셋 선택 원칙

온디바이스 VLA에서는 아래 속성이 중요하다.

- 멀티카메라 지원 여부
- action 표현 일관성
- robot embodiment 수
- language annotation 품질
- 실패 데이터 유무
- RLDS / Parquet / HDF5 등 학습 파이프라인 연결성

### 6.2 주요 공개 데이터셋 요약

| 데이터셋/벤치마크 | 성격 | 강점 | 한계 | 적합한 용도 |
| --- | --- | --- | --- | --- |
| Open X-Embodiment | 다기관 대규모 로봇 데이터 집합 | 다수 embodiment와 task 다양성 | action/센서 스키마 이질성 큼 | 범용 사전학습, cross-robot 정규화 |
| DROID | 대규모 실제 가정/실내 조작 데이터 | 실제 환경 다양성, 멀티카메라, 풍부한 raw data | 정제와 재라벨링 비용 큼 | 실기 조작 정책, 재현성 높은 fine-tune |
| BridgeData V2 | 실내 조작 중심 대규모 시연 | 조작 과업 표준화, BC/IL 실험에 적합 | embodiment 폭은 제한적 | manipulation 기본기 학습 |
| CALVIN | 장기 horizon language-conditioned benchmark | 멀티스텝 평가가 명확 | 주로 벤치마크 성격 | 장기 과업 계획/평가 |
| LIBERO | lifelong/transfer benchmark | 일반화와 지속학습 평가에 적합 | 실기 배치 직접성과는 거리 있음 | continual learning, transfer 평가 |
| LeRobot 생태계 | 데이터셋 + 정책 + 툴링 | 형식 통합, 재현성과 실험 속도 | 최신 대규모 VLA 전체를 대체하진 못함 | 학습 파이프라인 표준화, 빠른 재현 |

### 6.3 데이터셋별 실무 메모

#### Open X-Embodiment

Google DeepMind의 Open X-Embodiment는 다수 기관 로봇 데이터를 RLDS 형식으로 묶은 대규모 공개 집합이다. 다로봇 사전학습에는 강력하지만, 실제 fine-tuning 전에 아래 정규화가 필요하다.

- 카메라 뷰 선택 기준 통일
- action space를 `pose delta` 또는 `skill token`으로 재정의
- language 필드 정제
- episode 품질 필터링

즉, OXE는 `바로 배포할 데이터`보다 `사전학습 원천 데이터`에 가깝다.

#### DROID

DROID는 실제 환경 수집량과 장면 다양성 측면에서 매우 유용하다. 다만 raw 성격이 강해서 현장 적용 전 다음 단계가 필요하다.

- task taxonomy 재정의
- 멀티뷰 선택 또는 압축
- 실패/성공 rule 재라벨
- wrist/base 사용 여부에 따라 action head 분리

실제로는 DROID를 `현장 데이터 부트스트랩` 또는 `시각-행동 정렬 보강` 용도로 쓰는 편이 현실적이다.

#### BridgeData V2

BridgeData V2는 조작 정책의 초기 수렴성과 재현성 면에서 장점이 있다.

- 장점
  - 조작 과업이 비교적 정리돼 있다.
  - diffusion policy, BC, VLA 미세조정 비교 실험에 자주 쓰인다.
- 한계
  - 실제 제품 수준의 장기 horizon, 복합 embodiment 다양성은 제한적이다.

#### CALVIN / LIBERO

이 둘은 `현장 로그 데이터셋`보다 `평가와 일반화 측정`에 가깝다.

- CALVIN: language-conditioned long-horizon 평가에 적합
- LIBERO: lifelong, transfer, task-suite 기반 일반화 측정에 적합

실무에서는 `학습 데이터`와 `평가 벤치마크`를 분리하는 편이 좋다.

## 7. 권장 학습 파이프라인

### 7.1 전체 흐름

가장 현실적인 파이프라인은 아래 순서다.

1. 비로봇 비전-언어 또는 소형 VLM 사전학습 모델 확보
2. OXE, DROID, BridgeData V2 같은 공개 로봇 데이터로 행동 조건부 미세조정
3. 자사 하드웨어 action space에 맞게 output head 재정의
4. 현장 수집 데이터로 task-specific SFT/BC
5. 작은 모델로 distillation 또는 adapter 기반 경량화
6. INT8/INT4 또는 런타임별 컴파일
7. 로봇 리플레이/실기 A/B 테스트

### 7.2 데이터 표준화 단계

학습 전에 반드시 아래 스키마를 강제로 맞춰야 한다.

- `observation.image.front`
- `observation.image.wrist`
- `observation.state.joint`
- `observation.state.ee_pose`
- `observation.state.base`
- `language.instruction`
- `action.pose_delta`
- `action.gripper`
- `action.skill_id`
- `episode.success`
- `episode.failure_type`

이 정규화가 없으면 멀티데이터셋 혼합 학습은 성능보다 노이즈를 더 키운다.

### 7.3 액션 표현 설계

하드웨어 제약을 고려하면 아래 우선순위가 현실적이다.

1. `skill token + skill parameter`
2. `end-effector delta pose + gripper`
3. `base subgoal + local planner`
4. `joint-space direct control`은 마지막 선택지

이유는 다음과 같다.

- cross-robot 이식성이 좋다.
- 데이터 정규화가 쉽다.
- 안전 계층과 결합하기 쉽다.
- 작은 모델에서도 예측 안정성이 높다.

### 7.4 학습 방식 선택

#### Behavior Cloning / SFT

- 시작점으로 가장 안정적이다.
- 데이터 품질이 좋으면 작은 모델도 꽤 강하다.
- 온디바이스 모델 증류와 궁합이 좋다.

#### Diffusion Policy 계열

- 연속 행동의 부드러움과 멀티모달 행동 분포 표현에 강점이 있다.
- 대신 추론 스텝 수와 런타임 최적화가 문제다.
- 따라서 온디바이스에선 teacher로 쓰고 student를 증류하는 접근이 더 현실적이다.

#### Autoregressive VLA

- 언어와 행동 토큰을 통합하기 쉽다.
- 긴 horizon reasoning에 유리하다.
- 하지만 추론 지연과 KV cache 부담이 크다.

#### Offline RL / Preference Refinement

- 실패 회피, 보수적 행동, 특정 안전 규칙 반영에 유용하다.
- 다만 기본 시연 데이터 품질이 낮으면 개선폭이 제한적이다.

### 7.5 증류와 경량화

온디바이스 목적이라면 학습보다 이 단계가 더 중요하다.

- teacher: 큰 VLA/VLM 또는 diffusion policy
- student: 작은 VLM + action head 또는 스킬 분류기
- 기법
  - logits distillation
  - action regression distillation
  - QLoRA/LoRA 후 병합
  - post-training quantization
  - layer dropping
  - vision token pruning

권장 원칙은 `기능을 덜 잃는 큰 모델`보다 `현장 루프를 지키는 작은 모델`을 우선하는 것이다.

## 8. 배포 파이프라인

### 8.1 오프라인 배포 절차

1. 학습 산출물을 ONNX 또는 런타임별 포맷으로 내보낸다.
2. 타깃 장비에서 TensorRT, OpenVINO, Core ML, QNN 등으로 컴파일한다.
3. 실시간 카메라 입력 포함 벤치마크를 측정한다.
4. 열 스로틀링 상태에서 다시 측정한다.
5. safety layer와 watchdog을 붙인 상태로 hardware-in-the-loop 테스트를 한다.
6. 실패 시 롤백 가능한 패키지 단위로 배포한다.

### 8.2 런타임별 실무 포인트

- TensorRT
  - 비전 인코더, action head 최적화가 강점
  - dynamic shape를 남발하면 성능 예측이 불안정해진다
- OpenVINO
  - CPU/NPU 분산 배치에 유리
  - perception과 planner를 분리하면 운영이 편하다
- Core ML
  - Apple 장비 프로토타이핑과 소형 모델에 적합
  - 로봇 I/O 통합은 별도 브리지 필요
- QNN/SNPE
  - 모바일 SoC 최적화에 유리
  - 범용 멀티모달보다는 작은 파이프라인 분해형에 적합

## 9. 데이터 수집과 현장 루프

### 9.1 공개 데이터만으로는 부족한 이유

실제 로봇 성능을 결정하는 것은 아래 항목이다.

- 카메라 설치 위치
- 그리퍼 형상
- 제어 지연
- 마찰과 물체 분포
- 사용자 작업 문장 습관
- 안전구역과 작업 셀 구조

즉, 공개 데이터는 부트스트랩 용도이고, 배치 전에는 반드시 자사 수집 루프가 필요하다.

### 9.2 권장 수집 루프

1. teleop 시연 수집
2. 자동 리플레이 검증
3. 실패 에피소드 태깅
4. hard-negative 재학습
5. 현장 shadow mode
6. 제한된 실기 실행
7. 로그 기반 재학습

### 9.3 꼭 저장해야 할 로그

- 원본 이미지와 타임스탬프
- depth 또는 stereo 정합 정보
- joint, ee pose, base odom
- action command와 실제 실행 결과
- safety override 이벤트
- 실패 원인 코드
- 작업 지시 원문과 정규화된 instruction

## 10. 평가 지표

온디바이스 VLA는 논문 성공률만 보면 충분하지 않다. 최소 아래 지표를 같이 봐야 한다.

- task success rate
- first-try success rate
- intervention rate
- recovery success rate
- 평균 완수 시간
- action latency p50/p95
- 전력 소모와 배터리 영향
- 열 스로틀링 이후 성능 유지
- safety violation count
- unseen object / unseen layout generalization

## 11. 실무 권고안

### 11.1 지금 가장 현실적인 조합

가장 현실적인 첫 버전은 아래다.

- 하드웨어: Jetson Orin급 또는 x86 + OpenVINO급
- 모델: 소형 VLM/VLA 또는 VLM + action head 분리형
- 액션: `skill token + pose delta`
- 데이터: OXE/BridgeData/DROID로 사전학습 후 자사 데이터 미세조정
- 안전: 별도 ROS 2 safety node + watchdog
- 메모리: LLM 긴 컨텍스트 대신 구조화 상태 저장소

### 11.2 피해야 할 접근

- 범용 거대 멀티모달 모델을 그대로 엣지에 이식하려는 접근
- action space 정규화 없이 데이터셋을 섞는 접근
- safety 계층 없이 end-to-end 정책만 믿는 접근
- 성공 데이터만 모으고 실패 로그를 버리는 접근

## 12. 후속 작업 제안

- 현재 목표 로봇에 맞춘 `action schema`를 먼저 고정
- 목표 하드웨어별 `실시간 예산표` 작성
- 공개 데이터셋을 RLDS 또는 공통 parquet 형식으로 정규화
- `teacher model -> student model` 증류 실험 설계
- 실기 로그 수집용 ROS 2 recorder / replay 도구 정비

## 13. 참고 자료

아래는 이번 갱신에 직접 참고한 공개 자료다.

- NVIDIA Jetson 개발 플랫폼: https://developer.nvidia.com/embedded-computing
- NVIDIA TensorRT 문서: https://docs.nvidia.com/deeplearning/tensorrt/latest/
- NVIDIA Isaac ROS 문서: https://nvidia-isaac-ros.github.io/
- Intel OpenVINO 문서: https://docs.openvino.ai/
- Apple Core ML 문서: https://developer.apple.com/documentation/coreml
- Apple MLX: https://ml-explore.github.io/mlx/build/html/index.html
- Qualcomm AI Hub 문서: https://aihub.qualcomm.com/
- Google Coral 문서: https://coral.ai/docs/
- Hailo Developer Zone: https://hailo.ai/developer-zone/
- NXP eIQ / Edge AI 개요: https://www.nxp.com/design/design-center/software/eiq-ml-software-development-environment
- OpenVLA 프로젝트: https://openvla.github.io/
- OpenVLA GitHub: https://github.com/openvla/openvla
- Open X-Embodiment / RT-X 프로젝트: https://robotics-transformer-x.github.io/
- DROID 프로젝트: https://droid-dataset.github.io/
- BridgeData V2 프로젝트: https://bridgedata-v2.github.io/
- CALVIN 프로젝트: https://www.mees.calvin.cs.uni-freiburg.de/
- LIBERO GitHub: https://github.com/Lifelong-Robot-Learning/LIBERO
- LeRobot 문서: https://huggingface.co/docs/lerobot
