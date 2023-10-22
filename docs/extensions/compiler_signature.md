# `extensions.compiler_signature`
Wrapper classes for comparing signatures
Compiler signatures usually appear between lump headers & the first lump
Stores some metadata such as tool versions & compile date


## MRVNRadiant
[MRVN-Radiant](https://github.com/MRVN-Radiant/MRVN-Radiant)
```python
>>> bsp = RespawnBsp(titanfall2, "tests/maps/Titanfall 2/mp_crossfire.bsp")
>>> compiler_signature.MRVNRadiant.from_bytes(bsp.signature)
<MRVNRadiant (version: 0.0.0-dev-git-bb8fb43, time: Mon Nov 28 00:35:15 2022)>
```
```
Built with love using MRVN-radiant :)
Version:        0.0.0-dev-git-bb8fb43
Time:           Mon Nov 28 00:35:15 2022
```
