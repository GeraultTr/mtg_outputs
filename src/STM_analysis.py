from src.analysis import main_workflow


def run(file, output_path, extract_props):
    """
    :param path: specify path to xarray netcdf output files from mtg logging
    :return:
    """
    main_workflow.run_analysis(file, output_path, extract_props)
