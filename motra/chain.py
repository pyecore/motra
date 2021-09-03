import cmd
import pyecore
from pyecore.resources import ResourceSet, Resource
from .chainengine import M2M, M2T, Chain, Save, Interactive


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
