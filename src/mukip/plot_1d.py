import os

import matplotlib

from .plot_2d import read_csv_matrix, to_float_or_nan

matplotlib.use('Agg')

import matplotlib.pyplot as plt

def plot_1d(csv_path, fig_size=None, plot_kw=None, data_type=None, annotation=None):
    # Read raw data
    data = read_csv_matrix(csv_path)
    title = os.path.splitext(os.path.basename(csv_path))[0]

    if not data or len(data) < 2 or len(data[0]) < 2:
        raise ValueError("Invalid CSV format: at least a 2x2 grid (including header) is required.")

    title_row = data.pop(0)
    xlabel = title_row.pop(0)

    # Extract X values (first row, skip first element)
    x_vals = [to_float_or_nan(x) for x in title_row]

    # Extract Y values (first column, skip first element)
    parsed_data = {}
    for row in data:
        title = row.pop(0)
        parsed_data[title] = [to_float_or_nan(x) for x in row]


    # log z for special types
    if data_type in ['TOF']:
        plt.yscale('log')
        title = f"log({title})"

    # Plot
    if not fig_size:
        fig_size = (9, 6)
    plt.figure(figsize=fig_size)

    if not plot_kw:
        plot_kw = {}
    for key, value in parsed_data.items():
        plt.plot(x_vals, value, label=key, **plot_kw)
    plt.legend()

    if annotation:
        for text, pos in annotation.items():
            x, y = pos
            plt.plot(x, y, 'o', color='k', markersize=4)
            plt.annotate(text, xy=(x, y), fontsize=16)

    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(csv_path.replace('.csv', '.png'))
