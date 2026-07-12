ARM64 Notes

- Removed `pyarrow` and `httptools` from the ARM64 requirements to avoid wheel build failures on Windows ARM64.
- Use `requirements-arm64.txt` when installing on ARM64 Windows or other environments lacking prebuilt wheels for those packages.

Quick install (PowerShell):

```
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-arm64.txt
```

If you need `pyarrow` or `httptools` later, either install prebuilt wheels or install Visual Studio Build Tools with the ARM64 toolset (see Visual Studio Installer -> "Desktop development with C++" -> MSVC v143 ARM64 toolset).
