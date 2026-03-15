# 온디바이스 경량 VLA 사업 권장 아키텍처 조사자료

- 작성일: 2026-03-16
- 목적: `온디바이스 경량 VLA + 국산 AI 반도체 + 제조·물류 실증` 사업에 맞는 권장 시스템 아키텍처를 외부 자료 기반으로 제시
- 기준 문서:
  - `research/on-device-vla-project-brief.md`
  - `research/on-device-vla-project-brief-analysis.md`

## 1. 핵심 결론

- 본 사업에는 `단일 초거대 end-to-end VLA`보다 `계층형 온디바이스 아키텍처`가 적합하다.
- 추천 구조는 `실시간 안전/제어 계층`과 `VLA 추론 계층`을 분리하는 방식이다.
- 로봇 본체에서는 `경량 멀티모달 이해 + 행동/스킬 생성 + 안전 감시 + 모션 실행`을 분리해야 `100ms 이하 반응`, `현장 안전성`, `국산 반도체 2종 이상 이식성`을 동시에 맞출 수 있다.
- 배포 소프트웨어는 특정 칩 전용 구조보다 `ONNX Runtime 기반 추론 추상화 + 칩별 컴파일러/런타임 어댑터` 구조가 유리하다.

## 2. 외부 자료에서 읽히는 설계 시사점

### 2.1 VLA 자체는 유효하지만, 그대로 사업 아키텍처가 되지는 않는다

- Google DeepMind의 RT-2는 로봇 행동을 텍스트 토큰처럼 표현해 vision-language model을 robotic control로 확장했다. 이는 `자연어 지시 -> 행동 토큰` 흐름의 유효성을 보여준다.
- OpenVLA도 `visual encoder + projector + LLM backbone + tokenized actions` 구조를 사용하며, 대규모 로봇 trajectory 데이터로 학습됐다.
- 다만 두 사례 모두 `대규모 모델 기반 정책`의 가능성을 보여주는 연구 레퍼런스이지, 국내 과제의 `100ms`, `국산 반도체 2종`, `제조·물류 안전 실증` 요구를 바로 만족하는 배포 아키텍처라고 보기는 어렵다.

즉, 본 사업은 `VLA 모델을 중심에 두되`, 실제 제품 아키텍처는 `모델-제어-안전-배포`를 분리한 구조로 가져가는 편이 현실적이다.

### 2.2 로봇 런타임은 ROS 2 기반 분리형 구성이 정석에 가깝다

- ROS 공식 문서는 최신 ROS 2 LTS로 `Jazzy Jalisco`를 권장하고 있다.
- ROS 2 문서는 실시간 로봇 시스템에서 deadline/jitter 관리를 위해 비결정적 연산을 피해야 한다고 설명한다.
- micro-ROS는 마이크로컨트롤러가 `hard, low-latency real-time`과 하드웨어 접근에 적합하다고 밝힌다.

따라서 고수준 VLA 추론과 저수준 안전 제어를 같은 프로세스/같은 칩/같은 스케줄러에 넣는 것은 피하는 편이 맞다.

### 2.3 복구와 재계획은 모델 내부가 아니라 실행 계층에서 다루는 편이 검증 가능하다

- Nav2 기본 behavior tree는 `1 Hz 주기 재계획 + recovery actions` 구조를 제공한다.
- BehaviorTree.CPP는 fallback/reactive fallback 같은 제어 흐름으로 복구 전략을 조합할 수 있다.
- MoveIt의 planning scene은 로봇 상태와 월드 표현을 함께 관리하며 collision checking의 중심이 된다.

즉, 현장 대응은 `VLA가 모든 상황을 직접 해결`하는 방식보다 `VLA가 상위 의도와 스킬을 만들고, 실행 계층이 재계획/복구/충돌 회피를 담당`하는 구조가 맞다.

### 2.4 국산 반도체 2종 이상 요구는 모델보다 런타임 추상화가 더 중요하다는 뜻이다

- ONNX Runtime Execution Provider 구조는 동일 API로 여러 하드웨어 백엔드를 우선순위 기반으로 사용할 수 있게 한다.
- DEEPX DX-M1은 2~5W, 25 TOPS(INT8), Ubuntu/ONNX/PyTorch/TensorFlow 지원을 내세우며 robotics를 주요 적용처로 제시한다.
- Rebellions ATOM-Lite는 edge AI inference용 저전력 가속기로 65W, 최대 256 TOPS(INT4)를 제시한다.
- Furiosa는 RNGD와 소프트웨어 스택을 통해 multimodality/LLM deployment를 지원하지만, 180W급이므로 로봇 본체 탑재보다는 개발/검증 서버 또는 게이트웨이 측 보조 용도가 더 자연스럽다.

