from .m2m import Transformation
import motra.motram2m as mm2m
import pyecore.ecore as Ecore
from types import FunctionType
import inspect
import ast

# def mapping2model(m):
#     src = mm2m.PythonAST.from_string(inspect.getsource(m))
#
#     mapping = mm2m.Mapping(body=src, name=m.__name__)
#     if m.when:
#         for node in ast.walk(src):
#             decorator = [x for x in node.decorator_list if x.func.attr == 'mapping'][0]
#             lambda_fun_ast = [k for k in decorator.keywords if k.arg == 'when'][0].value
#             mapping.when = mm2m.WhenFunction(body=lambda_fun_ast)
#             mapping.body.decorator_list.remove(decorator)
#             break
#     else:
#         for node in ast.walk(src):
#             decorator = [x for x in node.decorator_list if x.attr == 'mapping'][0]
#             mapping.body.decorator_list.remove(decorator)
#             break
#     return mapping
#
#
# def main2model(m):
#     src = mm2m.PythonAST.from_string(inspect.getsource(m))
#     for node in ast.walk(src):
#         decorator = [x for x in node.decorator_list if x.attr == 'main'][0]
#         src.decorator_list.remove(decorator)
#         break
#     return mm2m.Main(body=src, name=m.__name__)
#
#
# def transfo2model(t):
#     transfo = mm2m.Transformation(name=t.name)
#     transfo.main = main2model(t._main)
#     for rule in t.registered_mappings:
#         transfo.rules.append(mapping2model(rule))
#     for input_ in t.inputs_def:
#         print(input_)
#     for output in t.outputs_def:
#         print(output)
#     return transfo

t2model = Transformation('t2model', inputs=['transfo'], outputs=['transfo_model'])


@t2model.main
def main(transfo, transfo_model):
    t2t(transfo.contents[0]._wrapped)


@t2model.mapping
def t2t(self: Transformation) -> mm2m.Transformation:
    result.name = self.name
    result.parameters.extend(str2input(x, self) for x in self.inputs_def)
    result.parameters.extend(str2output(x, self) for x in self.outputs_def if x not in self.inouts)
    result.main = main2main(self._main)
    result.rules.extend(x for rule in self.registered_mappings if (x := rule2rule(rule)) is not None)


@t2model.mapping
def str2input(self: str, t: Transformation) -> mm2m.TransfoParameter:
    result.name = self
    result.direction = mm2m.DirectionKind.INOUT if self in t.inouts else mm2m.DirectionKind.IN


@t2model.mapping
def str2output(self: str, t: Transformation) -> mm2m.TransfoParameter:
    result.name = self
    result.direction = mm2m.DirectionKind.INOUT if self in t.inouts else mm2m.DirectionKind.OUT


@t2model.mapping
def main2main(self: FunctionType) -> mm2m.Main:
    result.name = self.__name__
    src = mm2m.PythonAST.from_string(inspect.getsource(self))
    for node in ast.walk(src):
        decorator = [x for x in node.decorator_list if x.attr == 'main'][0]
        src.decorator_list.remove(decorator)
        break
    result.body = src
    t = self.__transformation__
    for key in inspect.signature(self).parameters.keys():
        if key in t.inputs_def:
            result.parameters.append(str2input(key, t))
        elif key in t.outputs_def and key not in t.inouts:
            result.parameters.append(str2output(key, t))


@t2model.mapping(when=lambda self: self.__mapping__)
def rule2rule(self: FunctionType) -> mm2m.Mapping:
    result.name = self.__name__
    src = mm2m.PythonAST.from_string(inspect.getsource(self))
    if self.when:
        for node in ast.walk(src):
            decorator = [x for x in node.decorator_list if x.func.attr == 'mapping'][0]
            lambda_fun_ast = [k for k in decorator.keywords if k.arg == 'when'][0].value
            result.when = mm2m.WhenFunction(body=lambda_fun_ast)
            src.decorator_list.remove(decorator)
            break
    else:
        for node in ast.walk(src):
            decorator = [x for x in node.decorator_list if x.attr == 'mapping'][0]
            src.decorator_list.remove(decorator)
            break
    result.body = src
    signature = inspect.signature(self)
    for p in signature.parameters.values():
        result.inputs.append(parameter2parameter(p))
    if signature.return_annotation is not inspect.Signature.empty:
        result.output = result2result(self)


@t2model.mapping
def rule2rule(self: FunctionType) -> mm2m.Disjunct:
    result.name = self.__name__
    result.mappings.extend(rule2rule(rule.__wrapped__.__wrapped__) for rule in self.mappings)
    src = mm2m.PythonAST.from_string(inspect.getsource(self))
    for node in ast.walk(src):
        decorator = [x for x in node.decorator_list if x.func.attr == 'disjunct'][0]
        src.decorator_list.remove(decorator)
        break
    result.body = src


# @t2model.disjunct(
#     mappings=[mapping2mapping, disjunct2disjunct]
# )
# def rule2rules(self: FunctionType) -> mm2m.Disjunct:
#     ...


@t2model.mapping
def parameter2parameter(self: inspect.Parameter) -> mm2m.RuleParameter:
    result.name = self.name
    type_annotation = self.annotation
    result.type = type_annotation


@t2model.mapping
def result2result(self: FunctionType) -> mm2m.RuleParameter:
    result.name = 'result'
    type_annotation = inspect.signature(self).return_annotation
    result.type = type_annotation
