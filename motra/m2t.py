import inspect
import functools
from io import StringIO
from pathlib import Path
from pyecore.utils import DynamicEPackage
from pyecore.resources import ResourceSet, Resource, URI
from mako.template import Template
from mako.runtime import Context


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

    def run(self, model, resource_set=None):
        if isinstance(model, Resource):
            model = resource.contents[0]  # FIXME deal with mutliple root resources
        elif isinstance(model, (str, URI)):
            rset = resource_set if resource_set else ResourceSet()
            for metamodel in self.metamodels:
                rset.metamodel_registry[metamodel.nsURI] = metamodel
            resource = rset.get_resource(model)
            model = resource.contents[0]  # FIXME deal with mutliple root resources
        buf = StringIO()
        myprops = {}
        myprops['in_file'] = in_file
        for metamodel in self.metamodels:
            myprops[metamodel.name] = DynamicEPackage(metamodel)
        self.template = Template
        result = ""
        for element in (model, *model.eAllContents()):
            for (fun, pname, etype), template in self.mains:
                if isinstance(element, etype):
                    params = {pname: element}
                    template = Template(self.full_template)
                    myprops['in_file'] = in_file
                    ctx = Context(buf,**myprops)
                    template.get_def(fun.__name__).render_context(ctx, element)
                    result += buf.getvalue()
        return result


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
        self.metamodels.add(parameter.annotation.eClass.ePackage)
        self._register_template(f)
        return cached_fun

    def template(self, f):
        cached_fun = functools.lru_cache()(f)
        if not f.__doc__:
            return cached_fun
        parameter = next(iter(inspect.signature(f).parameters.values()))
        self.metamodels.add(parameter.annotation.eClass.ePackage)
        self._register_template(f)
        return cached_fun
