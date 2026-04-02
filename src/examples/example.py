# run `pip install mukip` at the terminal
import mukip

# Create an instance of MicrokineticModel with the path to the setup file
a = mukip.MicrokineticModel(r"1.NORR_Ni/NORR_Ni.mukip")

# Run the microkinetic simulation using the default map_sample method
a.run()

# Save the computed results to a .dat file for future use
# The saved data can be reloaded later using a.load_data() to skip re-running the simulation
a.save_data()

# Retrieve and print thermodynamic parameters at 800 K and 1.0 bar
# The arguments correspond to grid indices (25, 15) in the parameter space
print(a.get_grid_thermo(25, 15))

# Retrieve and print simulation results at 800 K and 1.0 bar
print(a.get_result(25, 15))

# Retrieve and print detailed variable information at 800 K and 1.0 bar
print(a.get_variables(25, 15))

# Write output results and generate plots as defined in the writer section of the setup file
# The output content and path are configured in the setup file's writer field
a.write(plot=True)