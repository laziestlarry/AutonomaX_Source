#!/usr/bin/env python3
"""
Local task queue runner.

Reads a YAML file describing tasks and executes them sequentially with retries.
Logs run output to data_room/runs/<ts>_<task-name>.log

Example YAML (config/local_tasks.yaml):

tasks:
  - name: blueprint
    cmd: ./ops/generate_blueprint.sh repos repos 20
  - name: intake
    cmd: ./ops/intake_inventory.sh --filelist-glob 'repos/*.csv' --label repos
  - name: team_evidence
    cmd: ./ops/team_run_demo.sh
    env:
      CLOUD_RUN_URL: https://autonomax-api-....run.app

"""
from __future__ import annotations
import argparse, os, subprocess, time, sys
from pathlib import Path
from typing import Dict, Any, List
import yaml

def run_task(task: Dict[str, Any], log_dir: Path) -> int:
    name = task.get('name', 'task')
    cmd = task.get('cmd')
    py = task.get('python')  # optional module:function
    env = os.environ.copy()
    env.update({k:str(v) for k,v in (task.get('env') or {}).items()})
    cwd = task.get('cwd') or None
    retries = int(task.get('retries') or 0)
    timeout = int(task.get('timeout') or 0) or None
    log_path = log_dir / f"{int(time.time())}_{name}.log"
    attempts = 0
    while True:
        attempts += 1
        try:
            with open(log_path, 'a') as lf:
                lf.write(f"== START {name} attempt {attempts} ==\n")
                if cmd:
                    proc = subprocess.run(cmd, shell=True, cwd=cwd, env=env, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout)
                    rc = proc.returncode
                elif py:
                    mod, func = py.split(':', 1)
                    lf.write(f"Calling {py}\n")
                    module = __import__(mod, fromlist=[func])
                    fn = getattr(module, func)
                    res = fn()
                    lf.write(f"Result: {res}\n")
                    rc = 0
                else:
                    lf.write("No cmd or python provided\n")
                    rc = 2
                lf.write(f"== END {name} code {rc} ==\n")
            if rc == 0:
                return 0
        except subprocess.TimeoutExpired:
            with open(log_path, 'a') as lf:
                lf.write(f"Timeout for {name}\n")
        except Exception as e:
            with open(log_path, 'a') as lf:
                lf.write(f"Error in {name}: {e}\n")
        if attempts > retries:
            return rc if 'rc' in locals() else 1
        time.sleep(2)

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config/local_tasks.yaml')
    args = ap.parse_args(argv)

    conf_path = Path(args.config)
    if not conf_path.exists():
        print(f"Config not found: {conf_path}")
        return 2
    conf = yaml.safe_load(conf_path.read_text()) or {}
    tasks = conf.get('tasks') or []
    if not tasks:
        print("No tasks defined")
        return 0
    log_dir = Path('data_room/runs'); log_dir.mkdir(parents=True, exist_ok=True)
    results = []  # (name, rc)
    for t in tasks:
        name = t.get('name','task')
        print(f"Run task: {name}")
        rc = run_task(t, log_dir)
        results.append((name, rc))
        if rc != 0:
            print(f"Task failed with code {rc}")
            break
    ok = all(rc==0 for _, rc in results)
    print("All tasks complete" if ok else "Pipeline halted on failure")

    # Summary
    print("==> Local queue summary")
    for name, rc in results:
        # Find latest log for this task by prefix search
        logs = sorted(log_dir.glob(f"*_{name}.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        log_str = str(logs[0]) if logs else "<no-log>"
        print(f"  - {name}: {'ok' if rc==0 else 'fail'} • {log_str}")
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
