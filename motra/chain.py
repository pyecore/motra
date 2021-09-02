from .chainengine import M2M, M2T, Chain, Save


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
