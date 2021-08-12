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
