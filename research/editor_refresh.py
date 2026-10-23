"""Bring the rulebook editor up to date with the current rulebook, waiting out a busy editor.

The editor drops a run-build request that arrives while it is already building
({"started": false, "reason": "a build is already running"}). loop_tools.refresh_editor()
starts this waiter (detached) in that case. It waits until the editor is idle, requests a
build, waits for it, and repeats while the rulebook changed during that build. One waiter at
a time (lock file); a later request finds it running and leaves the work to it.
"""
import hashlib, json, os, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULEBOOK = ROOT / 'effortless-rulebook' / 'effortless-rulebook.json'
API = 'http://localhost:42441'
LOCK = ROOT / '.logs' / 'editor-refresh.lock'
LOG = ROOT / '.logs' / 'editor-refresh.log'
DEADLINE = time.time() + 30 * 60


def log(msg):
    with LOG.open('a') as f:
        f.write(time.strftime('%H:%M:%S ') + msg + '\n')


def get(path):
    return json.load(urllib.request.urlopen(API + path, timeout=5))


def post_build():
    req = urllib.request.Request(API + '/api/admin/run-build', data=b'{}', method='POST', headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=10))


def wait_idle():
    while time.time() < DEADLINE:
        try:
            if not get('/api/admin/build-status').get('running'):
                return True
        except Exception:
            pass
        time.sleep(3)
    return False


def digest():
    return hashlib.sha256(RULEBOOK.read_bytes()).hexdigest()


def lock_held_by_live_process():
    try:
        pid = int(LOCK.read_text().strip())
        os.kill(pid, 0)
        return pid != os.getpid()
    except Exception:
        return False


def main():
    LOCK.parent.mkdir(exist_ok=True)
    if lock_held_by_live_process():
        return
    LOCK.write_text(str(os.getpid()))
    try:
        while time.time() < DEADLINE:
            if not wait_idle():
                log('gave up: editor never became idle')
                return
            if get('/api/uncommitted-status').get('pending'):
                log('skipped: unsaved admin-portal edits')
                return
            h = digest()
            r = post_build()
            if not r.get('started'):
                time.sleep(3)
                continue
            log(f'build started for rulebook {h[:12]}')
            time.sleep(5)
            wait_idle()
            if digest() == h:
                log('editor is current')
                return
            log('rulebook changed during the build; building again')
    finally:
        try:
            LOCK.unlink()
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    main()
