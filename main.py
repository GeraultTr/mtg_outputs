from src.tools_output import plot_xr
from src.tools_mtg import plot_mtg
import openalea.plantgl.all as pgl


def launch_analysis(dataset, mtg, global_state_extracts, global_flow_extracts, state_extracts, flow_extracts,
                    output_dir="", global_sensitivity=True, global_plots=True, plot_architecture=True, STM_clustering=True):
    if global_sensitivity:
        # TERMINAL SENSITIVITY ANALYSIS
        # TODO : general sensitivity analysis on time-series data, but issue of post simulation Sensitivity Methods not existing
        # Global sensitivity analysis at the end of the simulation for now
        # Using a linear regression

        print("[INFO] Performing regression sensitivity on model final global states...")
        from src import global_sensitivity
        global_sensitivity.regression_analysis(dataset=dataset, output_path=output_dir, extract_prop=global_state_extracts)

    if global_plots:
        # PLOTTING GLOBAL OUTPUTS
        print("[INFO] Plotting global properties...")
        plot_xr(datasets=dataset, selection=list(global_state_extracts.keys()))
        plot_xr(datasets=dataset, selection=list(global_flow_extracts.keys()))

    if plot_architecture:
        # PLOTTING ARCHITECTURED VID LEGEND
        print("[INFO] Plotting topology and coordinate map...")
        # Plotting the vid as color to enable a better reading of groups
        mtg.properties()["v"] = dict(
            zip(list(mtg.properties()["struct_mass"].keys()), list(mtg.properties()["struct_mass"].keys())))

        from src.custom_colorbar import custom_colorbar
        custom_colorbar(min(mtg.properties()["v"].values()), max(mtg.properties()["v"].values()), unit="Vid number")

        scene = pgl.Scene()
        scene += plot_mtg(mtg,
                          prop_cmap="v",
                          lognorm=False,  # to avoid issues with negative values
                          vmin=min(mtg.properties()["struct_mass"].keys()),
                          vmax=max(mtg.properties()["struct_mass"].keys()))
        pgl.Viewer.display(scene)
        pgl.Viewer.saveSnapshot(output_dir + "/vid_map.png")

    if STM_clustering:
        # RUNNING STM CLUSTERING AND SENSITIVITY ANALYSIS
        # For some reason, dataset should be loaded before umap, and the run() call should be made at the end of
        # the workflow because tkinter locks everything
        # TODO : adapt to sliding windows along roots ?
        print("[INFO] Performing local organs' physiology clustering...")
        from src import STM_analysis
        pool_locals = {}
        pool_locals.update(state_extracts)
        pool_locals.update(flow_extracts)
        STM_analysis.run(file=dataset, output_path=output_dir, extract_props=pool_locals)
