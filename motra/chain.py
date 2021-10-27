import cmd
import pyecore
from pyecore.resources import ResourceSet, Resource
from .chainengine import M2M, M2T, Chain, Save, Interactive, Transformation
# from . import m2t


class ChainEngine(object):
    def __init__(self, name):
        self.chain = Chain(name=name)

    def m2m(self, transfo):
        self.chain.operations.append(M2M(implementation=transfo))
        return self

    def m2t(self, transfo):
        self.chain.operations.append(M2T(implementation=transfo))
        return self

    def save(self, path):
        self.chain.operations.append(Save(path=path))
        return self

    def interaction(self, interactive):
        self.chain.operations.append(interactive)
        return self

    def repl(self):
        self.chain.operations.append(modelrepl)
        return self

    def run(self, model):
        return self.chain.run(model)


class ModelShell(cmd.Cmd):
    intro = 'Python model shell, modify your model'
    prompt = '(shell) '

    def __init__(self, resource_set=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rset = resource_set if resource_set else ResourceSet()
        self.vars = {
            'rset': self.rset,
        }
        self.gvars = {
            'ecore': pyecore.ecore
        }
        self.vars['metavars'] = self.vars

    def do_load(self, arg):
        try:
            print(f'!! Loading {arg}')
            res = self.rset.get_resource(arg)
            self.vars['self'] = res.contents[0]
        except Exception as e:
            print(e)

    def do_register(self, arg):
        try:
            print(f'!! Registering {arg}')
            res = self.rset.get_resource(arg)
            root = res.contents[0]
            self.rset.metamodel_registry[root.nsURI] = root
        except Exception as e:
            print(e)

    def default(self, line):
        try:
            self.compile_execute(line)
        except Exception as e:
            print(e)

    def compile_execute(self, line):
        code = compile(line, '<expr>', 'single')
        return eval(code, self.gvars, self.vars)

    def do_quit(self, arg):
        print("\n!! Exiting")
        return True

    do_q = do_quit
    do_EOF = do_quit



class ModelREPL(Interactive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, resource):
        rset = self.chain.resource_set
        shell = ModelShell(rset)
        shell.vars['self'] = resource.contents[0]
        shell.cmdloop()
        return resource


modelrepl = ModelREPL()


# chain_printer = m2t.Transformation('chain_printer')
#
#
# @chain_printer.main
# def main(self: Chain):
#     """
# Generate dot file: "${output_path}/${self.name}.dot"
# <%motra:file path="${output_path}/${self.name}.dot"> \\
# Digraph ${self.name} {
#     rankdir=LR
#     % for operation in self.operations:
#     ${shape_config(operation)}
#     % endfor
#     % for operation in self.operations:
#     ${gen_name(operation)} \\
#     % if loop.index != len(self.operations) - 1:
#  -> \\
#     % endif
#     % endfor
#
# }
# </%motra:file>
#     """
#
# @chain_printer.template
# def shape_config(self: Transformation):
#     """${self.implementation.name} [shape=circle]"""
#
#
# @chain_printer.template
# def shape_config(self: Save):
#     """ "${self.path}" [shape=note]"""
#
#
# @chain_printer.template
# def shape_config(self: Interactive):
#     """${self.__class__.__name__} [shape=tab]"""
#
#
# @chain_printer.template
# def gen_name(self: Transformation):
#     """${self.implementation.name}"""
#
#
# @chain_printer.template
# def gen_name(self: Save):
#     """ "${self.path}" """
#
#
# @chain_printer.template
# def gen_name(self: Interactive):
#     """${self.__class__.__name__}"""
# # digraph G {
# #     rankdir=LR
# #     node [margin=0 fontcolor=blue fontsize=32 width=0.5 shape=note style=filled]
# #     inter [shape=rect width=0.1 label="" color=black]
# #
# #   a -> b
# #   b -> c
# #   b -> d
# # }
