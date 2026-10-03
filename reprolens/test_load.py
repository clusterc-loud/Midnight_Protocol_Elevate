from pathlib import Path

def load_fallback(exp_id: str):
    run_dir_map = {"EXP-001": "RUN-001", "EXP-002": "RUN-002"}
    run_dir = Path(f"runs/{['RUN-001', 'RUN-002'][['EXP-001', 'EXP-002'].index(exp_id)]}")
    stdout = (Path(run_dir) / "stdout.log").read_text()
    print(f'exp_id={exp_id}')
    print(f'  run_dir={run_dir}')
    print(f'  stdout[:100]={stdout[:100]}')
    rc = 0
    wall = 0.0
    return stdout, 0, 0.0, 0

print('EXP-001:')
load_fallback('EXP-001')
print()
print('EXP-002:')
load_fallback('EXP-002')