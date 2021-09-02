
from .chainengine import getEClassifier, eClassifiers
from .chainengine import name, nsURI, nsPrefix, eClass
from .chainengine import Chain, Operation, Save, Transformation, M2M, M2T, SerializationFormat, Interactive, Load, IO, OperationExtension


from . import chainengine

__all__ = ['Chain', 'Operation', 'Save', 'Transformation', 'M2M', 'M2T',
           'SerializationFormat', 'Interactive', 'Load', 'IO', 'OperationExtension']

eSubpackages = []
eSuperPackage = None
chainengine.eSubpackages = eSubpackages
chainengine.eSuperPackage = eSuperPackage

Chain.operations.eType = Operation
Operation.chain.eType = Chain
Operation.chain.eOpposite = Chain.operations
Save.serializationformat.eType = SerializationFormat
SerializationFormat.saves.eType = Save
SerializationFormat.saves.eOpposite = Save.serializationformat

otherClassifiers = []

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
