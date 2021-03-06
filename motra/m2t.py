import inspect
import functools
from io import StringIO
from pathlib import Path
import pyecore.ecore as Ecore
from pyecore.utils import DynamicEPackage
from pyecore.resources import ResourceSet, Resource, URI
from mako.template import Template
from mako.runtime import Context, Undefined


def in_file(path, append, body):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = 'w+' if append else 'w'
    with open(path, mode) as f:
        f.write(body)
    return ""


file_tag = """
<%namespace name="motra">
<%def name="file(path, append=True)"><%  body = capture(caller.body) %> ${in_file(path, append, body)}</%def>
</%namespace>
"""


class Transformation(object):
    def __init__(self, name):
        self.name = name
        self.mains = []
        self.file_tag = file_tag
        self.full_template = self.file_tag
        self.metamodels = set()
        self._polymorphic_calls = {}
        self.helpers = []

    def run(self, model, resource_set=None, **kwargs):
        if isinstance(model, Resource):
            model = model.contents[0]  # FIXME deal with mutliple root resources
        elif isinstance(model, (str, URI)):
            rset = resource_set if resource_set else ResourceSet()
            for metamodel in self.metamodels:
                rset.metamodel_registry[metamodel.nsURI] = metamodel
            resource = rset.get_resource(model)
            model = resource.contents[0]  # FIXME deal with mutliple root resources
        buf = StringIO()
        myprops = {'in_file': in_file}
        myprops.update(**kwargs)
        for f in self.helpers:
            myprops[f.__name__] = f
        for name, templates in self._polymorphic_calls.items():
            myprops[name] = templates[0]
        for metamodel in self.metamodels:
            myprops[metamodel.name] = DynamicEPackage(metamodel)

        ctx = Context(buf,**myprops)
        sp = inspect.currentframe()
        sp.f_globals["mycontext"] = ctx

        self.template = Template
        for element in (model, *model.eAllContents()):
            for (fun, pname, etype), template in self.mains:
                if isinstance(element, etype):
                    params = {pname: element}
                    template = Template(self.full_template)
                    template.get_def(fun.__name__).render_context(ctx, element)
        del sp.f_globals["mycontext"]
        return buf.getvalue()

    def _register_template(self, f):
        def_template = """
<%def name="{}({})">{}</%def>
""".format(f.__name__, (', '.join(x for x in inspect.signature(f).parameters)), f.__doc__)
        self.full_template += def_template

    def main(self, f):
        cached_fun = functools.lru_cache()(f)
        if not f.__doc__:
            return cached_fun
        parameter = next(iter(inspect.signature(f).parameters.values()))
        self.mains.append(((f, parameter.name, parameter.annotation), cached_fun))
        ec = parameter.annotation
        if hasattr(ec, '_staticEClass'):
            self.metamodels.add(parameter.annotation.eClass.ePackage)
        elif isinstance(ec, Ecore.EObject):
            self.metamodels.add(eclass.ePackage)
        self._register_template(f)
        return cached_fun

    def template(self, f=None, when=None):
        if not f:
            return functools.partial(self.template,
                                     when=when)
        f.when = when

        @functools.wraps(f)
        def inner(*args, **kwargs):
            try:
                var_name = f.__code__.co_varnames[0]
                index = f.__code__.co_varnames.index(var_name)
                self_parameter = args[index]
            except IndexError:
                self_parameter = kwargs[var_name]
            candidates = self._polymorphic_calls[f.__name__]
            for candidate in candidates:
                candidate = candidate.__wrapped__.__wrapped__
                parameter = next(iter(inspect.signature(candidate).parameters.values()))
                if isinstance(self_parameter, parameter.annotation):
                    # func = candidate
                    # break
                    if not candidate.when or candidate.when(*args, **kwargs):
                        func = candidate
                        break
            else:
                return Undefined
            # Create object for the context
            sp = inspect.currentframe()
            try:
                ctx = sp.f_globals["mycontext"]
            except KeyError:
                raise RuntimeError("Template cannot be executed outside of the "
                                   "the transformation.")
            old_io = ctx._buffer_stack[0]
            buf = StringIO()
            ctx._buffer_stack[0] = buf
            func.template.get_def(func.__name__).render_context(ctx, *args, **kwargs)
            ctx._buffer_stack[0] = old_io
            return buf.getvalue()
        cached_fun = functools.lru_cache()(inner)
        self._polymorphic_calls.setdefault(f.__name__,[]).append(cached_fun)
        if not f.__doc__:
            return cached_fun
        def_template = """<%def name="{}({})">{}</%def>""".format(f.__name__, (', '.join(x for x in inspect.signature(f).parameters)), f.__doc__)
        f.template = Template(def_template)
        parameter = next(iter(inspect.signature(f).parameters.values()))
        f.f_parameter = parameter
        self.metamodels.add(parameter.annotation.eClass.ePackage)
        return cached_fun

    def helper(self, f):
        self.helpers.append(f)
