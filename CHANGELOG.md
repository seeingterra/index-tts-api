# Changelog

All notable changes to this repository should be documented in this file.

## [Unreleased]
- docs: removed `uv`-specific instructions and Chinese content; README now focuses on Windows (PowerShell) + `venv` + `pip` workflow.
- scripts: added `scripts/setup_venv_py311.ps1` improvements:
  - Detect Microsoft Visual C++ runtime and warn about WinError 126.
  - Added `-InstallCpuTorch` flag to install CPU-only PyTorch/torchaudio wheels.
  - Added `-AutoDetectCuda` flag to detect CUDA via `nvcc` or `nvidia-smi` and install matching GPU wheels (with safe fallback to CPU wheels).
  - Broadened CUDA->torch wheel tag mapping for common CUDA versions (12.1, 12.0, 11.8, 11.7, 11.6) and nearest-compatible selection.
- ci: added `.github/workflows/ci-windows-setup-cpu.yml` to validate the CPU installation path on `windows-latest`.


## Notes
- The AutoDetectCuda detection and mapping is best-effort. If a matching GPU wheel isn't available or installation fails, the script automatically falls back to CPU wheels to ensure a working environment.
- This change was implemented on branch `seeingterra/add/vc-check-setup-venv` and is ready for PR to `index-tts/index-tts:main`.
