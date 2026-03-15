# Automation

이 디렉터리는 현재 저장소를 주기적으로 커밋하고 푸시하는 로컬 자동화 파일을 담고 있습니다.

핵심 목표는 저장소 폴더명이 바뀌더라도 수정 지점을 최소화하는 것입니다.

## 구성

- `autopush.env`
  브랜치, 원격 저장소, LaunchAgent 라벨처럼 환경별로 바뀔 수 있는 값을 한 곳에 모읍니다.

- `auto-push.sh`
  자신의 위치를 기준으로 저장소 루트를 계산하고, `autopush.env` 를 읽어 git 자동화 작업을 수행합니다.

- `com.jaysys.repo-autopush.plist`
  macOS `launchd` 작업 정의 파일입니다. 파일명은 예시이며, 필요하면 원하는 서비스 식별자에 맞게 바꿀 수 있습니다.

- `logs/`
  셸 스크립트가 남기는 실행 로그 디렉터리입니다.

## 변경에 강한 구조

이 구조에서는 저장소 이름이 바뀌어도 다음 영향만 관리하면 됩니다.

1. 저장소 루트는 고정 심볼릭 링크 경로를 통해 참조합니다.
2. 브랜치, 원격, LaunchAgent 라벨 변경은 `autopush.env` 에서만 수정합니다.
3. 실제 git 작업 경로와 스크립트 로그 경로는 스크립트 위치를 기준으로 자동 계산됩니다.

즉, 저장소 폴더명을 바꿀 때는 `plist` 를 직접 고치기보다 심볼릭 링크 대상만 바꾸면 됩니다.

## 설정 값

기본 설정 파일은 현재 아래 값을 가집니다.

```bash
AUTOPUSH_JOB_LABEL="com.jaysys.repo-autopush"
AUTOPUSH_BRANCH="main"
AUTOPUSH_REMOTE="origin"
```

## 심볼릭 링크

현재 구성은 아래 두 링크를 기준으로 동작합니다.

```text
/Users/jaehojoo/workspace/current-research-repo
  -> /Users/jaehojoo/workspace/Research-online

~/Library/LaunchAgents/com.jaysys.repo-autopush.plist
  -> /Users/jaehojoo/workspace/Research-online/automation/com.jaysys.repo-autopush.plist
```

저장소 폴더명이 바뀌면 첫 번째 링크만 새 실제 경로로 다시 연결하면 됩니다.

## 동작 순서

작업이 한 번 실행될 때마다 아래 순서로 동작합니다.

1. 스크립트 위치를 기준으로 저장소 루트를 찾습니다.
2. `autopush.env` 가 있으면 설정을 읽습니다.
3. `.git` 디렉터리가 있는지 확인합니다.
4. 변경사항이 없으면 로그에 `no changes` 를 남기고 종료합니다.
5. 변경사항이 있으면 `git add -A` 후 자동 커밋을 시도합니다.
6. `git fetch` 로 원격 상태를 확인합니다.
7. 원격 브랜치가 로컬보다 앞서 있으면 푸시를 건너뜁니다.
8. 그렇지 않으면 `git push` 를 실행합니다.

## 설치

LaunchAgent 심볼릭 링크 예시:

```bash
ln -sf <REPO_PATH>/automation/<PLIST_FILENAME> \
  ~/Library/LaunchAgents/<PLIST_FILENAME>
```

예시 치환값:

```text
<REPO_PATH>="/absolute/path/to/your/repo"
<PLIST_FILENAME>="com.example.repo-autopush.plist"
```

현재 저장소 기준 실제 링크:

```bash
ln -sfn /Users/jaehojoo/workspace/Research-online \
  /Users/jaehojoo/workspace/current-research-repo

ln -sfn /Users/jaehojoo/workspace/Research-online/automation/com.jaysys.repo-autopush.plist \
  ~/Library/LaunchAgents/com.jaysys.repo-autopush.plist
```

로드:

```bash
launchctl load ~/Library/LaunchAgents/<PLIST_FILENAME>
```

현재 저장소 기준 예시:

```bash
launchctl load ~/Library/LaunchAgents/com.jaysys.repo-autopush.plist
```

이 명령은 위 LaunchAgent 심볼릭 링크가 이미 연결되어 있다는 전제에서 동작합니다.

언로드:

```bash
launchctl unload ~/Library/LaunchAgents/<PLIST_FILENAME>
```

현재 저장소 기준 예시:

```bash
launchctl unload ~/Library/LaunchAgents/com.jaysys.repo-autopush.plist
```

수동 실행:

```bash
launchctl start <JOB_LABEL>
```

현재 저장소 기준 예시:

```bash
launchctl start com.jaysys.repo-autopush
```

## 상태 확인

현재 저장소 상태 확인:

```bash
git -C <REPO_PATH> status --short --branch
```

LaunchAgent 상태 확인:

```bash
launchctl print gui/$(id -u)/<JOB_LABEL>
```

## 로그 확인

스크립트 로그:

```bash
tail -n 50 <REPO_PATH>/automation/logs/run.log
```

LaunchAgent 표준 출력 로그:

```bash
tail -n 50 /tmp/<JOB_LABEL>.out.log
```

LaunchAgent 표준 오류 로그:

```bash
tail -n 50 /tmp/<JOB_LABEL>.err.log
```

플레이스홀더는 다음처럼 해석하면 됩니다.

```text
<REPO_PATH>   저장소 절대경로
<PLIST_FILENAME> LaunchAgent plist 파일명
<JOB_LABEL>   launchd 에 등록된 Label 값
```

현재 `plist` 는 저장소 실제 폴더가 아니라 `/Users/jaehojoo/workspace/current-research-repo` 를 기준 경로로 사용합니다.

## 주의사항

- 이 자동화는 `git add -A` 를 사용하므로 추적 중인 삭제 파일과 새로 생긴 비무시 파일까지 함께 포함합니다.
- 자동 커밋되면 안 되는 미완성 작업은 작업 트리에 그대로 두지 않는 편이 안전합니다.
- 다른 기기나 다른 사용자가 원격 브랜치에 먼저 푸시한 경우, 이 작업은 자동 병합하지 않고 푸시를 건너뜁니다.
