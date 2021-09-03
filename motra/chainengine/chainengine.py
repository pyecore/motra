"""Definition of meta model 'chainengine'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *
import motra.chainengine.chainengine_mixins as _user_module


name = 'chainengine'
nsURI = 'http://chainengine/1.0'
nsPrefix = 'chainengine'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)


class Chain(_user_module.ChainMixin, EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    operations = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)

    def __init__(self, *, name=None, operations=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name

        if operations:
            self.operations.extend(operations)


@abstract
class Operation(_user_module.OperationMixin, EObject, metaclass=MetaEClass):

    chain = EReference(ordered=True, unique=True, containment=False, derived=False)

    def __init__(self, *, chain=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if chain is not None:
            self.chain = chain


class SerializationFormat(_user_module.SerializationFormatMixin, EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    saves = EReference(ordered=True, unique=True, containment=False, derived=False, upper=-1)

    def __init__(self, *, name=None, saves=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name

        if saves:
            self.saves.extend(saves)


@abstract
class Transformation(_user_module.TransformationMixin, Operation):

    implementation = EAttribute(eType=EJavaObject, unique=True, derived=False, changeable=True)

    def __init__(self, *, implementation=None, **kwargs):

        super().__init__(**kwargs)

        if implementation is not None:
            self.implementation = implementation


@abstract
class Interactive(_user_module.InteractiveMixin, Operation):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


@abstract
class IO(_user_module.IOMixin, Operation):

    path = EAttribute(eType=EString, unique=True, derived=False, changeable=True)

    def __init__(self, *, path=None, **kwargs):

        super().__init__(**kwargs)

        if path is not None:
            self.path = path


class OperationExtension(_user_module.OperationExtensionMixin, Operation):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Save(_user_module.SaveMixin, IO):

    serializationformat = EReference(ordered=True, unique=True, containment=False, derived=False)

    def __init__(self, *, serializationformat=None, **kwargs):

        super().__init__(**kwargs)

        if serializationformat is not None:
            self.serializationformat = serializationformat


class M2M(_user_module.M2MMixin, Transformation):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class M2T(_user_module.M2TMixin, Transformation):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Load(_user_module.LoadMixin, IO):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
