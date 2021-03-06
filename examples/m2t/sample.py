from motra import m2t
import pyecore.ecore as ecore


#
# A simple ecore to dot to see hierarchie (no other stuff)
#
ecore2dot = m2t.Transformation("ecore2dot")


@ecore2dot.main
def package2graph(self: ecore.EPackage):
    """
Generate dot file: "examples/outputs/${self.name}.dot"
<%motra:file path="examples/outputs/${self.name}.dot"> \\
Digraph metamodel_${self.name} {
    % for eclass in self.eClassifiers:
        ${eclass.name};
        % if isinstance(eclass, ecore.EClass):
            %for stype in eclass.eSuperTypes:
        ${eclass2node(eclass, stype)}
            %endfor
            %for ref in eclass.eReferences:
        ${ereference2link(ref)}
            %endfor
        % endif
    % endfor
}
</%motra:file>

Generate Makefile: "examples/outputs/Makefile"
<%motra:file path="examples/outputs/Makefile"> \\
all: ${self.name}.png

${self.name}.png: ${self.name}.dot
\tdot -Tpng -o $@ $<
</%motra:file>
"""


@ecore2dot.template
def eclass2node(self: ecore.EClass, stype: ecore.EClass):
    """${self.name} -> ${stype.name};"""


@ecore2dot.template
def ereference2link(self: ecore.EReference):
    """${self.eContainer().name} -> ${self.eType.name}"""

#
# A simple ecore 2 java-like language.
# This demonstrate the use of various tag to produce many files and file hierarchies
#
ecore2simplejava = m2t.Transformation("ecore2simplejava")

@ecore2simplejava.main
def eclass2class(self: ecore.EClass):
    """
<%motra:file path="examples/outputs/${self.ePackage.name}/${self.name}.java">
public class ${self.name.capitalize()} {
    % for feature in self.eStructuralFeatures:
    // ${override(feature)}
    ${feature2attribute(feature)}
    % endfor
}
</%motra:file>
"""

@ecore2simplejava.template(
    when=lambda self: self.many
)
def feature2attribute(self: ecore.EAttribute):
    """List<${self.eType.name}> ${self.name}; // many attribute"""


@ecore2simplejava.template
def feature2attribute(self: ecore.EAttribute):
    """${self.eType.name} ${self.name}; // single attribute"""


@ecore2simplejava.template(
    when=lambda self: self.many
)
def feature2attribute(self: ecore.EReference):
    """List<${self.eType.name}> ${self.name}; // many reference"""


@ecore2simplejava.template
def feature2attribute(self: ecore.EReference):
    """${self.eType.name} ${self.name}; // single reference"""


@ecore2simplejava.template
def override(self: ecore.EAttribute):
    """Attribut ${self.name}: ${self.eType.name} [${self.lowerBound}..${upper2symbol(self)}]"""


@ecore2simplejava.template
def override(self: ecore.EReference):
    """Reference ${self.name}: ${self.eType.name} [${self.lowerBound}..${upper2symbol(self)}]"""


@ecore2simplejava.helper
def upper2symbol(self: ecore.EStructuralFeature):
    return '*' if self.many else self.upperBound
