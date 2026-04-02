import multiprocessing
from typing import Literal
import jpype

from mukip.plot_2d import plot_2d
from mukip.jvm_manager import get_class


def _wrap_thermo(thermo):
    return {str(k): float(v) for k, v in thermo.getValues().items()}

def _wrap_vector(vector):
    return [float(b.doubleValue()) for b in vector]

def _wrap_double_array(array):
    return [float(d) for d in array]

class MicrokineticModel:
    """
    A wrapped class for microkinetic modeling.
    """
    MKM = get_class("com.wang_lab.mukip.components.model.MicrokineticModel").class_.getField("Companion").get(None)
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
    def __init__(self, setup_file: str):
        """
        Create a new MicrokineticModel object.

        :param setup_file: The path of the setup file for microkinetic model
        """
        self.setup_file = setup_file
        self.model = self.MKM.reactionModel(jpype.JString(self.setup_file))

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

    def get_global_thermo(self):
        """
        Get global thermodynamic data.
        :return: A dictionary of all global thermodynamic variables.
        """
        return _wrap_thermo(self.model.getThermo())

    def get_grid_thermo(self, *index: int):
        """
        Get the thermodynamic data of a grid point.
        :param index: The index of the grid point.
        :return: A dictionary of all thermodynamic variables on this point.
        """
        return _wrap_thermo(self._get_grid_point(*index).getThermo())

    def run(self, method: Literal['map_sample', 'map_in_turn', 'map_expand', 'map_check']='map_sample', n_thread: int = n_cpu):
        """
        Run the microkinetic model with given method.
        :param method: The method to use to run the microkinetic model.
            - 'map_sample': Use sampling-expansion method (SEM), which boasts high solving efficiency and stability
            , and is highly recommended.
            - 'map_in_turn': Solve all points in turn.
            - 'map_expand': Solve all unsolved points from points with solution. It should be used when a partial set
            of points are successfully solved.
            - 'map_check': Check existing solutions on all points in turn. If the solution on a point is incorrect,
            it will attempt to solve it. If the solution fails, the data will be deleted to ensure that
            all solutions are correct after the method is completed.
        :param n_thread: Number of threads to use.
        """
        self.model.getMapper().map(method, n_thread, self.ArrayList(), None)

    def get_result(self, *index: int):
        """
        Get results on a point.
        :param index: The index of the grid point.
        :return: Results as a dictionary.
        """
        pt = self._get_grid_point(*index)
        results = {}
        if r := pt.getCoverage():
            adsorbates = self.model.get(self.Adsorbate)
            coverage = _wrap_vector(r)
            results["coverage"] = {str(ads.getName()): c for ads, c in zip(adsorbates, coverage)}
        if r := pt.getTof():
            fluids = self.model.get(self.Fluid)
            tof = _wrap_double_array(r)
            results["TOF"] = {str(gas.getName()): p for gas, p in zip(fluids, tof)}
        if r := pt.getCurrent():
            results["current"] = float(r)
        if r := pt.getPressure():
            gases = self.model.get(self.Gas)
            pressure = _wrap_vector(r)
            results["pressure"] = {str(gas.getName()): p for gas, p in zip(gases, pressure)}
        if r := pt.getConcentration():
            aquas = self.model.get(self.Aqua)
            concentration = _wrap_vector(r)
            results["concentration"] = {str(aq.getName()): c for aq, c in zip(aquas, concentration)}
        return results

    def get_variables(self, *index: int):
        """
        Get all fined variables on a point.
        :param index: The index of the grid point.
        :return: Fined variables as a dictionary.
        """
        pt = self._get_grid_point(*index)
        variables = self.model.getSolver().getFinePointValues(pt)
        results = {str(k): float(v.doubleValue()) for k, v in variables.items()}
        expressions = self.model.getSolver().getExpressionDictionary()
        buffer = self.LinkedHashMap()
        for k, v in expressions.items():
            results[k] = float(self.JUtils.toDouble(v.arithmetic(variables, expressions, buffer)))
        return results

    def write(self, plot: bool = False, fig_size=None, contour_kw=None, clabel_kw=None, contourf_kw=None):
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
        """
        for writer in self.model.getWriters():
            writer.output()
            if plot:
                class_name = writer.__class__.__name__
                csv_path = str(writer.getOutputFile().getAbsolutePath())
                if class_name == "com.wang_lab.mukip.components.writer.CSV2DCustomWriter":
                    plot_2d(csv_path, fig_size, contour_kw, clabel_kw, contourf_kw)
                else:
                    print(f"Plot method for {class_name} not implemented")

