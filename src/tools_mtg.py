#  -*- coding: utf-8 -*-

"""
    root_cynaps.tools
    ~~~~~~~~~~~~~

    The module :mod:`root_cynaps.tools` defines useful functions for data preprocessing, graph making...

    :copyright: see AUTHORS.
    :license: see LICENSE for details.
"""

# TODO: add functions from making_graph.py and video.py

import os
from decimal import Decimal
from math import pi, cos, sin, floor
import numpy as np
import pandas as pd

from openalea.mtg import turtle as turt
from openalea.mtg.plantframe import color
import openalea.plantgl.all as pgl


# FUNCTIONS FOR DATA PREPROCESSING :
####################################

# TODO: see if this function should stay in tools, or move to simulations/run_rhizodep.py

def formatted_inputs(original_input_file="None", final_input_file='updated_input_file.csv', original_time_step_in_days=1 / 24., final_time_step_in_days=1.,
                     simulation_period_in_days=60., do_not_execute_if_file_with_suitable_size_exists=False):
    """
    This function creates a new input file containing data on soil temperature and sucrose input rate (in mol of sucrose per second),
    based on an original file. The new file is adapted to the required time step (higher, equal or lower than the original time step).
    If the option 'do_not_execute_if_file_with_suitable_size_exists' is set to True, a new file will be created only if the already-
    existing 'input_file.csv' does not contain the correct number of lines.
    """

    # If there is a file where the inputs of sucrose in the root system have to be read:
    if original_input_file != "None":

        # We first define the path and the file to read as a .csv:
        PATH1 = os.path.join('.', original_input_file)
        # Then we read the file and copy it in a dataframe "df":
        df = pd.read_csv(PATH1, sep=',', header=0)

        # simulation_period_in_days = df['time_in_days'].max()-df['time_in_days'].min()
        n_steps = int(floor(simulation_period_in_days / final_time_step_in_days)) + 1

        if do_not_execute_if_file_with_suitable_size_exists:
            PATH2 = os.path.join('.', 'input_file.csv')
            previous_file = pd.read_csv(PATH2, sep=',', header=0)

            if len(previous_file['step_number']) == n_steps:
                print("There is already an 'input_file.csv' of proper length for this simulation, "
                      "we therefore did not create a new input file here (if you wish to do so, please select 'do_not_execute_if_file_with_suitable_size_exists=False').")
                return previous_file

        # We create a new, final dataframe that will be used to read inputs of sucrose:
        input_frame = pd.DataFrame(
            columns=["step_number", "initial_time_in_days", "final_time_in_days", "soil_temperature_in_degree_Celsius",
                     "sucrose_input_rate"])
        input_frame["step_number"] = range(1, n_steps + 1)
        input_frame["initial_time_in_days"] = (input_frame["step_number"] - 1) * final_time_step_in_days * 1.
        input_frame["final_time_in_days"] = input_frame["initial_time_in_days"] + final_time_step_in_days

        print("Creating a new input file adapted to the required time step (time step =",
              "{:.2f}".format(Decimal(final_time_step_in_days)), "days)...")

        # CASE 1: the final time step is higher than the original one, so we have to calculate an average value:
        # -------------------------------------------------------------------------------------------------------
        if final_time_step_in_days >= original_time_step_in_days:

            # We initialize the row ID "j" in which exact sucrose inputs will be recorded:
            j = 0
            # We initialize the time over which sucrose input will be integrated:
            cumulated_time_in_days = 0.
            time_in_days = 0.
            sucrose_input = 0.
            sum_of_temperature_in_degree_days = 0.

            # For each line of the data frame that contains information on sucrose input:
            for i in range(0, len(df['time_in_days'])):

                # If the current cumulated time is below the time step of the main simulation:
                if (cumulated_time_in_days + original_time_step_in_days) < 0.9999 * final_time_step_in_days:
                    # Then the amount of time elapsed here is the initial time step:
                    net_elapsed_time_in_days = original_time_step_in_days
                    remaining_time = 0.
                else:
                    # Otherwise, we limit the elapsed time to the one necessary for reaching a round number of final_time_step_in_days:
                    net_elapsed_time_in_days = original_time_step_in_days - (
                            cumulated_time_in_days + original_time_step_in_days - final_time_step_in_days)
                    remaining_time = (cumulated_time_in_days + original_time_step_in_days - final_time_step_in_days)

                # In any case, the sucrose input and the sum of temperature are increased according to the elapsed time considered here:
                sucrose_input += df.loc[i, 'sucrose_input_rate'] * net_elapsed_time_in_days * 60 * 60 * 24.
                sum_of_temperature_in_degree_days += df.loc[i, 'soil_temperature_in_Celsius'] * net_elapsed_time_in_days

                # If at the end of the original time step corresponding to the line i in df, one final time step has been reached
                # or if this is the last line of the original table df to be read:
                if cumulated_time_in_days + original_time_step_in_days >= 0.9999 * final_time_step_in_days \
                        or i == len(df['time_in_days']) - 1:

                    # We move to the next row in the table to create:
                    j += 1
                    # print("   Creating line", j, "on", n_steps, "lines in the new input frame...")
                    # We record the final temperature and sucrose input rate:
                    input_frame.loc[j - 1, 'sucrose_input_rate'] = sucrose_input / (
                            (cumulated_time_in_days + net_elapsed_time_in_days) * 60. * 60. * 24.)
                    input_frame.loc[j - 1, 'soil_temperature_in_degree_Celsius'] = sum_of_temperature_in_degree_days \
                                                                                   / ((
                            cumulated_time_in_days + net_elapsed_time_in_days))

                    # We reinitialize the counter with the exact time that has not been included yet:
                    cumulated_time_in_days = remaining_time
                    # print "After reinitializing cumulated time, it is equal to", cumulated_time_in_days
                    # We reinitialize the sucrose input with the remaining sucrose that has not been taken into account:
                    sucrose_input = df.loc[i, 'sucrose_input_rate'] * (cumulated_time_in_days) * 60 * 60 * 24.
                    sum_of_temperature_in_degree_days = df.loc[i, 'soil_temperature_in_Celsius'] * (
                        cumulated_time_in_days)

                else:
                    cumulated_time_in_days += original_time_step_in_days

                # If the number of total lines of the final input frame has been reached:
                if j >= n_steps:
                    # Then we stop the loop here:
                    break

        # CASE 2: the final time step is higher than the original one, so we have to calculate an average value:
        # -------------------------------------------------------------------------------------------------------
        if final_time_step_in_days < original_time_step_in_days:

            # We initialize the row ID "i" in which the original values are read:
            i = 1
            # print "      Considering now line", i, "in the original table for time = ", df.loc[i, 'time_in_days']

            # We initialize the time over which sucrose input will be integrated:
            cumulated_time_in_days = 0.
            time_in_days = 0.
            sucrose_input = 0.
            sum_of_temperature_in_degree_days = 0.

            sucrose_input_rate_initial = df.loc[0, 'sucrose_input_rate']
            temperature_initial = df.loc[0, 'soil_temperature_in_Celsius']

            # For each line of the final table:
            for j in range(0, n_steps):

                # If the current cumulated time is below the time step of the main simulation:
                if cumulated_time_in_days + final_time_step_in_days < 0.9999 * original_time_step_in_days:
                    # Then the amount of time elapsed here is the initial time step:
                    net_elapsed_time_in_days = final_time_step_in_days
                    remaining_time = 0.
                else:
                    # Otherwise, we limit the elapsed time to the one necessary for reaching a round number of original_time_step_in_days:
                    net_elapsed_time_in_days = final_time_step_in_days - (
                            cumulated_time_in_days + final_time_step_in_days - original_time_step_in_days)
                    remaining_time = (cumulated_time_in_days + final_time_step_in_days - original_time_step_in_days)

                sucrose_input_rate = sucrose_input_rate_initial \
                                     + (df.loc[
                                            i, 'sucrose_input_rate'] - sucrose_input_rate_initial) / original_time_step_in_days * cumulated_time_in_days
                temperature = temperature_initial \
                              + (df.loc[
                                     i, 'soil_temperature_in_Celsius'] - temperature_initial) / original_time_step_in_days * cumulated_time_in_days

                print("   Creating line", j + 1, "on", n_steps, "lines in the new input frame...")
                # We record the final temperature and sucrose input rate:
                input_frame.loc[j, 'sucrose_input_rate'] = sucrose_input_rate
                input_frame.loc[j, 'soil_temperature_in_degree_Celsius'] = temperature

                # If at the end of the final time step corresponding to the line j in input_frame, one original time step has been reached:
                if cumulated_time_in_days + final_time_step_in_days >= 0.9999 * original_time_step_in_days:

                    # We record the current sucrose input rate and temperature in the original table:
                    sucrose_input_rate_initial = df.loc[i, 'sucrose_input_rate']
                    temperature = df.loc[i, 'soil_temperature_in_Celsius']

                    # We move to the next row in the original table, unless we are already at the last line:
                    if i < len(df['time_in_days']) - 1:
                        i += 1
                        # print "      Considering now line", i, "in the original table for time = ", df.loc[i, 'time_in_days']

                    # We reinitialize the counter with the exact time that has not been included yet:
                    cumulated_time_in_days = remaining_time

                else:

                    cumulated_time_in_days += final_time_step_in_days

                # If the number of total lines of the final input frame has been reached:
                if j >= n_steps:
                    # Then we stop the loop here:
                    break

    input_frame.to_csv(final_input_file, na_rep='NA', index=False, header=True)
    print("The new input file adapted to the required time step has been created and saved as 'updated_input_file.csv'.")

    return input_frame


