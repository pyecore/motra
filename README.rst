=========================================
Motra: Models Transformations for PyEcore
=========================================

Motra is a librairie providing model transformations facilities to PyEcore.
The goal of the librairie is to propose a set of embedded DSLs in Python for models to models transformations (M2M) and model to text transformations (M2T) with advanced traceability mechanism.
Here are some characteristics about Motra M2M:

* it proposes a semantic close to QVTo, imperative, based on ``mappings`` where the execution order is defined by the developer in each mapping,
* it supports multiple input and multiple outputs,
* each ``mapping`` result is cached and when a mapping is called twice with a same set of parameters, the exact same created object is returned,
* by default, any object created in a ``mapping`` that is not explicitaly placed in a container is automatically added as model root,
* used metamodels are automatically registered for smooth load/save of any models.
* it supports ``mapping`` polymorphism without having to rely on manual coding a dispatch with a ``disjunct`` (if the mappings own the same name)


Documentation
=============

WIP, at the moment, please refer to transformations examples in ``examples``.
To avoid the need to load/install special metamodels, all the transformations examples are given directly over Ecore.
The transformations are gathered in simple modules depending to their characteristics: in-place, in-out, endogenous or exogenous.


M2M Quick start
===============

Each transformation must be defined in it's own Python module (even if multiple transformations can be defined in one module).

.. code-block:: python

    # import the input and output metamodels
    import ghmde  # based on https://github.com/kolovos/datasets/blob/master/github-mde/ghmde.ecore
    import graph  # based on a simple graph metamodel

    # import motra for utils and for M2M transformation definition
    import motra
    from motra import m2m

    # M2M transformation "signature" definition
    ghmde2graph = m2m.Transformation('ghmde2graph',
                                     inputs=['ghmde_model'],
                                     outputs=['graph_model'])


    # defines the entry point of the transformation
    @ghmde2graph.main
    def main(ghmde_model, graph_model):
        print('Transforming repository to graph', graph_model)
        for f in motra.objects_of_kind(ghmde_model, ghmde.File):
            file2node(f)
        for repository in motra.objects_of_kind(ghmde_model, ghmde.Repository):
            repository2graph(repository, postfix='_graph')
        # m2m.objects_of_kind

    # defines a first mapping transforming Files in Node
    @ghmde2graph.mapping
    def file2node(self: ghmde.File) -> Node:
        result.name = self.path   # The "result" variable is automatically created and injected in the current context


    # defines a conditional mapping from Repository to Graph
    def does_not_starts_with(self, postfix):
        return not self.name.startswith(postfix)

    @ghmde2graph.mapping(when=does_not_starts_with)
    def repository2graph(self: ghmde.Repository, postfix: str) -> Graph:
        result.name = self.name + postfix
        for repo_file in self.files:
            result.nodes.append(file2node(repo_file))


Then, it can be imported and directly used from another module.
Currently, there is no default runner, but there will be in the future, a way of defining models transformations chains.

.. code-block:: python

    # Import the transformation
    from transfo_example import ghmde2graph

    # Just run it. Input can be a "Resource" or directly a file
    result_context = ghmde2graph.run(ghmde_model="input_model.xmi")*

    # A result context gives access to:
    # * the inputs
    # * the outputs
    # * the execution trace (still WIP)
    # * the transformation definition
    # * the used resource set for this transformation
    result_context.inputs.ghmde_model.save(output="input_copy.xmi")
    result_context.outputs.graph_model.save(output="test.xmi")



M2T Quick start
===============

As for M2M, a M2T transformation must be defined in it's own Python module (even if multiple transformations can be defined in one module as defined in the module ``examples/m2t/sample.py``).
Each template code is written as ``__doc__`` of template functions.

.. code-block:: python

    from motra import m2t
    import pyecore.ecore as ecore

    # M2T transformation "signature" definition
    ecore2simplejava = m2t.Transformation("ecore2simplejava")

    # Definition of the main entry point.
    # At the moment, entry-point cannot have "when=" parameter
    # The special <%motra:file ><%/motra:file> is used to specify blocs
    # where the code must be written. Multiple "file" tags can be introduced by template.
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
        """List<${self.eType.name}> ${self.name}; // single reference"""


    @ecore2simplejava.template
    def override(self: ecore.EAttribute):
        """Attribut ${self.name}: ${self.eType.name} [${self.lowerBound}..${upper2symbol(self)}]"""


    @ecore2simplejava.template
    def override(self: ecore.EReference):
        """Reference ${self.name}: ${self.eType.name} [${self.lowerBound}..${upper2symbol(self)}]"""


    @ecore2simplejava.helper
    def upper2symbol(self: ecore.EStructuralFeature):
        return '*' if self.many else self.upperBound


Then, it can be imported and directly used from another module.
Currently, there is no default runner, but there will be in the future, a way of defining models transformations chains.

.. code-block:: python

    # Import the transformation
    from examples.m2t.sample import ecore2simplejava

    # Just run it. Input can be a "Resource", a model or directly a file
    ecore2simplejava.run('examples/inputs/input.ecore')
