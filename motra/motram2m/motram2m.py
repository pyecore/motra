"""Definition of meta model 'motram2m'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *
import ast
import importlib



name = 'motram2m'
nsURI = 'http://motra/m2m/1.0'
nsPrefix = 'motram2m'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)
DirectionKind = EEnum('DirectionKind', literals=['IN', 'OUT', 'INOUT'])


PythonAST = EDataType('PythonAST', eType=ast.AST, from_string=lambda code: ast.parse(code).body[0], to_string=ast.unparse)


def load_class(s):
    package, cls = s.split('#')
    if package == 'builtins' and cls == 'function':
        return type(load_class)
    return getattr(importlib.import_module(package), cls)

Ecore.EJavaClass.from_string = load_class
Ecore.EJavaClass.to_string = lambda x: f"{x.__module__}#{x.__name__}"


class Namedelement(EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)

    def __init__(self, *, name=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name


@abstract
class PythonBody(EObject, metaclass=MetaEClass):

    body = EAttribute(eType=PythonAST, unique=True, derived=False, changeable=True)

    def __init__(self, *, body=None, **kwargs):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__(**kwargs)

        if body is not None:
            self.body = body

    def to_source(self):
        return ast.unparse(self.body)


class DerivedInputs(EDerivedCollection):
    def _get_collection(self):
        return [e for e in self.parameters if e.direction in (DirectionKind.IN, DirectionKind.INOUT)]

    def __len__(self):
        return len(self._get_collection())

    def __getitem__(self, index):
        return self._get_collection()[index]

    def __repr__(self):
        return 'DerivedCollection({})'.format(self._get_collection())


class DerivedOutputs(EDerivedCollection):
    def _get_collection(self):
       return [e for e in self.parameters if e.direction in (DirectionKind.OUT, DirectionKind.INOUT)]

    def __len__(self):
       return len(self._get_collection())

    def __getitem__(self, index):
       return self._get_collection()[index]

    def __repr__(self):
       return 'DerivedCollection({})'.format(self._get_collection())


class DerivedInouts(EDerivedCollection):
    def _get_collection(self):
       return [e for e in self.parameters if e.direction is DirectionKind.INOUT]

    def __len__(self):
       return len(self._get_collection())

    def __getitem__(self, index):
       return self._get_collection()[index]

    def __repr__(self):
       return 'DerivedCollection({})'.format(self._get_collection())


class Transformation(Namedelement):

    rules = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)
    inputs = EReference(ordered=True, unique=True, containment=True,
                        derived=True, upper=-1, derived_class=DerivedInputs)
    outputs = EReference(ordered=True, unique=True, containment=True,
                         derived=True, upper=-1, derived_class=DerivedOutputs)
    inouts = EReference(ordered=True, unique=True, containment=True,
                         derived=True, upper=-1, derived_class=DerivedInouts)
    main = EReference(ordered=True, unique=True, containment=True, derived=False)
    parameters = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)

    def __init__(self, *, rules=None, inputs=None, outputs=None, main=None, parameters=None, **kwargs):

        super().__init__(**kwargs)

        if rules:
            self.rules.extend(rules)

        if inputs:
            self.inputs.extend(inputs)

        if outputs:
            self.outputs.extend(outputs)

        if main is not None:
            self.main = main

        if parameters:
            self.parameters.extend(parameters)


class RuleParameter(Namedelement):

    native_type = EAttribute(eType=EJavaClass, unique=True, derived=False, changeable=True)
    eobject_type = EReference(eType=EClass)
    _type = EAttribute(eType=EJavaObject, unique=True, derived=True, changeable=True, name='type')

    @property
    def type(self):
        if self.eobject_type:
            return self.eobject_type
        return self.native_type

    @type.setter
    def type(self, value):
        if isinstance(value, Ecore.EObject):
            self.eobject_type = value
        elif hasattr(value, '_staticEClass'):
            self.eobject_type = value.eClass
        else:
            self.native_type = value

    def __init__(self, *, name=None, native_type=None, type=None, **kwargs):

        super().__init__(**kwargs)

        if native_type is not None:
            self.native_type = native_type

        if type is not None:
            self.type = type


class TransfoParameter(Namedelement):

    direction = EAttribute(eType=DirectionKind, unique=True, derived=False, changeable=True)
    package = EReference(eType=EPackage)

    def __init__(self, *, direction=None, **kwargs):

        super().__init__(**kwargs)

        if direction is not None:
            self.direction = direction


class WhenFunction(PythonBody):

    body = EAttribute(eType=PythonAST, unique=True, derived=False, changeable=True)

    def __init__(self, *, body=None, **kwargs):

        super().__init__(**kwargs)

        if body is not None:
            self.body = body


class Main(Namedelement, PythonBody):

    body = EAttribute(eType=PythonAST, unique=True, derived=False, changeable=True)
    parameters = EReference(ordered=True, unique=True, containment=False, derived=False, upper=-1)
    transformation = EReference(ordered=True, unique=True, containment=False, derived=False)

    def __init__(self, *, parameters=None, body=None, transformation=None, **kwargs):

        super().__init__(**kwargs)

        if body is not None:
            self.body = body

        if parameters:
            self.parameters.extend(parameters)

        if transformation is not None:
            self.transformation = transformation


@abstract
class Rule(Namedelement, PythonBody):

    inputs = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)
    output = EReference(ordered=True, unique=True, containment=True, derived=False)
    transformation = EReference(ordered=True, unique=True, containment=False, derived=False)

    def __init__(self, *, inputs=None, output=None, transformation=None, **kwargs):

        super().__init__(**kwargs)

        if inputs:
            self.inputs.extend(inputs)

        if output is not None:
            self.output = output

        if transformation is not None:
            self.transformation = transformation


class Disjunct(Rule):

    mappings = EReference(ordered=True, unique=True, containment=False, derived=False, upper=-1)

    def __init__(self, *, mappings=None, **kwargs):

        super().__init__(**kwargs)

        if mappings:
            self.mappings.extend(mappings)


class Mapping(Rule):

    when = EReference(ordered=True, unique=True, containment=True, derived=False)

    def __init__(self, *, when=None, **kwargs):

        super().__init__(**kwargs)

        if when is not None:
            self.when = when
