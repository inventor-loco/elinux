from dulwich.repo import Repo
from dulwich.porcelain import add, commit
from dulwich.index import build_index_from_tree

repo = Repo('.')

# 1. Reset the index and branch to the safe previous commit
safe_commit_id = b'83ba54063aeb149607cab093475416ed84ffab39'
safe_commit = repo[safe_commit_id]

repo.refs[b'refs/heads/main'] = safe_commit_id
build_index_from_tree(repo.path, repo.index_path(), repo.object_store, safe_commit.tree)

# 2. Write .gitignore
with open('.gitignore', 'w') as f:
    f.write("venv/\ntest_venv/\nminiconda.sh\ndataset.cache\nweights_imx_model/*\n!weights_imx_model/packerOut.zip\n__pycache__/\n")

# 3. Add valid files
add(repo.path, ['.gitignore', 'imx_linux.yaml', 'verify_and_convert.py', 'weights_imx_model/packerOut.zip', 'TODO.md', 'readme.md'])

# 4. Create the new commit
commit(
    repo.path,
    message=b"Add model conversion scripts and output artifact",
    author=b"inventor-loco <inventor-loco@users.noreply.github.com>",
    committer=b"inventor-loco <inventor-loco@users.noreply.github.com>"
)

print("Git history rewritten successfully.")
