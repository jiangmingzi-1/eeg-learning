import importlib
import sys

print("PYTHON:", sys.version.split()[0])
print("EXE   :", sys.executable)
print("-" * 46)
for m in ["numpy", "matplotlib", "pandas", "scipy", "sklearn", "mne", "jupyter"]:
    try:
        mod = importlib.import_module(m)
        print(f"  OK    {m:12s} {getattr(mod, '__version__', '?')}")
    except Exception as e:
        print(f"  MISS  {m:12s} ({type(e).__name__})")
