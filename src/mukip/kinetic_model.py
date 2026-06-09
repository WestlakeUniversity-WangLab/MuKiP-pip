import multiprocessing
from typing import Literal
import jpype

from .plot_1d import plot_1d
from .plot_2d import plot_2d
from .jvm_manager import get_class


def _wrap_parameter(pars):
    return {str(k): float(v) for k, v in pars.getValues().items()}

def _wrap_vector(vector):
    return [float(b.doubleValue()) for b in vector]

def _wrap_double_array(array):
    return [float(d) for d in array]

class KineticModel:
    """
    A wrapped class for microkinetic modeling.
    """
    KM = get_class("com.wang_lab.mukip.components.model.KineticModel").class_.getField("Companion").get(None)
    ArrayList = get_class('java.util.ArrayList')
    LinkedHashMap = get_class("java.util.LinkedHashMap")
    GridPoint = get_class("com.wang_lab.mukip.point.GridPoint")
    MapPoint = get_class("com.wang_lab.mukip.point.MapPoint")
    JUtils = get_class("com.wang_lab.mukip.MuKiPUtils")
    Adsorbate = get_class("com.wang_lab.mukip.species.Adsorbate")
    Gas = get_class("com.wang_lab.mukip.species.Gas")
    Fluid = get_class("com.wang_lab.mukip.species.Fluid")
    Aqua = get_class("com.wang_lab.mukip.species.Aqua")
    n_cpu = multiprocessing.cpu_count()

    def _to_float(self, num):
        return float(self.JUtils.toDouble(num))

    def __init__(self, setup_file: str):
        """
        Create a new MicrokineticModel object.

        :param setup_file: The path of the setup file for microkinetic model
        """
        self.setup_file = setup_file
        self.model = self.KM.reactionModel(jpype.JString(self.setup_file))

    def load_data(self):
        """
        Load solutions for each point from the data file.
        """
        self.model.loadData()

    def save_data(self):
        """
        Save solutions on each point to the data file.
        """
        self.model.saveData()

    def _get_grid_point(self, *index: int):
        return self.model.getPoint(self.GridPoint(*index))

    def get_global_parameters(self):
        """
        Get global parameters.
        :return: A dictionary of all global parameters.
        """
        return _wrap_parameter(self.model.getFixedPars())

    def get_grid_parameters(self, *index: int):
        """
        Get the parameters of a grid point.
        :param index: The index of the grid point.
        :return: A dictionary of all parameters on this point.
        """
        return _wrap_parameter(self._get_grid_point(*index).getParameter())

    def run(self, method: Literal['map_sample', 'map_in_turn', 'map_expand', 'map_check', 'map_drc']='map_sample', n_thread: int = n_cpu):
        """
        Run the kinetic model with given method.
        Methods:
            - 'map_sample': Use sampling-expansion method (SEM), which boasts high solving efficiency and stability
            , and is highly recommended.

            - 'map_in_turn': Solve all points in turn.

            - 'map_expand': Solve all unsolved points from points with solution. It should be used when a partial set
            of points are successfully solved.

            - 'map_check': Check existing solutions on all points in turn. If the solution on a point is incorrect,
            it will attempt to solve it. If the solution fails, the data will be deleted to ensure that
            all solutions are correct after the method is completed.

            - 'map_drc': Calculate degree od rate control. Only available when a SpeciesEnergyDRCModifier is set in
            the setup file.
        :param method: The method to use to run the kinetic model.
        :param n_thread: Number of threads to use.
        """
        self.model.getMapper().map(method, n_thread, self.ArrayList(), None)

    def get_variable_list(self):
        """
        Get the variables of the reaction model.
        :return: variables as a list.
        """
        return [str(it) for it in self.model.getSolver().getVarList()]

    def get_equations(self):
        """
        Get the equations of the reaction model.
        :return: equations as a list.
        """
        return [str(it) for it in self.model.getSolver().getResidues()]

    def get_global_constants(self):
        """
        Get the global constants that do not vary with descriptors.
        :return: constant names and values as a dictionary.
        """
        return {str(k): self._to_float(v) for k, v in self.model.getSolver().getGlobalConstant().items()}

    def get_point_constant_expressions(self):
        """
        Get the point constant expressions that varies with descriptors but does not vary with independent variables.
        :return: constant names and their expressions.
        """
        return {str(k): str(v) for k, v in self.model.getSolver().getConstantExpressionDictionary().items()}

    def get_expression_dictionary(self):
        """
        Get the variables that vary with the independent variables along with their expressions.
        :return: variable names and their expressions.
        """
        return {str(k): str(v) for k, v in self.model.getSolver().getExpressionDictionary().items()}

    def get_data_types(self):
        """
        Get the data types of the reaction model.
        :return: data types as a list.
        """
        return [str(it) for it in self.model.getSolver().plotTypes()]

    def get_data_items(self, type_name: str):
        """
        Get the data items of the selected type of the reaction model.
        :param type_name:
        :return: data items as a list.
        """
        items = self.model.getItem(type_name)
        if items:
            return [str(it) for it in items]
        else:
            raise Exception(f"Data type {type_name} not found.")

    def get_result(self, *index: int):
        """
        Get results on a point.
        :param index: The index of the grid point.
        :return: Results as a dictionary.
        """
        type_names = self.get_data_types()
        pt = self._get_grid_point(*index)
        results = {}

        for type_name in type_names:
            items = self.get_data_items(type_name)
            data = self.model.getPointData(pt, type_name)
            results[type_name] = {it: v for it, v in zip(items, data)}
        return results

    def get_variables(self, *index: int):
        """
        Get constants and results on a point.
        :param index: The index of the grid point.
        :return: Fined variables as a dictionary.
        """
        pt = self._get_grid_point(*index)
        variables = self.model.getSolver().getFinePointValues(pt)
        results = {str(k): float(v.doubleValue()) for k, v in variables.items()}
        return results

    def get_full_variables(self, *index: int):
        """
        Get all variables on a point, including all intermediate variables.
        :param index: The index of the grid point.
        :return: Fined variables as a dictionary.
        """
        pt = self._get_grid_point(*index)
        variables = self.model.getSolver().getFinePointValues(pt)
        results = {str(k): float(v.doubleValue()) for k, v in variables.items()}
        expressions = self.model.getSolver().getExpressionDictionary()
        buffer = self.LinkedHashMap()
        for k, v in expressions.items():
            results[k] = self._to_float(v.arithmetic(variables, expressions, buffer))
        return results

    def get_DRC_info_at(self, *index: int):
        """
        Get detailed DRC info at a point. Only species whose DRC is over 0.1 will show.
        Only available when a SpeciesEnergyDRCModifier is set in the setup file.
        :param index: The index of the grid point.
        :return: Fined DRC information.
        """
        pt = self._get_grid_point(*index)
        data = pt.getAllPointData().get("DRC")
        if not data:
            return "No DRC data found."
        return str(data.show(pt))

    def write(self, plot: bool = False, fig_size=None, contour_kw=None, clabel_kw=None, contourf_kw=None, plot_kw=None):
        """
        Write data with writers defined in the setup file.
            :param plot: Whether to generate and save plots along with data.
            Default: False
        :param fig_size: Figure size in inches as a tuple (width, height).
            Default: (9, 6)
        :param contour_kw: Keyword arguments passed to matplotlib's contour() for contour lines.
            Default: {'levels': 31, 'colors': 'black', 'linewidths': 0.5}
        :param clabel_kw: Keyword arguments passed to matplotlib's clabel() for contour labels.
            Default: {'inline': True, 'fontsize': 8}
        :param contourf_kw: Keyword arguments passed to matplotlib's contourf() for filled contours.
            Default: {'levels': 31, 'cmap': 'jet'}
        :param plot_kw: Keyword arguments passed to matplotlib's plot() for curves.
            Default: {}
        """
        scaler_class = self.model.getScaler().__class__.__name__
        metals = None
        if scaler_class == "com.wang_lab.mukip.components.scaler.LinearScaler":
            metals = {str(k): _wrap_double_array(v) for k,v in self.model.getScaler().getSurfaceDescriptorValue().items()}
        for writer in self.model.getWriters():
            writer.output()
            if plot:
                class_name = writer.__class__.__name__
                csv_path = str(writer.getOutputFile().getAbsolutePath())
                if class_name == "com.wang_lab.mukip.components.writer.CSV2DWriter":
                    plot_2d(csv_path, fig_size, contour_kw, clabel_kw, contourf_kw, str(writer.getDataType()), metals)
                elif class_name == "com.wang_lab.mukip.components.writer.CSV2DCustomWriter":
                    plot_2d(csv_path, fig_size, contour_kw, clabel_kw, contourf_kw, None, metals)
                elif class_name == "com.wang_lab.mukip.components.writer.CSV1DWriter":
                    plot_1d(csv_path, fig_size, plot_kw, str(writer.getDataType()), metals)
                elif class_name == "com.wang_lab.mukip.components.writer.CSV1DMultiWriter":
                    plot_1d(csv_path, fig_size, plot_kw, None, metals)
                else:
                    print(f"Plot method for {class_name} not implemented")

