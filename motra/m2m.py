import typing
import functools
import inspect
import pyecore.ecore as Ecore
from pyecore.resources import ResourceSet, URI, Resource
from pyecore.notification import EObserver
from . import trace


class ResultObserver(EObserver):
    def notifyChanged(self, notif):
        print(notif)


class EObjectProxy(object):
    def __init__(self, instance):
        object.__setattr__(self, 'wrapped', instance)
        object.__setattr__(self, 'wrapped_eClass', instance.eClass)

    def __getattribute__(self, name):
        wrapped = object.__getattribute__(self, 'wrapped')
        eClass = object.__getattribute__(self, 'wrapped_eClass')
        result = getattr(wrapped, name)
        # if eClass.findEStructuralFeature(name):
        #     print('access', name, ':', result, 'for', wrapped)
        return result

    def __eq__(self, other):
        return object.__getattribute__(self, 'wrapped').__eq__(other)

    def __hash__(self):
        return object.__getattribute__(self, 'wrapped').__hash__()

    def __setattr__(self, name, value):
        wrapped = object.__getattribute__(self, 'wrapped')
        if isinstance(value, EObjectProxy):
            value = object.__getattribute__(value, 'wrapped')
        return setattr(wrapped, name, value)

    def __str__(self):
        wrapped = object.__getattribute__(self, 'wrapped')
        return wrapped.__str__()


class Parameters(object):
    def __init__(self, transformation, parameter_names):
        self.transformation = transformation
        self.parameter_names = parameter_names

    def __getitem__(self, item):
        if type(item) is str:
            return getattr(self, item)
        return getattr(self, self.parameter_names[item])


