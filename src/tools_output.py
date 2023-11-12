# Import
import openalea.plantgl.all as pgl

from src.tools_mtg import plot_mtg

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import numpy as np
from time import sleep


def plot_N(g, p, axs, prop_extracts, span_slider=0.1):

    range_min, range_max = [0 for k in prop_extracts], [0 for k in prop_extracts]
    scene = pgl.Scene()
    for k in range(len(p)):
        # Computing plot ranges for the selected properties
        props = g.property(p[k])
        max_scale = g.max_scale()
        plot_range = [props[vid] for vid in g.vertices(scale=max_scale) if g.property("struct_mass")[vid] != 0]
        x_span = max(plot_range) - min(plot_range)
        range_min[k], range_max[k] = np.mean(plot_range) - span_slider*x_span/2, np.mean(plot_range) + span_slider*x_span/2
        # Creating a color mesh in a separate window for colormap's interpretation
        cm = plt.cm.get_cmap('jet')
        ax = axs[k]
        ax.clear()
        y, x = np.histogram(plot_range, 20)
        colors = [cm(((j - range_min[k]) / (range_max[k] - range_min[k]))) for j in x]
        ax.bar(x[:-1], y, color=colors, width=x[1]-x[0])

        scene += plot_mtg(g,
                         prop_cmap=p[k],
                         lognorm=False,  # to avoid issues with negative values
                         vmin=range_min[k],
                         vmax=range_max[k],
                         k=k)

    pgl.Viewer.display(scene)

    return range_min, range_max


