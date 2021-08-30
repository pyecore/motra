__version__ = "0.1.1"


def objects(resource):
    for elt in resource.contents:
        yield elt
        yield from elt.eAllContents()


def objects_of_kind(resource, type):
    for elt in resource.contents:
        if isinstance(elt, type):
            yield elt
        for x in elt.eAllContents():
            if isinstance(x, type):
                yield x
