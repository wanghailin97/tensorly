import tensorly as tl

from ...testing import assert_array_almost_equal, assert_raises, assert_
from ... import random
from ..import batched_tensor_dot


def test_batched_tensor_dot():
    shape = [3, 4, 2]
    vecs = [random.random_tensor((s)) for s in shape]
    tensor = random.random_tensor((shape))
    
    # Equivalence with inner product when contracting with self along all modes
    res = batched_tensor_dot(tensor, tensor, modes=3)#[[0, 1, 2], [0, 1, 2]])
    true_res = tl.tenalg.inner(tensor, tensor, n_modes=3)
    assert_array_almost_equal(true_res, res, decimal=5)
    # Equivalent to the above expression
    res = batched_tensor_dot(tensor, tensor, modes=[[0, 1, 2], [0, 1, 2]])
    assert_array_almost_equal(true_res, res, decimal=5)

    # Equivalence with n-mode-dot
    for mode, vec in enumerate(vecs):
        res = batched_tensor_dot(tensor, vec, (mode, 0))
        true_res = tl.tenalg.mode_dot(tensor, vec, mode)
        assert_array_almost_equal(true_res, res, decimal=5)
        
    # Multi-mode-dot
    res = batched_tensor_dot(batched_tensor_dot(tensor, vecs[0], (0,0)), vecs[1], (0,0))
    true_res = tl.tenalg.multi_mode_dot(tensor, vecs[:2], [0, 1])

    # Wrong number of modes
    with assert_raises(ValueError):
        batched_tensor_dot(tensor, tensor, modes=[[0, 2],[0, 1, 2]])
    
    # size mismatch
    with assert_raises(ValueError):
        batched_tensor_dot(tensor, vecs[1], modes=(0,0))

    # Test Batched tensor dot
    tensor = random.random_tensor((4, 2, 3, 3))
    tensor2 = random.random_tensor((3, 4, 2, 3))
    res = batched_tensor_dot(tensor, tensor2, ((0, 3), (1, 3)), batched_modes=(1, 2))
    # Check for each sample of the batch-size individually
    for i in range(2):
        true_res = tl.tensordot(tensor[:, i], tensor2[:, :, i], ((0, 2), (1, 2)))
        assert_array_almost_equal(res[i], true_res, decimal=5)
        
    # Test for actual tensordot
    tensor = random.random_tensor((4, 2, 3, 3))
    tensor2 = random.random_tensor((3, 4, 2, 3))
    res = batched_tensor_dot(tensor, tensor2, modes=(), batched_modes=())
    assert_(res.shape == (4, 2, 3, 3, 3, 4, 2, 3))
    res = batched_tensor_dot(tensor, tensor2, modes=(), batched_modes=((0, ), (1, )))
    assert_(res.shape == (4, 2, 3, 3, 3, 2, 3))