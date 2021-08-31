import pytest
import inspect
import pyecore.ecore as ecore
from motra import m2m


@pytest.fixture(scope='module')
def t1():
    # Define a transformation meta-data
    t = m2m.Transformation('t1', inputs=['in_model'], outputs=['in_model'])

    @t.mapping(when=lambda self: self.name.startswith('Egg'))
    def r1(self: ecore.EClass):
        self.name = self.name + '_egg'

    @t.mapping(when=lambda self: self.name.startswith('Spam'))
    def r1(self: ecore.EClass):
        self.name = self.name + '_spam'


    return t, r1


def test__override_with_when(t1):
    t, r1 = t1

    # Fake main for the mapping execution
    result1 = None
    result2 = None
    def fake_main(in_model):
        nonlocal result1
        nonlocal result2
        result1 = r1(ecore.EClass('Spam'))
        result2 = r1(ecore.EClass('Egg'))

    t._main = fake_main

    t.run(in_model=ecore.EPackage())
    assert result1.name == "Spam_spam"
    assert result2.name == "Egg_egg"
