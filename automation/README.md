# Automation

This directory contains the local automation used to periodically commit and push this repository.

Files:
- `auto-push.sh`: launchd target script
- `com.jaysys.research-online-autopush.plist`: launchd job definition
- `logs/`: runtime logs written by the script and launchd

The intended setup is:
1. Keep the real files in this directory.
2. Symlink the plist into `~/Library/LaunchAgents/`.
3. Load the job with `launchctl`.

Useful commands:

```bash
launchctl unload ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.jaysys.research-online-autopush.plist
launchctl start com.jaysys.research-online-autopush
tail -n 50 /Users/jaehojoo/workspace/Research-online/automation/logs/run.log
```
