from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2
from bsp_tool.extensions import compiler_signature

import pytest


from .. import files


bsps = files.local_bsps(
    RespawnBsp, {
        titanfall2: [
            "Titanfall 2"]})

bsps = {
    m: b
    for m, b in bsps.items()
    if b.signature != b""}


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_MRVNRadiant(bsp):
    """parse & replicate"""
    signature = compiler_signature.MRVNRadiant.from_bytes(bsp.signature)
    assert signature.as_bytes() == bsp.signature


bsp_signature_classes = [
    (bsp, compiler_signature.MRVNRadiant)
    for bsp in bsps.values()]


@pytest.mark.parametrize("bsp,SignatureClass", bsp_signature_classes, ids=bsps.keys())
def test_identify(bsp, SignatureClass):
    assert isinstance(compiler_signature.identify(bsp.signature), SignatureClass)
