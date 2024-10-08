"""

This script contains the functions to plot the different graphs for the terrain and NOMAD results.

This script requires multiple libraries that are written in the `requirements.txt` to be installed in your Python environnement. 
Make sure to install them properly with the right version.

"""

import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np

def plot_terrain(x, y, obj_function, units, obj_function_value, n_wt, ub, boundary_shapely, exclusion_zones_shapely, wind_rose_path="", max_index="", max_ws="", cg="", ax="", plot_flow_map=False, full_wind_rose=False, save=False, save_name=""):
    """Script to evaluate the blackbox function.

    Parameters
    ----------
    x : list
        List of x coordinates.
    y : list
        List of y coordinates.
    obj_function : str
        Name of the objective function.
    units : str
        Units of the objective function.
    obj_function_value : int
        Value of the objective function.
    n_wt : int
        Number of wind turbines.
    ub : list
        Upper bound of the boundary zone on the x and y axis.
    boundary_shapely : list
        List of Shapely polygons for the boundary.
    exclusion_zones_shapely : list
        List of Shapely polygons for the exclusion zone.
    wind_rose_path : str
        Path to where the wind rose is saved.
    max_index : int
        Wind direction having the highest frequency.
    max_ws : int
        Wind speed with the highest frequency in the principal wind direction.
    cg :
        fmGROSS site with associated coordinates of the wind turbines and selected wind values.   
    ax : Pyplot Axis
        Parameter to set if there is already a Pyplot Axis created.
    plot_flow_map : Boolean
        If True then the flow map is plotted on top of the terrain.
    full_wind_rose : Boolean
        If True then the full wind rose is plotted in the top right corner insted of the major wind direction arrow.
    save : Boolean
        If True then the graph is save with the `save_name` name.
    save_name : str
        Name of the file.

    Returns
    -------
    Pyplot graph of the terrain.
    """
    
    if ax == "":    
        fig, ax = plt.subplots()

    if plot_flow_map:
        cg.flow_map(wd=[max_index*10], ws=[max_ws]).plot_wake_map(levels=100, plot_windturbines=False, ax=ax)

    boundary_filled = gpd.GeoSeries(boundary_shapely)
    boundary = boundary_filled.boundary
    ok_zone = boundary_filled
    ax.set_facecolor("lightsteelblue")

    if exclusion_zones_shapely != []:
        exclusion_zone_filled = gpd.GeoSeries(exclusion_zones_shapely)
        boundary_filled_index = gpd.GeoSeries(boundary_shapely*len(exclusion_zones_shapely)).boundary
        exclusion_zone = exclusion_zone_filled.boundary
        for polygon in exclusion_zone_filled:
            ok_zone = ok_zone.difference(polygon)
            null_zone_boundaries = boundary_filled_index.intersection(exclusion_zone_filled)
        ok_zone.plot(ax=ax, color='lightgreen', alpha=0.5, zorder=1)
        exclusion_zone_filled.plot(ax=ax, color=['gainsboro']*len(exclusion_zones_shapely), zorder=3)
        exclusion_zone.plot(ax=ax, color=['darkgrey']*len(exclusion_zones_shapely), hatch="///", linewidths=1, zorder=5)
        null_zone_boundaries.plot(ax=ax, color=['darkgreen']*len(exclusion_zones_shapely), linestyle='dashed', linewidths=1, zorder=4)
        ax.scatter(x, y, marker="o", s=40, color='red', linewidths=1, alpha=0.5, zorder=6, label='Wind Turbine')

    else:
        ok_zone.plot(ax=ax, color='lightgreen', alpha=0.5, zorder=1)
        ax.scatter(x, y, marker="o", s=40, color='red', linewidths=1, alpha=0.5, zorder=3, label='Wind Turbine')
    
    if isinstance(boundary_shapely, list): 
        boundary.plot(ax=ax, color=['darkgreen']*len(boundary_shapely), linewidths=1, zorder=2)
    else:
        boundary.plot(ax=ax, color=['darkgreen'], linewidths=1, zorder=2)
    plt.title( str(obj_function + " = %s " + units + ", Wind turbines : %s")%(np.round(obj_function_value, 4), n_wt))

    if full_wind_rose:
        wr_plot = inset_axes(ax,
                        width="20%", # width = 20% of parent_bbox
                        height="29%", 
                        loc=1)
        wr_plot.patch.set_edgecolor('black')  
        wr_plot.patch.set_linewidth(2) 
        im = plt.imread(wind_rose_path)
        wr_plot.imshow(im)
        wr_plot.axis('off')
    
    else:
        u = np.cos(np.radians(max_index*10))
        v = np.sin(np.radians(max_index*10))
        ax.quiver(ub[0]-100, ub[1]-100, u, v, 40, angles=270-(max_index*10), scale=15)

    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    ax.legend(loc='lower left')

    if save:
        plt.savefig(save_name)

def plot_result_nomad(np_evals, np_obj, best_eval, best_of, save_name):
    """Script to evaluate the blackbox function.

    Parameters
    ----------
    np_evals : array
        List of evaluations where the NOMAD solver could compute the objective function value.
    np_obj : array
        List of objective function values where the NOMAD solver could compute the objective function value.
    best_eval : list
        List of evaluations where the NOMAD solver improved the objective function value.
    best_of : list
        List of objective function values where the NOMAD solver improved the objective function value.
    save_name : str
        Name to save the figure.

    Returns
    -------
    Pyplot graph of the convergence plot.
    """

    plt.scatter(np_evals, np_obj, color='#d79494', s=10, marker='v', label="NOMAD")
    plt.step(best_eval, best_of, 'r', where='post')
    plt.xlabel("Number of function evaluations")
    plt.ylabel("Best Objective function value (GWh)")
    plt.title("Convergence plot")
    plt.xlim(xmin=0)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_name)