따라서 배포 전략은 `모델 하나를 한 칩에 맞추는 방식`이 아니라 `공통 IR/공통 인터페이스 위에서 칩별 최적화`를 하는 방식이 되어야 한다.

## 3. 권장 아키텍처

### 3.1 권장 원칙

- 원칙 1: `안전/정지/회피`는 VLA 바깥의 독립 계층에서 보장
- 원칙 2: `자연어 이해`와 `행동 실행` 사이에 명시적 중간표현 삽입
- 원칙 3: `고수준 계획`과 `저수준 제어` 분리
- 원칙 4: `칩 독립 추론 인터페이스` 확보
- 원칙 5: 모든 판단과 제어 개입을 로그화해 실증 평가에 연결

### 3.2 권장 논리 구조

```text
[Operator / MES / WMS / Natural Language Mission]
                    |
                    v
        [Task Interpreter / Mission Compiler]
        - 자연어 지시 해석
        - 목표/제약/우선순위 추출
        - Goal -> Subtask -> Skill Graph 변환
                    |
                    v
        [World Model / State Estimator]
        - RGB / Depth / LiDAR / Robot State 동기화
        - 객체/장애물/사람/작업물 상태 구조화
        - MoveIt Planning Scene 갱신
                    |
          +---------+---------+
          |                   |
          v                   v
 [VLA / VLM Planner]    [Safety Supervisor]
 - 현재 상태 이해        - 사람 접근 감지
 - 다음 서브태스크 결정   - 충돌/금지영역 감시
 - skill token 생성      - 속도 제한/정지/회피 우선권
          |                   |
          +---------+---------+
                    v
         [Skill Executor / Behavior Tree]
         - grasp / place / move / inspect
         - retry / fallback / recovery
         - Nav2 / MoveIt 연동
                    |
                    v
         [Real-time Control Bridge]
         - trajectory / twist / gripper command
         - micro-ROS / MCU / PLC / servo interface
                    |
                    v
                [Robot HW]
```

## 4. 계층별 권장 구현

### 4.1 Mission Compiler 계층

역할:

- 작업 지시를 `Goal -> Subtask -> Skill Parameter`로 변환
- 예:
  - `우측 팔레트의 박스를 집어 2번 컨베이어에 적재`
  - `pick(box, zone=right_pallet) -> move(conveyor_2) -> place(slot=target)`

권장 이유:

- 사업의 `동작 분해 정확도 80% 이상` 목표는 이 계층 품질에 직접 연결된다.
- 자연어를 곧바로 joint command로 보내는 구조는 디버깅, 평가, 반도체 이식성이 모두 나쁘다.

권장 구현:

- 소형 국산 LLM/VLM 또는 경량 instruction-tuned model
- 출력 스키마는 JSON/DSL 고정
- 예외 시 rule-based validator로 schema 검증

### 4.2 World Model / Perception 계층

역할:

- 시각 정보와 로봇 상태를 구조화해 VLA 입력 토큰 수를 줄인다.
- 사람, 장애물, 작업물, 목표 영역, free space를 별도 표현으로 유지한다.

권장 이유:

- RT-2/OpenVLA는 VLA의 가능성을 보여주지만, 실제 현장 시스템은 원시 센서 전체를 매 step LLM에 넣기 어렵다.
- 제조·물류 현장은 `정밀 좌표`, `충돌 여유`, `동적 장애물` 표현이 필수다.

권장 구현:

- 고주기 센서 전처리 노드 분리
- 객체 검출, pose estimation, tracking, free-space estimation 분리
- MoveIt Planning Scene 지속 갱신

### 4.3 VLA / VLM Planner 계층

역할:

- 현재 상태와 임무를 바탕으로 `다음 서브태스크` 또는 `skill token`을 생성
- 필요 시 짧은 horizon action chunk 생성

권장 이유:

- VLA는 `의도 해석 + 상황 이해 + 다음 행동 결정`에 강점이 있다.
- 하지만 `100ms 이하 현장 반응`은 대형 단일 모델보다 `작은 planner + 별도 safety/control` 조합이 유리하다.

권장 구현:

- 후보 1: `경량 VLM + action head`
- 후보 2: `VLM planner + 별도 imitation/diffusion/ACT 계열 skill policy`
- 후보 3: 국산 멀티모달 모델을 planner로 두고 행동은 skill token으로 제한

실무 권장:

- 1차 실증은 `연속 joint action 직접 출력`보다 `skill token + parameter` 방식을 우선
- 이유: 반도체 이식, 로그 해석, 실패 복구가 더 쉽다

