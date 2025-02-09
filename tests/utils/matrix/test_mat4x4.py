from bsp_tool.utils.matrix import Mat4x4


def test_identity():
    A = Mat4x4()
    for i in range(4):
        for j in range(4):
            if i == j:
                assert A[i][j] == 1
            else:
                assert A[i][j] == 0


def test_addition():
    # NOTE: each cell should have a unique value
    # -- this ensures we haven't messed anything up with the indices
    A = Mat4x4([
        [0x00, 0x01, 0x02, 0x03],
        [0x04, 0x05, 0x06, 0x07],
        [0x08, 0x09, 0x0A, 0x0B],
        [0x0C, 0x0D, 0x0E, 0x0F]])
    B = Mat4x4([
        [0x10, 0x11, 0x12, 0x13],
        [0x14, 0x15, 0x16, 0x17],
        [0x18, 0x19, 0x1A, 0x1B],
        [0x1C, 0x1D, 0x1E, 0x1F]])
    assert A + B == Mat4x4([
        [0x00 + 0x10, 0x01 + 0x11, 0x02 + 0x12, 0x03 + 0x13],
        [0x04 + 0x14, 0x05 + 0x15, 0x06 + 0x16, 0x07 + 0x17],
        [0x08 + 0x18, 0x09 + 0x19, 0x0A + 0x1A, 0x0B + 0x1B],
        [0x0C + 0x1C, 0x0D + 0x1D, 0x0E + 0x1E, 0x0F + 0x1F]])


def test_multiplication():
    # NOTE: this example exists on wikipedia
    # -- that multiplication is 2x3 * 3*2 => 2x2
    # -- mxn * nxp => mxp
    # -- [2 3 4][ 0 1000]   [3 2340]
    # -- [1 0 0][ 1  100] = [0 1000]
    # --        [ 0   10]
    A = Mat4x4([
        [2, 3, 4, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]])
    B = Mat4x4([
        [0, 1000, 0, 0],
        [1, 100, 0, 0],
        [0, 10, 0, 0],
        [0, 0, 0, 0]])
    assert A * B == Mat4x4([
        [3, 2340, 0, 0],
        [0, 1000, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]])
