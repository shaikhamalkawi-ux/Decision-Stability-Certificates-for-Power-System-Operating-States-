# Preserved preparation-launch error and corrected invocation

The first invocation used the existing scientific interpreter with `-I -S`. It exited1 in3.0231947tool-wall seconds at2026-09-27T11:50:41UTC. The `-S` flag hid site-packages, so `environment()` could not locate NumPy package metadata. This occurred before `capture_inputs()`, scientific model decoding, prepared-directory creation, cut evaluation or an optimizer call. Both `prepared` and `run01` were absent at diagnosis.

The first failure record remains unchanged at `failure.json`, SHA256 `b41de7c0f0a5bedef3b78494f4e0abec3a9c2ce7d7aa04c4b81f5299c410f7ce`. It records `PackageNotFoundError`; this is a launcher flag error, not evidence that the already installed scientific environment lacks NumPy or is incompatible.

The parent explicitly authorized a corrected invocation using the same pinned interpreter and `-I` only. This is the first payload preparation, not a scientific retry. The corrected prospective command, recorded before launching, is:

```text
"C:/Users/gmalkawi/OneDrive - Higher Colleges of Technology/Documents 1/ChatGPT/3/.work/solver_env/Scripts/python.exe" -I src/researchnext_repaired_crossworld.py --prepare-only
```

Source `c64409480c5649b84620e96bfbb173d1779fca8a5a1c42eef7a2a2c7fedf6aa8`, protocol `0cb5126e78ebefaa5d259016cde7aa575ebe633be33a0da15d7b17603d10c746` and invented-fixture receipt `ffee6953079e11ec3becaa39edaae39a7a451039b2885b86ba8828de3546cde4` are unchanged. No scientific source/protocol correction accompanies this launch. Separate independent source/prepared review and root GO remain required before any cut evaluation or LP.
