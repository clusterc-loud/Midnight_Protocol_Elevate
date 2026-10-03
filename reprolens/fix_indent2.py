with open('reprolens/backend/main.py', 'r') as f:
    content = f.read()

# Replace the ev line in the live path (should be 12 spaces, not 8)
# The target line has        ev = (8 spaces) and needs to be 12 spaces
old = '        ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get(\"image_name\", \"reprolens-demo\"), repo_commit=paper.get(\"commit\", \"a1b2c3d\"))'
new = '            ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get(\"image_name\", \"reprolens-demo\"), repo_commit=paper.get(\"commit\", \"a1b2c3d\"))'

if old in content:
    content = content.replace(old, new)
    with open('reprolens/backend/main.py', 'w') as f:
        f.write(content)
    print('Fixed live path ev indentation')
else:
    print('Old string not found')
    # Debug: find the ev lines
    import re
    matches = re.findall(r'        ev = evidence.build_evidence[^)]+', content)
    print('Found', len(matches), 'ev lines')
    for m in matches[:3]:
        print('  ', repr(m[:60]))