with open('reprolens/backend/main.py') as f:
    content = f.read()

# Fix line 200: should be 4 spaces, not 12
old = '            ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get("image_name", "reprolens-demo"), repo_commit=paper.get("commit", "a1b2c3d"))'
new = '    ev = evidence.build_evidence(claim, mapping, stdout, metric, comparison, exit_code=rc, image_digest=paper.get("image_name", "reprolens-demo"), repo_commit=paper.get("commit", "a1b2c3d"))'

content = content.replace(old, new)
with open('reprolens/backend/main.py', 'w') as f:
    f.write(content)
print('Fixed line 200')