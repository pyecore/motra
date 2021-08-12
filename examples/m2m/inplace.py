import pyecore.ecore as ecore

import motra
from motra import m2m


##
# First simple in-place transformation
##
# "changename" is an in-place transformation
# inputs and outputs are the same
changename = m2m.Transformation('changename',
                                inputs=['ecore_model'],
                                outputs=['ecore_model'])


# parameter names must be the same as the one declared in the signature above
@changename.main
def main(ecore_model):
    for element in motra.objects_of_kind(ecore_model, ecore.ENamedElement):
        update_name(element)


# First parameter of any mapping *must* be named "self"
# typing is mandatory
@changename.mapping
def update_name(self: ecore.ENamedElement):
    self.name = f"{self.name}_newname"


##
# Seocnd simple in-place parametrable transformation
##
variable_changename = m2m.Transformation('variable_changename',
                                         inputs=['ecore_model'],
                                         outputs=['ecore_model'])


@variable_changename.main
def main(ecore_model, name=None, to=None):
    for element in motra.objects_of_kind(ecore_model, ecore.ENamedElement):
        update_name_var(element, name, to)


@variable_changename.mapping(
    when=lambda self, name, to:
            self.name == name
)
def update_name_var(self: ecore.ENamedElement, name=None, to=None):
    self.name = to


##
# Third simple in-place parametrable transformation
##
duplicate = m2m.Transformation('duplicate',
                               inputs=['ecore_model'],
                               outputs=['ecore_model'])


@duplicate.main
def main(ecore_model):
    dup(ecore_model.contents[0])


@duplicate.mapping(when=lambda self: isinstance(self, ecore.EClass))
def dupclass(self: ecore.EClass) -> ecore.EClass:
    result.name = f"{self.name}_duplicate"


@duplicate.mapping(when=lambda self: isinstance(self, ecore.EPackage))
def duppackage(self: ecore.EPackage) -> ecore.EPackage:
    result.name = f"{self.name}_duplicate"
    for classifier in list(self.eClassifiers):
        result.eClassifiers.append(dup(classifier))
        # or: result.eClassifiers += dup(classifier)


@duplicate.disjunct(mappings=[dupclass, duppackage])
def dup(self: ecore.EModelElement) -> ecore.EModelElement:
    ...


##
# Fourth simple in-place parametrable transformation, for cache feature
##
cache = m2m.Transformation('cache',
                           inputs=['ecore_model'],
                           outputs=['ecore_model'])


@cache.main
def main(ecore_model):
    change_name_package(ecore_model.contents[0])
    change_name_package(ecore_model.contents[0])


@cache.mapping
def change_name_package(self: ecore.EPackage):
    self.name = self.name + '_change'


##
# Fifth simple in-place parametrable transformation, demonstrating polymorphism
##
polymorphic = m2m.Transformation('polymorphic',
                                 inputs=['ecore_model'],
                                 outputs=['ecore_model'])


@polymorphic.main
def main(ecore_model):
    for element in ecore_model.contents[0].eAllContents():
        poly_name(element)


@polymorphic.mapping
def poly_name(self: ecore.EClass):
    self.name = self.name + '_ECLASS'

@polymorphic.mapping
def poly_name(self: ecore.EReference):
    self.name = self.name + '_EREFERENCE'
