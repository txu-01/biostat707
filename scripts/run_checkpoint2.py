"""Execute Checkpoint 2 in a fresh kernel and retain progress on failure."""
from pathlib import Path
import asyncio
import os
import sys
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
os.chdir(root)
# Direct invocation of a Pixi Python on Windows also needs its native DLL path.
library_bin = Path(sys.prefix) / 'Library' / 'bin'
if library_bin.is_dir():
    os.environ['PATH'] = str(library_bin) + os.pathsep + os.environ.get('PATH', '')
os.environ['IPYTHONDIR'] = str(root / 'output' / '.ipython_cp2')
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

path = root / 'checkpoint2.ipynb'
notebook = nbformat.read(path, as_version=4)
for cell in notebook.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None


def progress(cell, cell_index, **kwargs):
    nbformat.write(notebook, path)
    print(f'Completed cell {cell_index + 1}/{len(notebook.cells)}', flush=True)
    for output in cell.get('outputs', []):
        if output.output_type == 'stream':
            print(output.text, end='', flush=True)


client = NotebookClient(notebook, timeout=3600, kernel_name='python3',
                        resources={'metadata': {'path': str(root)}},
                        on_cell_executed=progress)
try:
    client.execute()
finally:
    nbformat.write(notebook, path)
print('Fresh-kernel notebook execution completed successfully.', flush=True)
