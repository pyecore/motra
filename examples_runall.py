from examples.m2m.inplace import changename, variable_changename, duplicate

print("* Runs in-place transformations", end="")
result_context = changename.run(ecore_model="examples/inputs/input.ecore")
result_context.outputs.ecore_model.save(output="examples/outputs/changename_output.ecore")

result_context = variable_changename.run(ecore_model="examples/inputs/input.ecore",
                                         name="MyRoot", to="NewRoot")
result_context.outputs.ecore_model.save(output="examples/outputs/variablechangename_output.ecore")


result_context = duplicate.run(ecore_model="examples/inputs/input.ecore")
result_context.outputs.ecore_model.save(output="examples/outputs/duplicate_output.ecore")
print("     [DONE]")
