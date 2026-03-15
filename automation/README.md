# Automation

이 디렉터리는 이 저장소를 GitHub로 주기적으로 커밋하고 푸시하는 로컬 자동화 파일을 담고 있습니다.

현재 대상 저장소:
- `/Users/jaehojoo/workspace/Research-online`

현재 스케줄러 설정:
- 브랜치: `main`
- 원격 저장소: `origin`
- 실행 주기: `600`초마다 1회 (`10`분)
- `RunAtLoad`: `false`

`RunAtLoad` 는 의도적으로 꺼두었습니다. LaunchAgent 를 로드한다고 해서 즉시 커밋이나 푸시가 실행되지는 않습니다. 작업은 다음 주기에 시작되거나, `launchctl start` 로 수동 실행했을 때 시작됩니다.

## 왜 저장소를 옮겼는가

이 자동화는 macOS `launchd` 를 기준으로 구성되어 있습니다. 저장소를 `Desktop` 에서 `~/workspace` 로 옮긴 이유는, `launchd` 가 `Desktop`, `Documents`, `Downloads` 같은 macOS 보호 폴더에서 실행될 때 `Operation not permitted` 오류를 낼 수 있기 때문입니다.

저장소 경로를 다시 바꾸게 되면 다음 항목을 함께 수정해야 합니다.
- `automation/com.jaysys.research-online-autopush.plist`
- `~/Library/LaunchAgents/` 안의 심볼릭 링크

## 파일 구성

- `auto-push.sh`
  실제 작업을 수행하는 스크립트입니다. 자신의 위치를 기준으로 저장소 루트를 찾고, git 작업 흐름을 실행합니다.

- `com.jaysys.research-online-autopush.plist`
  macOS `launchd` 작업 정의 파일입니다. 이 파일이 `~/Library/LaunchAgents/` 로 심볼릭 링크됩니다.

- `logs/`
  셸 스크립트와 `launchd` 가 남기는 실행 로그 디렉터리입니다.

## 동작 원리

작업이 한 번 실행될 때마다 아래 순서로 동작합니다.

1. 저장소 루트 디렉터리로 이동합니다.
2. `.git` 디렉터리가 있는지 확인합니다.
3. `git status --porcelain` 으로 변경사항을 확인합니다.
4. 변경사항이 없으면 로그에 `no changes` 를 남기고 종료합니다.
5. 변경사항이 있으면 `git add -A` 를 실행합니다.
6. 스테이징된 내용이 있으면 `auto: 2026-03-15 17:19:38` 같은 형식의 메시지로 커밋합니다.
7. `git fetch origin` 을 실행합니다.
8. `origin/main` 이 로컬 `main` 보다 앞서 있으면 푸시를 건너뛰고 `remote is ahead, skip push` 를 로그에 남깁니다.
9. 그렇지 않으면 `git push origin main` 을 실행합니다.

즉, 이 자동화는 매번 무조건 푸시하는 방식이 아니라, 조건을 확인한 뒤에만 푸시하는 방식입니다.

## 현재 경로

실제 파일 위치:
- `/Users/jaehojoo/workspace/Research-online/automation/auto-push.sh`
- `/Users/jaehojoo/workspace/Research-online/automation/com.jaysys.research-online-autopush.plist`

LaunchAgent 심볼릭 링크 위치:
- `~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist`

심볼릭 링크가 가리켜야 하는 대상:
- `/Users/jaehojoo/workspace/Research-online/automation/com.jaysys.research-online-autopush.plist`

## 로드와 언로드

언로드:

```bash
launchctl unload ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
```

로드:

```bash
launchctl load ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
```

`plist` 를 수정한 뒤 다시 반영할 때:

```bash
launchctl unload ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
launchctl load ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
```

## 수동 실행

즉시 한 번 실행:

```bash
launchctl start com.jaysys.research-online-autopush
```

주의: 현재 저장소에 변경사항이 남아 있으면, 이 명령으로 즉시 자동 커밋과 푸시가 일어날 수 있습니다.

## 상태 확인과 진단

로드된 작업 상태 확인:

```bash
launchctl print gui/$(id -u)/com.jaysys.research-online-autopush
```

심볼릭 링크 확인:

```bash
ls -l ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
```

다음 자동 실행 전에 저장소 상태 확인:

```bash
git -C /Users/jaehojoo/workspace/Research-online status --short --branch
```

## 로그 확인

스크립트 로그:

```bash
tail -n 50 /Users/jaehojoo/workspace/Research-online/automation/logs/run.log
```

LaunchAgent 표준 출력 로그:

```bash
tail -n 50 /Users/jaehojoo/workspace/Research-online/automation/logs/launchd.out.log
```

LaunchAgent 표준 오류 로그:

```bash
tail -n 50 /Users/jaehojoo/workspace/Research-online/automation/logs/launchd.err.log
```

## 주의사항

- 이 스크립트는 `git add -A` 를 사용하므로, 추적 중인 삭제 파일과 새로 생긴 비무시 파일까지 함께 포함합니다.
- 실행 시점의 작업 트리 내용을 그대로 커밋합니다. 자동 커밋되면 안 되는 미완성 작업은 그대로 두지 않는 편이 좋습니다.
- `.env`, `venv`, 캐시 파일, `automation/logs/` 는 반드시 계속 ignore 상태를 유지해야 합니다.
- 다른 기기나 다른 사용자가 `origin/main` 에 먼저 푸시한 경우, 이 작업은 자동 병합하지 않습니다. 대신 `remote is ahead, skip push` 를 로그에 남기고 종료합니다.
- 더 엄격하게 제어하고 싶다면 LaunchAgent 는 로드해 두되 `start` 는 함부로 쓰지 말고, 민감한 작업을 할 때는 잠시 언로드하는 편이 낫습니다.

## 완전 제거

작업을 내리고 심볼릭 링크를 삭제합니다.

```bash
launchctl unload ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
rm ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
```

`automation/` 내부 파일은 LaunchAgent 를 제거한 뒤에도 저장소 안에 그대로 두어도 됩니다.
