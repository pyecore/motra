.. _quickstart:

Quick Start
===========

Quick Overview
--------------

Motra is a library that brings model to model (M2M) and model to text (M2T) transformation for Python based on PyEcore.
It tries to mimic the semantic (until a certain level) of QVTo for M2M transformations and of Acceleo for M2T transformations, but in pure Python.
Motra also introduces a transformation chain engine that let you describe a complex sequence of transformations, reducing the pain of doing it manually.


M2M Quick start
---------------

To see how the M2M part works, lets introduce a very simple M2M refactoring transformation that just take a model instance of Ecore, and update the name of each ``EClass``.

.. code-block:: python

    # We consider here that the transformation is defined in a module "mytransfo.py"
    import pyecore.ecore as ecore  # we import the input/output metamodel
    import motra.m2m as m2m  # we import the m2m transformation possible
    import motra  # we import directly motra to have some utils functions

    prefixM2M = m2m.Transformation("prefixM2M", inputs=['mymodel'], outputs=['mymodel'])

    @prefixM2M.main
    def main(mymodel):
      for eclass in motra.objects_of_kind(mymodel, ecore.EClass):
        update_name(eclass)


    # This rule only update the name of the input object with a dumb prefix
    @prefixM2M.mapping
    def update_name(self: ecore.EClass):
      result.name := 'MyPrefix' + self.name
      # or:
      # self.name := 'MyPrefix' + self.name


This simple transformation gives some piece of information about what are the specificities of a Motra M2M.
First, it's important to import the metamodel you are working on, here it's the ``ecore`` metamodel.
Then, the transformation "signature" is defined using the ``m2m.Transformation`` class.
In the constructor of this object, the first parameter is the name, and the others are defining the name of the inputs and outputs parameters.
As we are on a transformation that modify the input model, then the same name is found in the inputs and in the outputs.
Each transformation need an entry point, defined using the ``main`` decorator.
The function decorated by ``main`` has to take as parameter the same names defined in the transformation, here ``mymodel``.
The objects passed to the ``main`` function are always the PyEcore resources containing the model.
Here, the main function simply filters all ``EClass`` instances from the resource and iterates on them, calling the ``update_name`` mapping rule.
The ``update_name`` function is here defined as a special mapping taking only ``ecore.EClass`` as inputs.
Mappings have some constraints:

* they have to use the annotations on each parameters of the mapping,
* if they produce a new object, it has to be the return type of the mapping (given through an annotation),
* the first parameter of the mapping have to be named ``self``,
* the ``result`` variable is automatically instanciated (when necessary) and injected by Motra.

This transformation can be defined at any level, but it's recommended to place it in a dedicated module.
Many transformations can be defined for a module, but unless they are small, it sounds like a good practice to put them in a dedicated module.
Once the transformation is defined, it can be directly run from another Python module/main, whatever:

.. code-block:: python

    from mytransfo import prefixM2M

    # as input, the "run" method accepts:
    # * PyEcore Resources,
    # * string path towards models,
    # * directly an EObject that is the unique root of your model
    result = prefixM2M.run(mymodel="examples/inputs/input.ecore")

    # The result object is an object giving many ways of accessing the input/output resources.
    # Each output/input accessed via the result of a transformation is always a PyEcore Resource.
    result.outputs.mymodel  # Access the result of the transformation by name
    result.inputs.mymodel   # Access the input of the transformation by name
    result.outputs[0]   # Access the first output model produced by the transformation
    result.inputs[0]    # Access the first input model produced by the transformation

    # By default, the output of a transformation is not serialized. It has to be done explicitally:
    result.outputs[0].save(output='myoutputfile.xmi')

    # From the result of a transformation, you can also access some other informations
    result.transformation  # Access the transformation that produced this result
    result.trace  # Access the execution trace of the transformation (WIP)


*Note:* after you defined a transformation and you decide to run it, there is no need to explicitally register a metamodel.
The simple fact of using it in the transformation is enough for Motra to detect it and auto-register it, meaning that you can directly pass to the runner a path toward a model instance of your metamodel without having to register the metamodel first in a dedicated ``ResourceSet``.


M2T Quick start
---------------

To see how the M2T part works, lets introduce a very simple M2T code generator that takes an ``ecore`` metamodel and simply generates two different outputs:

* a list of each ``EClass`` name **in a file** named after the name of the ``EPackage`` that contains them,
* a list of each ``EPackage`` name manipulated during the transformation **on stdout**.


.. code-block:: python

    import motra.m2t as m2t

    mygen = m2t.Transformation('mygen', inputs=['myecore'])


    @mygen.main
    def generate_epackage(self: ecore.EPackage):
        """
    * Generating names for EPackage "${self.name}"
    <%motra:file path="/tmp/${self.name}.md">
    = ${self.name.capitalize()}

    % for eclass in self.eClassifiers:
    * ${generate_eclass(eclass)}
    % endfor
    </%motra:file>
    """

  @mygen.template
  def generate_eclass(self: ecore.EClass):
    """
    ${self.name}
    """

From this transformation definition, here is what we can observe:

* the definition of the transformation is more or less equivalent to the M2M ones,
* templates are defined each ``@xxx.template`` docstrings,
* the template syntax is `Mako syntax <https://docs.makotemplates.org/>`_,
* unlike M2M Motra transformation, the main is directly expressed over a type (here ``EPackage``),
* there is a special balise ``<%motra:file></%motra:file>`` that defines in which file the code fragment must be generated.
