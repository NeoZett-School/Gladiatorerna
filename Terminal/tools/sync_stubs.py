"""For syncing stubs."""

from pathlib import Path
import ast, textwrap

def extract_docs(source: Path):
    tree = ast.parse(source.read_text())
    docs = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            docs[node.name] = ast.get_docstring(node)
    return docs

def sync_docs(source: Path, target: Path):
    src_docs = extract_docs(source)
    target_text = target.read_text()
    for name, doc in src_docs.items():
        if doc:
            docstring = textwrap.indent(f'"""{doc}"""', "    ")
            target_text = target_text.replace(f"def {name}(", f'def {name}(\n{docstring}\n    ')
    target.write_text(target_text)