def is_int(dt):
    """
    Returns True if dt is an integer, False in other cases.
    """
    try:
        num = int(dt)
    except ValueError:
        return False
    return True


def _buildDic(keyList, val, dic):
    if len(keyList) == 1:
        dic[keyList[0]] = val
        return

    newDic = dic.get(keyList[0], {})
    dic[keyList[0]] = newDic
    _buildDic(keyList[1:], val, newDic)


def buildDic(dict_scenario, dic=None):
    """
    Function that build a nested dictionary (dict of dict), which is used in simulations/scenario_parameters/maine_one_scenario.py
    e.g. buildDic({'a:b:c': 1, 'a:b:d': 2}) returns {'a': {'b': {'c': 1, 'd': 2}}}
    """
    if not dic:
        dic = {}

    for k, v in dict_scenario.items():
        if not pd.isnull(v):
            keyList = k.split(':')
            keyList_converted = []
            for kk in keyList:
                if is_int(kk):
                    keyList_converted.append(int(kk))
                else:
                    keyList_converted.append(kk)
            _buildDic(keyList_converted, v, dic)

    return dic


# FUNCTIONS TO DISPLAY THE RESULTS IN A GRAPH:
##############################################

# Defining functions for diplaying the root system in a 3D graph in PlantGL:
# --------------------------------------------------------------------------

