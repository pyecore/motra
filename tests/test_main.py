import pytest
import pyecore.ecore as ecore
from motra import m2m


@pytest.fixture(scope='module')
def t1():
    # Define a transformation meta-data
    t = m2m.Transformation('t1', inputs=['in_model'], outputs=['out_model'])

    @t.main
    def main(in_model, out_model):
        r1(in_model.contents[0])

    @t.mapping
    def r1(self: ecore.EClass) -> ecore.EPackage:
        result.name = self.name + '_package'

    return t, main, r1



def test__main_structure(t1):
    t, main, r1 = t1

    assert main.__transformation__ is t
    assert t._main is main


def test__main_call_and_output_input(t1):
    t, main, r1 = t1

    result = t.run(in_model=ecore.EClass('A'))
    assert result
    assert len(result.outputs) == 1
    assert result.outputs.out_model
    assert result.outputs[0] is result.outputs.out_model
    assert len(result.inputs) == 1
    assert result.inputs.in_model
    assert result.inputs[0] is result.inputs.in_model


def test__main_call_result_object(t1):
    t, main, r1 = t1

    result = t.run(in_model=ecore.EClass('A'))
    result_obj = result.outputs.out_model.contents[0]
    assert result_obj
    assert result_obj.name == 'A_package'