### 4.4 Safety Supervisor 계층

역할:

- 사람 접근, 충돌 위험, 안전구역 이탈, 작업물 낙하 가능성을 독립 감시
- 메인 planner보다 상위 우선순위로 정지/감속/우회 수행

권장 이유:

- ROS 2와 micro-ROS 문서가 시사하듯 안전·저지연 제어는 별도 실시간 경로가 필요하다.
- 본 사업의 차별점은 정확도보다 `실시간 위험 대응`에 있으므로, safety는 연구 부품이 아니라 제품 핵심이다.

권장 구현:

- ROS 2 별도 노드 + MCU/micro-ROS 경로
- 비전 기반 안전감시 + 거리센서 기반 하드 조건 감시 이중화
- safety event는 planner 출력을 즉시 preempt 가능해야 함

### 4.5 Skill Executor / Recovery 계층

역할:

- VLA가 낸 상위 명령을 실제 로봇 기능으로 실행
- 실패 시 retry, fallback, alternate path, regrasp 수행

권장 이유:

- Nav2와 BehaviorTree.CPP는 재계획/복구 구조를 이미 잘 제공한다.
- MoveIt은 manipulation planning scene과 collision check의 기준점 역할을 한다.

권장 구현:

- 이동: Nav2 BT 기반
- 조작: MoveIt 2 + hybrid planning / servo / controller bridge
- 상위 오케스트레이션: BehaviorTree.CPP 또는 SMACC2 계열 상태기계

### 4.6 Real-time Control Bridge 계층

역할:

- trajectory, twist, gripper command를 실제 제어기로 전달
- servo loop, motor control, emergency stop은 RT 계층에서 유지

권장 이유:

- ROS 2 문서는 real-time loop에서 page fault, dynamic allocation, indefinite blocking 회피를 강조한다.
- 이는 고수준 VLA 프로세스와 제어 루프를 분리해야 한다는 뜻이다.

권장 구현:

- Linux RT_PREEMPT + ROS 2 control
- 마이크로컨트롤러/PLC 구간은 micro-ROS 또는 전용 fieldbus
- e-stop, watchdog, heartbeat는 LLM/VLA와 독립

## 5. 권장 배포 아키텍처

### 5.1 소프트웨어 배포 구조

```text
Application Layer
- task interpreter
- planner service
- skill executor
- safety monitor

Middleware Layer
- ROS 2 Jazzy
- Nav2
- MoveIt 2
- BehaviorTree.CPP
- logging / telemetry

Inference Abstraction Layer
- ONNX Runtime
- provider selector
- model registry
- quantized model package

Chip Adapter Layer
- DEEPX compiler/runtime
- Rebellions SDK/runtime
- Furiosa compiler/runtime (optional server/gateway)

Hardware Layer
- edge NPU / CPU / MCU / sensors / robot controller
```

### 5.2 반도체 적용 권장안

#### 안 A. 로봇 본체 완전 온디바이스형

- 칩 1: DEEPX DX-M1(M.2 포함)
  - 저전력 perception/event model
  - 사람/장애물/작업물 감지
  - 배터리 기반 이동로봇에 적합
- 칩 2: Rebellions ATOM-Lite
  - planner/VLM 또는 더 큰 멀티모달 모델 추론
  - edge box형 로봇 컨트롤 컴퓨터에 적합

적합성:

- 사업의 `국산 AI 반도체 2종 이상`
- 로봇 본체 내 배치 가능성
- 제조·물류 현장 실증과 정합성 높음

#### 안 B. 로봇 본체 + 현장 게이트웨이 혼합형

- 로봇 본체:
  - DEEPX DX-M1 계열
  - Rebellions ATOM-Lite
- 현장 게이트웨이 또는 개발 검증 서버:
  - Furiosa RNGD

적합성:

- 교사 모델, distillation, 대형 멀티모달 비교평가, fleet analytics에 유리
- 다만 본 사업의 핵심 KPI는 로봇 본체 온디바이스이므로, 게이트웨이는 `핵심 폐루프`에서 제외해야 한다

## 6. 본 사업 기준 최종 권장안

가장 현실적인 추천은 아래 조합이다.

