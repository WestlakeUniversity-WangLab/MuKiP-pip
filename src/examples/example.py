# run `pip install mukip == 0.5.0` at the terminal
import mukip

# Create an instance of MicrokineticModel with the path to the setup file
a = mukip.KineticModel(r"1.NORR_Ni/NORR_Ni.mukip")

# Show all details of the reaction model.
print("Global constants:")
for k, v in a.get_global_constants().items():
    print(f"{k} = {v}")

print("")
print("Point constants:")
for k, v in a.get_point_constant_expressions().items():
    print(f"{k} = {v}")

print("")
print("Expression dictionary:")
for k, v in a.get_expression_dictionary().items():
    print(f"{k} = {v}")

print("")
print("Variables:")
print(a.get_variable_list())

print("")
print("Datatypes:")
for t in a.get_data_types():
    print(t + ':' + str(a.get_data_items(t)))

input("Press Enter to continue...")
# Run the microkinetic simulation using the default map_sample method
a.run()

# Calculate degree of rate control.
# This line only works when Only when a SpeciesEnergyDRCModifier is set in the setup file!
a.run('map_drc')

# Save the computed results to a .dat file for future use
# The saved data can be reloaded later using a.load_data() to skip re-running the simulation
a.save_data()

# Retrieve and print thermodynamic parameters at 800 K and 1.0 bar
# The arguments correspond to grid indices (25, 15) in the parameter space
print(a.get_grid_parameters(25, 15))

# Retrieve and print simulation results at 800 K and 1.0 bar
print(a.get_result(25, 15))

# Retrieve and print detailed variable information at 800 K and 1.0 bar
print(a.get_variables(25, 15))

# Show DRC information
# This line only works when Only when a SpeciesEnergyDRCModifier is set in the setup file!
print(a.get_DRC_info_at(10, 10))

# Write output results and generate plots as defined in the writer section of the setup file
# The output content and path are configured in the setup file's writer field
a.write(plot=True)