def get_root_visitor():
    """
    This function describes the movement of the 'turtle' along the MTG for creating a graph on PlantGL.
    :return: root_visitor
    """

    def root_visitor(g, v, turtle):
        n = g.node(v)
        # For displaying the radius or length 10 times larger than in reality:
        zoom_factor = 10.
        radius = n.radius * zoom_factor
        length = n.length * zoom_factor
        angle_down = n.angle_down
        angle_roll = n.angle_roll

        # We get the x,y,z coordinates from the beginning of the root segment, before the turtle moves:
        position1 = turtle.getPosition()
        n.x1 = position1[0] / zoom_factor
        n.y1 = position1[1] / zoom_factor
        n.z1 = position1[2] / zoom_factor

        # The direction of the turtle is changed:
        turtle.down(angle_down)
        turtle.rollL(angle_roll)

        # Tropism is then taken into account:
        # diameter = 2 * n.radius * zoom_factor
        # elong = n.length * zoom_factor
        # alpha = tropism_intensity * diameter * elong
        # turtle.rollToVert(alpha, tropism_direction)
        # if g.edge_type(v)=='+':
        # diameter = 2 * n.radius * zoom_factor
        # elong = n.length * zoom_factor
        # alpha = tropism_intensity * diameter * elong
        turtle.elasticity = 0.06 * (n.original_radius / g.node(1).original_radius)
        turtle.tropism = (0, 0, -1)

        # The turtle is moved:
        turtle.setId(v)
        if n.type == "Root_nodule":
            # s=turt.Sphere(radius)
            # turtle.draw(s)
            turtle.setWidth(radius)
            index_parent = g.Father(v, EdgeType='+')
            parent = g.node(index_parent)
            turtle.F()
        else:
            turtle.setWidth(radius)
            turtle.F(length)

        # We get the x,y,z coordinates from the end of the root segment, after the turtle has moved:
        position2 = turtle.getPosition()
        n.x2 = position2[0] / zoom_factor
        n.y2 = position2[1] / zoom_factor
        n.z2 = position2[2] / zoom_factor

    return root_visitor


