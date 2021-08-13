import pytest
import pyecore.ecore as ecore
from motra import m2m


@pytest.fixture
def t1():
    # Define a transformation meta-data
    t = m2m.Transformation('t1', inputs=['in_model'], outputs=['out_model'])
    return t


@pytest.fixture
def t2():
    # Define a transformation meta-data
    t = m2m.Transformation('t2', inputs=['in_model', 'other_model'], outputs=['in_model', 'second_output'])
    return t


@pytest.fixture
def t3():
    # Define a transformation meta-data
    t = m2m.Transformation('t3', inputs=['in_model'], outputs=['out_model'])

    @t.mapping
    def r1(self: ecore.EClass):
        ...

    return t


def test__metadata_empty_transformation(t1):
    assert t1.inputs_def == ['in_model']
    assert t1.outputs_def == ['out_model']

    assert t1.name == 't1'
    assert t1.metamodels == set()
    assert t1.registered_mappings == []
    assert t1._main is None

    assert t1.inouts == []


def test__metadata_empty_transformation_inouts(t2):
    assert t2.inputs_def == ['in_model', 'other_model']
    assert t2.outputs_def == ['in_model', 'second_output']

    assert t2.name == 't2'
    assert t2.metamodels == set()
    assert t2.registered_mappings == []
    assert t2._main is None

    assert t2.inouts == ['in_model']


def test__metadata_one_rule(t3):
    assert t3.inputs_def == ['in_model']
    assert t3.outputs_def == ['out_model']

    assert t3.name == 't3'
    assert t3.metamodels == {ecore.eClass}
    assert len(t3.registered_mappings) == 1
