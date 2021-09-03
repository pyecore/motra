from pyecore.resources import ResourceSet, Resource
from pyecore.ecore import EObject
"""Mixins to be implemented by user."""


class ChainMixin:
    """User defined mixin class for Chain."""

    def __init__(self, *, name=None, operations=None, **kwargs):
        super().__init__()

    def run(self, input=None):
        parameter = input
        self.resource_set = ResourceSet()
        for operation in self.operations:
            parameter = operation.execute(operation.prepare_execution(parameter))
        del self.resource_set
        return parameter


class OperationMixin:
    """User defined mixin class for Operation."""

    def __init__(self, *, chain=None, **kwargs):
        super().__init__()

    def prepare_execution(self, param):
        if isinstance(param, Resource):
            return param
        rset = self.chain.resource_set
        if isinstance(param, str):
            resource = rset.get_resource(resource)
        if isinstance(param, EObject):
            if param.eResource:
                resource = param.eResource
            else:
                resource = rset.create_resource(f"tmp_{id(param)}")
                resource.append(param)
        return resource

    def execute(self, model=None):

        raise NotImplementedError('operation execute(...) not yet implemented')


class SerializationFormatMixin:
    """User defined mixin class for SerializationFormat."""

    def __init__(self, *, name=None, saves=None, **kwargs):
        super().__init__()


class TransformationMixin:
    """User defined mixin class for Transformation."""

    def __init__(self, *, implementation=None, **kwargs):
        super().__init__(**kwargs)


class InteractiveMixin:
    """User defined mixin class for Interactive."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class IOMixin:
    """User defined mixin class for IO."""

    def __init__(self, *, path=None, **kwargs):
        super().__init__(**kwargs)


class OperationExtensionMixin:
    """User defined mixin class for OperationExtension."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SaveMixin:
    """User defined mixin class for Save."""

    def __init__(self, *, serializationformat=None, **kwargs):
        super().__init__(**kwargs)

    def execute(self, resource):
        resource.save(self.path)
        return resource


class M2MMixin:
    """User defined mixin class for M2M."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, resource):
        inputdefs = self.implementation.inputs_def
        input_dict = {
            inputdefs[0]: resource
        }
        try:
            rset = self.chain.resource_set
            result = self.implementation.run(resource_set=rset, **input_dict)
            return result.outputs[0]
        except AttributeError as e:
            raise RuntimeError("The transformation has to be launched from a chain")


class M2TMixin:
    """User defined mixin class for M2T."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, resource):
        try:
            rset = self.chain.resource_set
            result = self.implementation.run(resource)
            result = result.rstrip()
            if result:
                print(result)
            return resource
        except AttributeError as e:
            raise RuntimeError("The transformation has to be launched from a chain")


class LoadMixin:
    """User defined mixin class for Load."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