def my_colormap(g, property_name, cmap='jet', vmin=None, vmax=None, lognorm=True):
    """
    This function computes a property 'color' on a MTG based on a given MTG's property.
    :param g: the investigated MTG
    :param property_name: the name of the property of the MTG that will be displayed
    :param cmap: the type of color map
    :param vmin: the min value to be displayed
    :param vmax: the max value to be displayed
    :param lognorm: a Boolean describing whether the scale is logarithmic or not
    :return: the MTG with the corresponding color
    """

    prop = g.property(property_name)
    keys = prop.keys()
    values = list(prop.values())
    # m, M = int(values.min()), int(values.max())

    _cmap = color.get_cmap(cmap)
    norm = color.Normalize(vmin, vmax) if not lognorm else color.LogNorm(vmin, vmax)
    values = norm(values)

    colors = (_cmap(values)[:, 0:3]) * 255
    colors = np.array(colors, dtype=np.int).tolist()

    g.properties()['color'] = dict(zip(keys, colors))
    return g


def prepareScene(scene, width=1200, height=1200, scale=0., x_center=0., y_center=0., z_center=0.,
                 x_cam=0., y_cam=0., z_cam=0., grid=False):
    """
    This function returns the scene that will be used in PlantGL to display the MTG.
    :param scene: the scene to start with
    :param width: the width of the graph (in pixels)
    :param height: the height of the graph (in pixels)
    :param scale: a dimensionless factor for zooming in or out
    :param x_center: the x-coordinate of the center of the graph
    :param y_center: the y-coordinate of the center of the graph
    :param z_center: the z-coordinate of the center of the graph
    :param x_cam: the x-coordinate of the camera looking at the center of the graph
    :param y_cam: the y-coordinate of the camera looking at the center of the graph
    :param z_cam: the z-coordinate of the camera looking at the center of the graph
    :param grid: a Boolean describing whether grids should be displayed on the graph
    :return: scene
    """

    # We define the coordinates of the point cam_target that will be the center of the graph:
    cam_target = pgl.Vector3(x_center * scale,
                             y_center * scale + 0.7,
                             z_center * scale)
    # We define the coordinates of the point cam_pos that represents the position of the camera:
    cam_pos = pgl.Vector3(x_cam * scale,
                          y_cam * scale,
                          z_cam * scale)
    # We position the camera in the scene relatively to the center of the scene:
    pgl.Viewer.camera.lookAt(cam_pos, cam_target)
    # We define the dimensions of the graph:
    pgl.Viewer.frameGL.setSize(width, height)
    # We define whether grids are displayed or not:
    pgl.Viewer.grids.set(grid, grid, grid, grid)

    return scene


def circle_coordinates(x_center=0., y_center=0., z_center=0., radius=1., n_points=50):
    """
    This function calculates the coordinates of n points evenly distributed on a circle of a specified radius
    within the x-y plane for a given height (z).
    :param x_center: the x-coordinate of the center of the circle
    :param y_center: the y-coordinate of the center of the circle
    :param z_center: the z-coordinate of the center of the circle
    :param radius: the radius of the circle
    :param n_points: the number of points distributed on the circle
    :return: three lists containing all x-coordinates, y-coordinates and z-coordinates, respectively
    """

    # We initialize empty lists of coordinates for each of the three dimensions:
    x_coordinates = []
    y_coordinates = []
    z_coordinates = []

    # We initalize the angle at 0 rad:
    angle = 0
    # We calculate the increment theta that will be added to the angle for each new point:
    theta = 2 * pi / float(n_points)

    # For each point of the circle which coordinates should be calculated:
    for step in range(0, n_points):
        # We calculate the coordinates of the point corresponding to the new angle:
        x_coordinates.append(x_center + radius * cos(angle))
        y_coordinates.append(y_center + radius * sin(angle))
        z_coordinates.append(z_center)
        # And we increase the angle by theta:
        angle += theta

    return x_coordinates, y_coordinates, z_coordinates


