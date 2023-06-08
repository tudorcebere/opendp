import opendp.prelude as dp

dp.enable_features('floating-point', 'contrib')


def test_binary_search_overflow():

    from opendp.domains import atom_domain, vector_domain
    from opendp.metrics import symmetric_distance
    input_domain = vector_domain(atom_domain(T=float))
    input_metric = symmetric_distance()

    d_in = 1
    d_out = 1.01
    bounded_sum = (
        dp.t.make_clamp(input_domain, input_metric, bounds=(0.0, 1.0)) >>
        dp.t.make_bounded_sum(bounds=(0.0, 1.0))
    )
    dp.binary_search_param(
        lambda s: bounded_sum >> dp.m.part_base_laplace(scale=s),
        d_in=d_in,
        d_out=d_out
    )

def test_stuck():
    from opendp.domains import atom_domain, vector_domain
    from opendp.metrics import symmetric_distance
    input_domain = vector_domain(atom_domain(T=float))
    input_metric = symmetric_distance()

    epsilon = 1.3
    sens = 500_000.0 * 500_000.0
    bounded_sum = (
        dp.t.make_clamp(input_domain, input_metric, bounds=(0.0, sens)) >>
        dp.t.make_bounded_sum(bounds=(0.0, sens))
    )
    real_v = sens / epsilon
    discovered_scale = dp.binary_search_param(
        lambda s: bounded_sum >> dp.m.part_base_laplace(scale=s),
        d_in=1,
        bounds=(0.0, real_v * 2.0),
        d_out=(epsilon))
    print(discovered_scale)
    
def test_binary_search():
    assert dp.binary_search(lambda x: x <= -5, T=int) == -5
    assert dp.binary_search(lambda x: x <= 5, T=int) == 5
    assert dp.binary_search(lambda x: x >= -5, T=int) == -5
    assert dp.binary_search(lambda x: x >= 5, T=int) == 5


def test_type_inference():
    def chainer(b):
        return dp.t.make_sized_bounded_sum(1000, (-b, b))
    assert dp.binary_search_param(chainer, 2, 100) == 50

    def mean_chainer_n(n):
        return dp.t.make_sized_bounded_mean(n, (-20., 20.))
    assert dp.binary_search_param(mean_chainer_n, 2, 1.) == 41

    def mean_chainer_b(b):
        return dp.t.make_sized_bounded_mean(1000, (-b, b))
    assert 499.999 < dp.binary_search_param(mean_chainer_b, 2, 1.) < 500.
