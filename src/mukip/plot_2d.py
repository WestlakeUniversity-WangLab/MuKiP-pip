import os
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

def parse_axis_labels(label_str):
    """Extract A (Y-axis label) and B (X-axis label) from a string like 'A\\B'"""
    label_str = label_str.strip()
    if '\\' in label_str:
        a, b = label_str.split('\\', 1)
        return a.strip(), b.strip()
    else:
        return "Y", "X"

def read_csv_matrix(file_path):
    """Read CSV file into a 2D list of strings"""
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        matrix = [row for row in reader]
    return matrix

def to_float_or_nan(s):
    """Convert string to float; return np.nan if conversion fails"""
    try:
        return float(s)
    except ValueError:
        return np.nan

def plot_2d(csv_path, fig_size=None, contour_kw=None, clabel_kw=None, contourf_kw=None):
    # Read raw data
    data = read_csv_matrix(csv_path)
    title = os.path.splitext(os.path.basename(csv_path))[0]

    if not data or len(data) < 2 or len(data[0]) < 2:
        raise ValueError("Invalid CSV format: at least a 2x2 grid (including header) is required.")

    # Parse top-left cell (e.g., "A\\B")
    top_left = data[0][0]
    ylabel, xlabel = parse_axis_labels(top_left)

    # Extract X values (first row, skip first element)
    x_vals_str = data[0][1:]
    x_vals = np.array([to_float_or_nan(x) for x in x_vals_str])
    x_vals = x_vals[~np.isnan(x_vals)]

    # Extract Y values (first column, skip first element)
    y_vals_str = [row[0] for row in data[1:]]
    y_vals = np.array([to_float_or_nan(y) for y in y_vals_str])
    y_vals = y_vals[~np.isnan(y_vals)]

    # Extract Z data
    z_rows = []
    for i in range(1, len(data)):
        row = data[i]
        z_row = []
        for j in range(1, min(len(row), len(x_vals_str) + 1)):
            z_row.append(to_float_or_nan(row[j]))
        while len(z_row) < len(x_vals):
            z_row.append(np.nan)
        z_rows.append(z_row[:len(x_vals)])
    
    Z = np.array(z_rows, dtype=float)

    # Validate dimensions
    if Z.shape[0] != len(y_vals) or Z.shape[1] != len(x_vals):
        print(f"Warning: Data shape {Z.shape} doesn't match Y({len(y_vals)}) × X({len(x_vals)}).")

    # Create meshgrid
    X, Y = np.meshgrid(x_vals, y_vals)

    # Check for non-positive values (log undefined for <= 0)
    Z = np.log10(Z)

    # Plot
    if not fig_size:
        fig_size = (9, 6)
    plt.figure(figsize=fig_size)

    # Use LogNorm for logarithmic color scale
    if not contour_kw:
        contour_kw = {'levels': 31, 'colors': 'black', 'linewidths': 0.5}
    contour = plt.contour(X, Y, Z, **contour_kw)

    if not clabel_kw:
        clabel_kw = {'inline': True, 'fontsize': 8}
    plt.clabel(contour, **clabel_kw)

    if not contourf_kw:
        contourf_kw = {'levels': 31, 'cmap': 'jet'}
    filled = plt.contourf(X, Y, Z, **contourf_kw)
    plt.colorbar(filled)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'log({title})')
    plt.tight_layout()
    plt.savefig(csv_path.replace('.csv', '.png'))
