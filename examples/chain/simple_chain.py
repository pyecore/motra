from motra.chain import ChainEngine
from examples.m2m.inplace import changename, polymorphic
from examples.m2t.sample import ecore2simplejava, ecore2dot

ecore2javalike = (ChainEngine('ecore2javalike')
    .m2m(changename)
    .m2m(polymorphic)
    .save("examples/outputs/chpoly1.ecore")
    # .repl()
    .m2m(changename)
    # .repl()
    .save("examples/outputs/chpoly2.ecore")
    .m2t(ecore2simplejava)
    .m2t(ecore2dot)
)
