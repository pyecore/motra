import pytest
import pyecore.ecore as ecore
from motra import m2m


@pytest.fixture(scope='module')
def t1():
    # Define a transformation meta-data
    t = m2m.Transformation('t1', inputs=['in_model'], outputs=['out_model'])

    @t.main
    def main(in_model, out_model):
        r_gen(in_model.contents[0])

    @t.mapping(when=lambda self: self.name.startswith('Egg'))
    def r1(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_egg'

    @t.mapping(when=lambda self: self.name.startswith('Spam'))
    def r2(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_spam'

    @t.disjunct(mappings=[r1, r2])
    def r_gen(self: ecore.EClass) -> ecore.EPackage:
        ...

    return t, r_gen


@pytest.fixture(scope='module')
def t2():
    # Define a transformation meta-data
    t = m2m.Transformation('t2', inputs=['in_model'], outputs=['out_model'])

    @t.main
    def main(in_model, out_model):
        r_gen(in_model.contents[0])

    @t.mapping(when=lambda self: self.name.startswith('Egg'))
    def r1(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_egg'

    @t.mapping(when=lambda self: self.name.startswith('Egg'))
    def r2(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_otheregg'

    @t.disjunct(mappings=[r2, r1])
    def r_gen(self: ecore.EClass) -> ecore.EPackage:
        ...

    return t, r_gen


@pytest.fixture(scope='module')
def t3():
    # Define a transformation meta-data
    t = m2m.Transformation('t3', inputs=['in_model'], outputs=['out_model'])

    @t.main
    def main(in_model, out_model):
        r_gen(in_model.contents[0])
        r_gen(in_model.contents[0])

    @t.mapping(when=lambda self: self.name.startswith('Egg'))
    def r1(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_egg'

    @t.mapping(when=lambda self: self.name.startswith('Spam'))
    def r2(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_spam'

    @t.disjunct(mappings=[r1, r2])
    def r_gen(self: ecore.EClass) -> ecore.EPackage:
        ...

    return t, r_gen


def test__disjunct_structure(t1):
    t, r_gen = t1

    # assert r_gen in t.registered_mappings  # FIXME later


def test__disjunct_dispatch(t1):
    t, r_gen = t1

    result = t.run(in_model=ecore.EClass('Spam'))
    obj_result = result.outputs.out_model.contents[0]
    assert isinstance(obj_result, ecore.EPackage)
    assert obj_result.name == 'Spam_spam'

    result = t.run(in_model=ecore.EClass('Egg'))
    obj_result = result.outputs.out_model.contents[0]
    assert isinstance(obj_result, ecore.EPackage)
    assert obj_result.name == 'Egg_egg'


def test__disjunct_mapping_order(t2):
    t, r_gen = t2

    result = t.run(in_model=ecore.EClass('Spam'))
    assert len(result.outputs.out_model.contents) == 0

    result = t.run(in_model=ecore.EClass('Egg'))
    obj_result = result.outputs.out_model.contents[0]
    assert isinstance(obj_result, ecore.EPackage)
    assert obj_result.name == 'Egg_otheregg'


def test__disjunct_mapping_cache(t3):
    t, r_gen = t3

    inparam = ecore.EClass('Spam')
    result = t.run(in_model=inparam)
    assert len(result.outputs.out_model.contents) == 1

    obj_result = result.outputs.out_model.contents[0]
    assert isinstance(obj_result, ecore.EPackage)
    assert obj_result.name == 'Spam_spam'
