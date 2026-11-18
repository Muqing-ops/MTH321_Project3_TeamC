"""Regenerate data, tables, figures and evidence summaries in one command."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'results/.mplcache'))
from experiments.study import run
if __name__=='__main__':
    run()
    from experiments.validate import validate
    validate()
