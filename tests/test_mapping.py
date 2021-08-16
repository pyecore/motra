import pytest
import inspect
import pyecore.ecore as ecore
from motra import m2m


@pytest.fixture
def t1():
    # Define a transformation meta-data
    t = m2m.Transformation('t1', inputs=['in_model'], outputs=['out_model'])

    @t.mapping
    def r1(self: ecore.EClass) -> ecore.EPackage:
        ...

    @t.mapping
    def r2(self: ecore.EPackage):
        ...

    @t.mapping
    def r3(self: ecore.EClass, value: int) -> ecore.EPackage:
        ...

    return t, r1, r2, r3


@pytest.fixture
def t2():
    # Define a transformation meta-data
    t = m2m.Transformation('t2', inputs=['in_model'], outputs=['out_model'])

    @t.mapping
    def r1(self: ecore.EClass) -> ecore.EPackage:
        ...

    @t.mapping
    def r1(self: ecore.EPackage) -> ecore.EClass:
        ...

    @t.mapping
    def r1(self: ecore.EStructuralFeature) -> ecore.EDataType:
        ...

    return t, r1


def test__mapping_signature(t1):
    t, r1, r2, r3 = t1

    assert r1.__mapping__ is True
    assert r1.__transformation__ is t
    assert r1.self_eclass is ecore.EClass
    assert r1.result_eclass is ecore.EPackage
    assert r1.inout is False
    assert r2.inout is True


def test__mapping_result_creation(t1):
    t, r1, r2, r3 = t1

    # Cannot run a mapping outside of a transformation
    with pytest.raises(RuntimeError):
        r1(ecore.EClass('A'))

    # Cannot run a transformation without a main
    with pytest.raises(RuntimeError):
        t.run(in_model=ecore.EClass('A'))

    # Fake main for the mapping execution
    result = None
    def fake_main(in_model, out_model):
        nonlocal result
        result = r1(in_model.contents[0])

    t._main = fake_main

    # Running a transformation requires the name of the input in the name
    with pytest.raises(KeyError):
        t.run(ecore.EClass('A'))

    t.run(in_model=ecore.EClass('A'))
    assert isinstance(result, ecore.EPackage)



def test__mapping_result_cache(t1):
    t, r1, r2, r3 = t1

    # Fake main for the mapping execution
    result1 = None
    result2 = None
    def fake_main(in_model, out_model):
        nonlocal result1
        nonlocal result2
        result1 = r1(in_model.contents[0])
        result2 = r1(in_model.contents[0])

    t._main = fake_main

    t.run(in_model=ecore.EClass('A'))
    assert isinstance(result1, ecore.EPackage)
    assert isinstance(result2, ecore.EPackage)
    assert result1 is result2


def test__mapping_result_cache_following_parameters(t1):
    t, r1, r2, r3 = t1

    # Fake main for the mapping execution
    result1 = None
    result2 = None
    result3 = None
    def fake_main(in_model, out_model):
        nonlocal result1
        nonlocal result2
        nonlocal result3
        result1 = r3(in_model.contents[0], 0)
        result2 = r3(in_model.contents[0], 1)
        result3 = r3(in_model.contents[0], 0)

    t._main = fake_main

    t.run(in_model=ecore.EClass('A'))
    assert isinstance(result1, ecore.EPackage)
    assert isinstance(result2, ecore.EPackage)
    assert isinstance(result3, ecore.EPackage)
    assert result1 is result3
    assert result1 is not result2


def test__mapping_result_inout_is_input(t1):
    t, r1, r2, r3 = t1

    # Fake main for the mapping execution
    result = None
    def fake_main(in_model, out_model):
        nonlocal result
        result = r2(self=in_model.contents[0])

    t._main = fake_main

    t.run(in_model=ecore.EPackage())
    assert isinstance(result, ecore.EPackage)


def test__mapping_bad_input(t1):
    t, r1, r2, r3 = t1

    # Fake main for the mapping execution
    result = None
    def fake_main(in_model, out_model):
        nonlocal result
        result = r1(in_model.contents[0])

    t._main = fake_main

    with pytest.raises(RuntimeError):
        t.run(in_model=ecore.EPackage())


def test__mapping_rule_overloading(t2):
    t, r1 = t2

    # Fake main for the mapping execution
    result1 = None
    result2 = None
    result3 = None
    def fake_main(in_model, out_model):
        nonlocal result1
        nonlocal result2
        nonlocal result3
        result1 = r1(ecore.EClass('A'))  # output should be an EPackage
        result2 = r1(in_model.contents[0])  # output should be an EClass
        result3 = r1(ecore.EAttribute())  # output should be an EDataType

    t._main = fake_main

    t.run(in_model=ecore.EPackage())
    assert isinstance(result1, ecore.EPackage)
    assert isinstance(result2, ecore.EClass)
    assert isinstance(result3, ecore.EDataType)
