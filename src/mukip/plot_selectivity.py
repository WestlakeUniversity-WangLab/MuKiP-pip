"""
Composite selectivity map for the command-line interface.

This module re-implements the "Selectivity Map" of MuKiP-Visual
(``SelectivityWindow``) for the headless ``mukip`` package. Every product's
selectivity field is rendered as a grayscale ``binary_r`` contour map, its
RGBA buffer is tinted with the product's colour, and all tinted buffers are
summed into one RGB image so that the dominant product at each point is
visible at a glance.

The compositing step follows the original MuKiP-Visual implementation
verbatim: each product is rasterized with ``contourf`` into a full-resolution
RGBA buffer first, then ``img += rgba * color / 255``. This keeps the smooth,
high-resolution look of the GUI version instead of down-sampling to the raw
grid resolution.
"""

import os

import numpy as np

import matplotlib
matplotlib.use('Agg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import to_rgba

# Palette used by MuKiP-Visual's SelectivityWindow for the first three
# products, extended with additional deterministic colours.
DEFAULT_COLORS = [
    (255, 0, 0),    # red
    (0, 0, 255),    # blue
    (0, 255, 0),    # green
    (255, 165, 0),  # orange
    (128, 0, 128),  # purple
    (0, 128, 128),  # teal
    (255, 105, 180),  # pink
    (128, 128, 0),  # olive
    (139, 69, 19),  # brown
    (70, 130, 180),  # steel blue
]


def _normalize_color(color):
    if isinstance(color, str):
        r, g, b, a = to_rgba(color)
        return np.asarray([r, g, b, a], dtype=np.float32) * 255.0

    color = np.asarray(color, dtype=np.float32)
    if color.size < 3:
        raise ValueError(f"Invalid colour: {color!r}")

    rgb = color[:3].copy()
    alpha = color[3] if color.size >= 4 else 255.0

    if rgb.max() <= 1.0:
        rgb = rgb * 255.0
    if alpha <= 1.0:
        alpha = alpha * 255.0

    return np.asarray([rgb[0], rgb[1], rgb[2], alpha], dtype=np.float32)


def resolve_colors(product_names, colors=None):
    product_names = list(product_names)
    if colors is None:
        colors = {}
    result = []
    for i, _name in enumerate(product_names):
        if _name in colors:
            color = colors[_name]
        else:
            color = DEFAULT_COLORS[i] if i < len(DEFAULT_COLORS) else DEFAULT_COLORS[-1]
        result.append(_normalize_color(color))
    return result


def _build_composite(product_names, selectivities, x_values, y_values, colors, save_each, each_dir,
                     axes_width_px, axes_height_px, dpi):
    x_grid, y_grid = np.meshgrid(x_values, y_values)

    sub_figsize = (axes_width_px / dpi, axes_height_px / dpi)

    image = None
    for name, selectivity, color in zip(product_names, selectivities, colors):
        fig = Figure(figsize=sub_figsize, dpi=dpi,
                     facecolor='none', edgecolor='none')
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
        ax.set_axis_off()
        ax.contourf(x_grid, y_grid, np.asarray(selectivity, dtype=float),
                    cmap='binary_r', levels=np.linspace(0, 1.0, 256))
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())

        if save_each:
            fig.savefig(os.path.join(each_dir, f"total_selectivity_{name}.png"))

        width, height = canvas.get_width_height()
        if image is None:
            image = np.zeros((height, width, 4), dtype=np.float16)
        image += rgba * color / 255.0

    image = np.clip(image, 0, 255)
    image[..., 3] = 255.0
    return image.astype(np.uint8)


def plot_selectivity(product_names, selectivities, x_values, y_values, ranges, output_path, fig_size=None, colors=None,
                     xlabel=None, ylabel=None, annotation=None, save_each=False, each_dir=None, dpi=None):
    product_names = list(product_names)
    selectivities = list(selectivities)
    if len(product_names) != len(selectivities):
        raise ValueError(
            f"Number of product names ({len(product_names)}) does not match "
            f"the number of selectivity fields ({len(selectivities)})."
        )

    if not fig_size:
        fig_size = (9, 6)
    if dpi is None:
        dpi = 100

    if save_each:
        if each_dir is None:
            each_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(each_dir, exist_ok=True)

    normalized_colors = resolve_colors(product_names, colors)

    fig = Figure(figsize=fig_size, dpi=dpi)
    ax = fig.add_subplot(111)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.set_title('Selectivity Map')
    fig.tight_layout()
    fig.canvas.draw()
    axes_width_px = int(round(ax.bbox.width))
    axes_height_px = int(round(ax.bbox.height))

    image = _build_composite(product_names, selectivities, x_values, y_values,
                             normalized_colors, save_each, each_dir,
                             axes_width_px, axes_height_px, dpi)

    extent = (*ranges[0], *ranges[1])
    ax.imshow(image, aspect='auto', extent=extent)

    if annotation:
        for text, pos in annotation.items():
            x, y = pos
            ax.plot(x, y, 'o', color='k', markersize=4)
            ax.annotate(text, xy=(x, y), fontsize=16)
        ax.set_xlim(*ranges[0])
        ax.set_ylim(*ranges[1])

    fig.savefig(output_path)
    return output_path