def plot_xr(datasets, vertice=[], summing=0, selection=[], supplementary_legend=[""]):
    # TODO : convert to class
    root = tk.Tk()
    root.title(f'2D data from vertices {str(vertice)[1:-1]}')
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=10)
    root.columnconfigure(1, weight=10)
    root.columnconfigure(2, weight=1)

    # Listbox widget to add plots
    lb = tk.Listbox(root)
    for k in range(len(selection)):
        lb.insert(k, selection[k])

    # to avoid double window popup
    plt.ioff()
    # Check the number of plots for right subplot divisions
    if len(vertice) in (0, 1):
        fig, ax = plt.subplots()
        ax = [ax]
    else:
        fig, ax = plt.subplots(len(vertice), 1)

    # Embed figure in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)

    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()

    toolbar.grid(row=1, column=1, sticky="NSEW")
    canvas.get_tk_widget().grid(row=2, column=1, sticky="NSEW")
    lb.grid(row=2, column=2, sticky="NSEW", columnspan=2)

    if supplementary_legend == [""]:
        datasets = [datasets]
    for d in range(len(datasets)):
        # If we plot global properties
        if len(vertice) == 0:
            # If properties are spatialized but we want an overall root system summary
            if summing != 0:
                datasets[d] = datasets[d].sum(dim="vid")*summing
            text_annot = [[]]
            if summing != 0:
                for prop in selection:
                    getattr(datasets[d], prop).plot.line(x='t', ax=ax[0], label=prop + supplementary_legend[d])
                    text_annot[0] += [ax[0].text(0, 0, ""), ax[0].text(0, 0, "")]
            else:
                v_extract = datasets[d].stack(stk=[dim for dim in datasets[d].dims if dim not in ("vid", "t")]).sel(vid=1)
                # automatic legends from xarray are structured the following way : modalities x properties
                legend = []
                unit = []
                for combination in np.unique(v_extract.coords["stk"]):
                    combination_extract = v_extract.sel(stk=combination)
                    for prop in selection:
                        getattr(combination_extract, prop).plot.line(x='t', ax=ax[0],
                                                                     label=prop + supplementary_legend[d],
                                                                     add_legend=False)
                        text_annot[0] += [ax[0].text(0, 0, ""), ax[0].text(0, 0, "")]
                        if len(np.unique(v_extract.coords["stk"])) > 1:
                            legend += [combination]
                        else:
                            legend += [""]
                        unit += [getattr(combination_extract, prop).attrs["unit"]]
                        ax[0].get_lines()[-1].set_label('_' + ax[0].get_lines()[-1].get_label() + ' (' + unit[-1] + ')')
                        ax[0].get_lines()[-1].set_visible(False)

            ax[0].set_ylabel("")
            ax[0].set_title("")

        # If we plot local properties
        else:
            text_annot = [[] for k in range(len(vertice))]
            for k in range(len(vertice)):
                v_extract = datasets[d].stack(stk=[dim for dim in datasets[d].dims if dim not in ("vid", "t")]).sel(vid=vertice[k])
                # automatic legends from xarray are structured the following way : modalities x properties
                legend = []
                unit = []
                for combination in np.unique(v_extract.coords["stk"]):
                    combination_extract = v_extract.sel(stk=combination)
                    for prop in selection:
                        getattr(combination_extract, prop).plot.line(x='t', ax=ax[k], label=prop + supplementary_legend[d], add_legend=False)
                        text_annot[k] += [ax[k].text(0, 0, ""), ax[k].text(0, 0, "")]
                        if len(np.unique(v_extract.coords["stk"])) > 1:
                            legend += [combination]
                        else:
                            legend += [""]
                        unit += [getattr(combination_extract, prop).attrs["unit"]]
                        ax[k].get_lines()[-1].set_label('_' + ax[k].get_lines()[-1].get_label() + ' (' + unit[-1]+')')
                        ax[k].get_lines()[-1].set_visible(False)

                ax[k].set_ylabel("")
                ax[k].set_title("")

    if len(vertice) == 0:
        def hover_global(event):
            if event.inaxes == ax[0]:
                # At call remove all annotations to prevent overlap
                for k in text_annot[0]: k.set_visible(False)
                lines = ax[0].get_lines()
                # for all variables lines in the axe
                for l in range(len(lines)):
                    # if the mouse pointer is on the line
                    cont, ind = lines[l].contains(event)
                    if cont and lines[l].get_visible():
                        # get the position
                        posx, posy = [lines[l].get_xdata()[ind['ind'][0]], lines[l].get_ydata()[ind['ind'][0]]]
                        # get variable name
                        label = "{}_{}\n{},{}".format(lines[l].get_label(),
                                                          ["{:.2e}".format(s) for s in legend[l]],
                                                          posx,
                                                          "{:.2e}".format(posy) + " " + unit[l])
                        # add text annotation to the axe and refresh
                        text_annot[0] += [ax[0].text(x=posx, y=posy, s=label)]
                        fig.canvas.draw_idle()
            sleep(1)

        fig.canvas.mpl_connect("motion_notify_event", hover_global)
    else:
        def hover_local(event):
            # for each row
            for axe in range(len(ax)):
                # if mouse event is in the ax
                if event.inaxes == ax[axe]:
                    # At call remove all annotations to prevent overlap
                    for k in text_annot[axe]: k.set_visible(False)
                    # for all variables lines in the axe
                    lines = ax[axe].get_lines()
                    for l in range(len(lines)):
                        # if the mouse pointer is on the line
                        cont, ind = lines[l].contains(event)
                        if cont and lines[l].get_visible():
                            # get the position
                            posx, posy = [lines[l].get_xdata()[ind['ind'][0]], lines[l].get_ydata()[ind['ind'][0]]]
                            # get variable name
                            label = "{}_{}\n{},{}".format(lines[l].get_label(),
                                                          ["{:.2e}".format(s) for s in legend[l]],
                                                          posx,
                                                          "{:.2e}".format(posy) + " " + unit[l])
                            # add text annotation to the axe and refresh
                            text_annot[axe] += [ax[axe].text(x=posx, y=posy, s=label)]
                            fig.canvas.draw_idle()
            sleep(1)

        fig.canvas.mpl_connect("motion_notify_event", hover_local)

    def on_click(event):
        if event.button is MouseButton.LEFT:
            # for each row
            for axe in range(len(ax)):
                # if mouse event is in the ax
                if event.inaxes == ax[axe]:
                    # for all variables lines in the axe
                    for line in ax[axe].get_lines():
                        # if the mouse pointer is on the line
                        cont, ind = line.contains(event)
                        if cont:
                            line.set_visible(False)
                            line.set_label('_'+line.get_label())
                            ax[axe].relim(visible_only=True)
                            ax[axe].autoscale()
                            ax[axe].legend()
            canvas.draw()

    def on_lb_select(event):
        # TODO maybe add possibility to normalize-add a plot for ease of reading
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        # for each row
        for axe in range(len(ax)):
            for line in ax[axe].get_lines():
                if value in line.get_label():
                    line.set_visible(True)
                    if line.get_label()[0] == '_':
                        line.set_label(line.get_label()[1:])
            ax[axe].relim(visible_only=True)
            ax[axe].autoscale()
            ax[axe].legend()
        canvas.draw()

    lb.bind('<<ListboxSelect>>', on_lb_select)

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Finally show figure
    root.mainloop()
