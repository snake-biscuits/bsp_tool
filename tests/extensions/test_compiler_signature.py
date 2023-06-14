"""tests for bsp_tool/signature.py"""
from .. import utils
from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2
from bsp_tool.extensions import compiler_signature

import pytest


bsps = utils.get_test_maps(RespawnBsp, {titanfall2: ["Titanfall 2"]})
bsps = [b for b in bsps if b.signature != b""]


@pytest.mark.parametrize("bsp", bsps, ids=[f"Titanfall 2/{b.filename}" for b in bsps])
def test_MRVNRadiant(bsp):
    """parse & replicate"""
    signature = compiler_signature.MRVNRadiant.from_bytes(bsp.signature)
    assert signature.as_bytes() == bsp.signature


bsp_signature_classes = [(bsp, compiler_signature.MRVNRadiant) for bsp in bsps]


@pytest.mark.parametrize("bsp,SignatureClass", bsp_signature_classes, ids=[f"Titanfall 2/{b.filename}" for b in bsps])
def test_identify(bsp, SignatureClass):
    assert isinstance(compiler_signature.identify(bsp.signature), SignatureClass)
