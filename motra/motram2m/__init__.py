
from .motram2m import getEClassifier, eClassifiers
from .motram2m import name, nsURI, nsPrefix, eClass
from .motram2m import Transformation, Disjunct, Mapping, PythonAST, Main, Namedelement, Rule, RuleParameter, TransfoParameter, WhenFunction, DirectionKind, PythonBody


from . import motram2m

__all__ = ['Transformation', 'Disjunct', 'Mapping', 'PythonAST', 'Main', 'Namedelement',
           'Rule', 'RuleParameter', 'TransfoParameter', 'WhenFunction', 'DirectionKind', 'PythonBody']

eSubpackages = []
eSuperPackage = None
motram2m.eSubpackages = eSubpackages
motram2m.eSuperPackage = eSuperPackage

Transformation.inputs.eType = TransfoParameter
Transformation.outputs.eType = TransfoParameter
Transformation.parameters.eType = TransfoParameter
Disjunct.mappings.eType = Mapping
Mapping.when.eType = WhenFunction
Main.parameters.eType = TransfoParameter
Rule.inputs.eType = RuleParameter
Rule.output.eType = RuleParameter
Transformation.rules.eType = Rule
Transformation.main.eType = Main
Main.transformation.eType = Transformation
Main.transformation.eOpposite = Transformation.main
Rule.transformation.eType = Transformation
Rule.transformation.eOpposite = Transformation.rules

otherClassifiers = [PythonAST, DirectionKind]

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