class Transformation(object):
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.inputs_def = inputs
        self.outputs_def = outputs
        self.metamodels = set()
        self.registered_mappings = []
        self._main = None
        self._polymorphic_calls = {}

    @property
    def inouts(self):
        return [k for k in self.inputs_def if k in self.outputs_def]

    def main(self, fun):
        self._main = fun
        return fun

    def run(self, clean_mappings_cache=True, resource_set=None, **kwargs):
        sp = inspect.currentframe()
        context = TransformationExecution(self, resource_set)
        sp.f_globals["mycontext"] = context

        params = {}
        for in_model in self.inputs_def:
            try:
                rset = context.resource_set
                for mm in self.metamodels:
                    rset.metamodel_registry[mm.nsURI] = mm
                param = kwargs.pop(in_model)
                if isinstance(param, Ecore.EObject):
                    if param.eResource:
                        resource = param.eResource
                    else:
                        resource = rset.create_resource(URI(in_model))
                        resource.append(param)
                elif isinstance(param, Resource):
                    resource = param
                else:
                    resource = rset.get_resource(param)
                setattr(context.inputs, in_model, resource)
                params[in_model] = resource
                if in_model in self.inouts:
                    setattr(context.outputs, in_model, resource)
                    params[in_model] = resource
            except KeyError as e:
                raise type(e)(f'{e}:: {in_model} is a missing input model')
        for out_model in list(set(self.outputs_def) - set(self.inouts)):
            resource = rset.create_resource(URI(out_model))
            setattr(context.outputs, out_model, resource)
            params[out_model] = resource
        context.primary_output = context.outputs[0]
        params.update(kwargs)
        self._main(**params)
        if clean_mappings_cache:
            for mapping in self.registered_mappings:
                mapping.cache.cache_clear()
        return context

    def _remember_package(self, eclass):
        if eclass is None:
            return
        if isinstance(eclass, type):
            package = eclass.eClass.ePackage
        else:
            package = eclass.ePackage
        self.metamodels.add(package)

    def mapping(self, f=None, output_model=None, when=None):
        if not f:
            return functools.partial(self.mapping,
                                     output_model=output_model,
                                     when=when)
        result_var_name = 'result'
        self_var_name = 'self'
        f.self_eclass = typing.get_type_hints(f).get(self_var_name)
        if f.self_eclass is None:
            raise ValueError("Missing 'self' parameter for mapping: '{}'"
                             .format(f.__name__))

        existing_mappings = (x.__name__ for x in self.registered_mappings)
        if f.__name__ in existing_mappings:
            self._polymorphic_calls[(f.__name__, f.self_eclass)] = f

        self.registered_mappings.append(f)
        f.__mapping__ = True
        f.__transformation__ = self
        self._remember_package(f.self_eclass)
        f.result_eclass = typing.get_type_hints(f).get('return')
        self._remember_package(f.result_eclass)
        f.inout = f.result_eclass is None
        output_model_name = output_model or self.outputs_def[0]
        f.output_def = None if f.inout else output_model_name

        @functools.wraps(f)
        def inner(*args, **kwargs):
            try:
                func = self._polymorphic_calls[(f.__name__, type(args[0]))]
            except KeyError:
                for (fname, ftype), pfunc in self._polymorphic_calls.items():
                    if fname == f.__name__ and isinstance(args[0], ftype):
                        func = pfunc
                        break
                else:
                    func = f
            if func.inout:
                index = func.__code__.co_varnames.index(self_var_name)
                result = kwargs.get(self_var_name, args[index])
            elif func.result_eclass is Ecore.EClass:
                result = func.result_eclass('')
            else:
                result = func.result_eclass()
            inputs = [a for a in args if isinstance(a, Ecore.EObject)]
            # print('CREATE', result, 'FROM', inputs, 'BY', f.__name__)

            # Create object for the trace
            sp = inspect.currentframe()
            context = sp.f_globals["mycontext"]
            try:
                rule = context.trace[f.__name__]
            except Exception:
                rule = trace.Rule(name=f.__name__)
            context.trace.rules.append(rule)
            record = trace.Record()
            for element in args:
                if isinstance(element, Ecore.EObject):
                    record.inputs.append(trace.ObjectReference(old_value=element))
                else:
                    record.inputs.append(trace.Attribute(old_value=element))
            record.outputs.append(trace.ObjectReference(old_value=result))
            rule.records.append(record)

            # Inject new parameter
            g = func.__globals__
            marker = object()
            oldvalue = g.get(result_var_name, marker)
            g[result_var_name] = result
            # observer = ResultObserver(notifier=result)
            new_args = [EObjectProxy(obj)
                        if isinstance(obj, Ecore.EObject)
                        else obj
                        for obj in args]

            for key, value in kwargs.items():
                if isinstance(value, Ecore.EObject):
                    kwargs[key] = EObjectProxy(value)
            try:
                func(*new_args, **kwargs)
            finally:
                if oldvalue is marker:
                    del g[result_var_name]
                else:
                    g[result_var_name] = oldvalue
                # result.listeners.remove(observer)
                if func.output_def and \
                        result not in context.outputs[func.output_def].contents:
                    context.outputs[func.output_def].append(result)
            return result
        cached_fun = functools.lru_cache()(inner)
        f.cache = cached_fun
        if when:
            @functools.wraps(inner)
            def when_inner(*args, **kwargs):
                if when(*args, **kwargs):
                    return inner(*args, **kwargs)
            when_inner.cache = cached_fun
            return when_inner
        return cached_fun

    def disjunct(self, f=None, mappings=None):
        if not f:
            return functools.partial(self.disjunct, mappings=mappings)

        @functools.wraps(f)
        def inner(*args, **kwargs):
            for fun in mappings:
                result = fun(*args, **kwargs)
                if result is not None:
                    break
            f(*args, **kwargs)
            return result
        return inner


class TransformationExecution(object):
    def __init__(self, transfo, resource_set=None):
        self.trace = trace.TransformationTrace()
        self.inputs = Parameters(transfo, transfo.inputs_def)
        self.outputs = Parameters(transfo, transfo.outputs_def)
        self.transformation = transfo
        self.resource_set = resource_set if resource_set else ResourceSet()