- `ROS 2 Jazzy + Nav2 + MoveIt 2 + BehaviorTree.CPP`를 기본 로봇 소프트웨어 골격으로 채택
- `Task Interpreter`, `VLA Planner`, `Safety Supervisor`, `Skill Executor`, `Control Bridge`를 독립 노드/서비스로 분리
- planner 출력은 `joint command`보다 `skill token + parameter`로 설계
- 추론 런타임은 `ONNX Runtime 기반 추상화`를 두고 칩별 provider/adapter로 분기
- 실시간 안전 감시와 정지 로직은 `micro-ROS/MCU/PLC` 경로로 별도 유지
- 1차년도는 `단일 작업군 2~3개`에 대해 skill library를 고정하고 planner를 경량화
- 2차년도부터 action policy와 국산 멀티모달 모델을 확장

## 7. 왜 이 구조가 본 사업에 맞는가

### 7.1 100ms 목표 대응

- perception, planner, safety, control을 분리하면 모든 loop를 같은 속도로 돌릴 필요가 없다.
- 안전/제어는 10~20ms급, planner는 50~100ms급, 미션 재계획은 0.5~1Hz급으로 분리할 수 있다.

### 7.2 국산 반도체 2종 이식 대응

- 모델을 ONNX/양자화 패키지로 관리하면 칩별 변환 경로를 통제하기 쉽다.
- application layer를 유지한 채 inference backend만 교체 가능하다.

### 7.3 실증 대응

- 실패 원인을 `인지`, `계획`, `실행`, `안전개입`으로 분리해 로그 분석 가능하다.
- 제조·물류 현장에서 과업 실패와 안전 개입을 같은 체계로 기록할 수 있다.

### 7.4 사업화 대응

- 단일 초거대 VLA보다 유지보수와 인증 대응이 쉽다.
- 로봇 종류가 바뀌어도 task DSL, skill schema, safety layer를 재사용하기 좋다.

## 8. 제안서용 문장 초안

`본 과제는 자연어 지시를 작업 목표와 스킬 그래프로 변환하는 Task Interpreter, 멀티센서 기반 World Model, 경량 VLA Planner, 독립형 Safety Supervisor, Nav2/MoveIt 기반 Skill Executor, micro-ROS 연계 Real-time Control Bridge로 구성된 계층형 온디바이스 VLA 아키텍처를 채택한다. 이를 통해 100ms 이하 현장 반응, 국산 AI 반도체 2종 이상 이식성, 제조·물류 환경 실시간 안전 대응을 동시에 확보한다.`

## 9. 참고자료

1. RT-2: Vision-Language-Action Models
   - https://robotics-transformer2.github.io/
2. OpenVLA: An Open-Source Vision-Language-Action Model
   - https://openvla.github.io/
3. ROS Developer Documentation
   - https://docs.ros.org/index.html
4. ROS 2 Understanding real-time programming
   - https://docs.ros.org/en/rolling/Tutorials/Demos/Real-Time-Programming.html
5. micro-ROS
   - https://micro.ros.org/
6. Nav2 Detailed Behavior Tree Walkthrough
   - https://docs.nav2.org/behavior_trees/overview/detailed_behavior_tree_walkthrough
7. MoveIt Planning Scene
   - https://moveit.picknik.ai/humble/api/html/planning_scene_overview.html
8. ONNX Runtime Execution Providers
   - https://onnxruntime.ai/docs/execution-providers/
9. DEEPX DX-M1
   - https://deepx.ai/products/dx-m1/
10. Rebellions ATOM-Lite / ATOM SoC
   - https://rebellions.ai/ko/rebellions-product/atom-lite/
   - https://rebellions.ai/ko/rebellions-product/atom-soc/
11. FuriosaAI RNGD
   - https://www.furiosa.ai/

## 10. 외부 자료 핵심 근거 메모

- RT-2는 행동을 텍스트 토큰으로 표현하는 VLA 접근을 제시했다.
- OpenVLA는 `visual encoder + projector + LLM + tokenized actions` 구조를 공개했다.
- ROS는 최신 ROS 2 LTS로 Jazzy를 권장한다.
- ROS 2 real-time 문서는 deadline/jitter 대응을 위해 비결정적 연산 회피를 강조한다.
- micro-ROS는 microcontroller가 hard real-time과 hardware access에 적합하다고 설명한다.
- Nav2는 기본적으로 재계획과 recovery action을 제공한다.
- MoveIt planning scene은 충돌검사와 motion planning의 중심 표현이다.
- ONNX Runtime은 execution provider 구조로 다양한 하드웨어 가속 백엔드를 같은 API로 다룬다.
- DEEPX와 Rebellions는 각각 edge/robotics 친화 저전력 또는 edge inference 가속기 포지션을 제시한다.
- Furiosa는 멀티모달/LLM 배포용 강한 소프트웨어 스택을 제공하지만, 전력 특성상 로봇 본체보다는 검증 서버 측 활용이 더 자연스럽다.
