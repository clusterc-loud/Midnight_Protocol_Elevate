with open('reprolens/backend/main.py', 'r') as f:
    content = f.read()

old = '    ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get("image_name", "reprolens-demo"), repo_commit=paper.get("commit", "a1b2c3d"))'
new = '        ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get("image_name", "reprolens-demo"), repo_commit=paper.get("commit", "a1b2c3d"))'

if old in content:
    content = content.replace(old, new)
    with open('reprolens/backend/main.py', 'w') as f:
        f.write(content)
    print('Fixed indentation')
else:
    print('Old string not found')
    # Show what's around line 259
    idx = content.find('comparison = comparator.compare')
    if idx >= 0:
        print('Found comparison at', idx)
        print('Context:', repr(content[idx:idx+80]))