def plot_mtg(g, prop_cmap='hexose_exudation', cmap='jet', lognorm=True, vmin=1e-12, vmax=3e-7,
             x_center=0., y_center=0., z_center=0.,
             x_cam=0., y_cam=4.7, z_cam=0, viewer=True):
    """
    This function creates a graph on PlantGL that displays a MTG and color it according to a specified property.
    :param g: the investigated MTG
    :param prop_cmap: the name of the property of the MTG that will be displayed in color
    :param cmap: the type of color map
    :param lognorm: a Boolean describing whether the scale is logarithmic or not
    :param vmin: the min value to be displayed
    :param vmax: the max value to be displayed
    :param x_center: the x-coordinate of the center of the graph
    :param y_center: the y-coordinate of the center of the graph
    :param z_center: the z-coordinate of the center of the graph
    :param x_cam: the x-coordinate of the camera looking at the center of the graph
    :param y_cam: the y-coordinate of the camera looking at the center of the graph
    :param z_cam: the z-coordinate of the camera looking at the center of the graph
    :return: the updated scene
    """

    visitor = get_root_visitor()
    # We initialize a turtle in PlantGL:
    turtle = turt.PglTurtle()
    # We make the graph upside down:
    turtle.down(180)
    # We initialize the scene with the MTG g:
    scene = turt.TurtleFrame(g, visitor=visitor, turtle=turtle, gc=False)
    # We update the scene with the specified position of the center of the graph and the camera:
    if viewer:
        prepareScene(scene, x_center=x_center, y_center=y_center, z_center=z_center, x_cam=x_cam, y_cam=y_cam, z_cam=z_cam, scale=1.5)
    # We compute the colors of the graph:
    my_colormap(g, prop_cmap, cmap=cmap, vmin=vmin, vmax=vmax, lognorm=lognorm)
    # We get a list of all shapes in the scene:
    shapes = dict((sh.id, sh) for sh in scene)
    # We use the property 'color' of the MTG calculated by the function 'my_colormap':
    colors = g.property('color')
    # We cover each node of the MTG:
    for vid in colors:
        if vid in shapes:
            n = g.node(vid)
            # If the element is not dead:
            if n.type != "Dead":
                # We color it according to the property cmap defined by the user:
                shapes[vid].appearance = pgl.Material(colors[vid])
            else:
                # Otherwise, we print it in black:
                shapes[vid].appearance = pgl.Material([0, 0, 0])
            # property=g.property(prop_cmap)
            # if n.property <=0:
            #     shapes[vid].appearance = pgl.Material([0, 0, 200])

    # Changing some shapes geometry according to the element:
    for vid in shapes:
        n = g.node(vid)
        # If the element is a nodule, we transform the cylinder into a sphere:
        if n.type == "Root_nodule":
            # We create a sphere corresponding to the radius of the element:
            s = pgl.Sphere(n.radius * 1.)
            # We transform the cylinder into the sphere:
            shapes[vid].geometry.geometry = pgl.Shape(s).geometry
            # We select the parent element supporting the nodule:
            index_parent = g.Father(vid, EdgeType='+')
            parent = g.node(index_parent)
            # We move the center of the sphere on the circle corresponding to the external envelop of the parent:
            angle = parent.angle_roll
            circle_x = parent.radius * 10 * cos(angle)
            circle_y = parent.radius * 10 * sin(angle)
            circle_z = 0
            shapes[vid].geometry.translation += (circle_x, circle_y, circle_z)

    # We return the new updated scene:
    new_scene = pgl.Scene()
    for vid in shapes:
        shapes[vid].geometry = pgl.Translated(0, 0, 0, shapes[vid].geometry)
        new_scene += shapes[vid]

    # Consider: https://learnopengl.com/In-Practice/Text-Rendering

    return new_scene
