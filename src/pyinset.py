from pyproj import CRS, Transformer
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt


def limit_bbox(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    method: str = "cross",
    from_crs=CRS.from_epsg(4326),
    to_crs=CRS.from_epsg(4326),
) -> tuple:
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    if method == "cross":
        xs = np.concat([np.repeat((xmin + xmax) / 2, 20), np.linspace(xmin, xmax, 20)])
        ys = np.concat([np.linspace(ymin, ymax, 20), np.repeat((ymin + ymax) / 2, 20)])
    elif method == "box":
        xs = np.concat(
            [
                np.repeat(xmin, 20),
                np.linspace(xmin, xmax, 20),
                np.repeat(xmax, 20),
                np.linspace(xmin, xmax, 20),
            ]
        )
        ys = np.concat(
            [
                np.linspace(ymin, ymax, 20),
                np.repeat(ymax, 20),
                np.linspace(ymin, ymax, 20),
                np.repeat(ymin, 20),
            ]
        )
    elif method == "orthogonal":
        xs = np.array([xmin, xmax])
        ys = np.array([ymin, ymax])
    else:
        raise ValueError(f"Invalid method: {method}")
    tx, ty = transformer.transform(xs, ys)
    tx = tx[~np.isinf(tx)]
    ty = ty[~np.isinf(ty)]
    return np.nanmin(tx), np.nanmin(ty), np.nanmax(tx), np.nanmax(ty)


def config_inset(
    ax,
    inset_bounds,
    main_width,
    main_height,
    loc="right bottom",
    scale_factor=1.0,
    loc_bottom=None,
    loc_left=None,
    width=None,
    height=None,
    from_crs=CRS.from_epsg(4326),
    to_crs=CRS.from_epsg(4326),
):
    inset_bbox = limit_bbox(*inset_bounds, from_crs=from_crs, to_crs=to_crs)
    inset_xmin, inset_ymin, inset_xmax, inset_ymax = inset_bbox
    inset_width = inset_xmax - inset_xmin
    inset_height = inset_ymax - inset_ymin

    inset_wr = inset_width / main_width * scale_factor
    inset_hr = inset_height / main_height * scale_factor

    _hpo, _vpo = loc.split(" ") if loc else (None, None)
    if loc_left is None:
        _hpos2x = {
            "left": 0,
            "center": 0.5 - inset_wr / 2,
            "right": 1 - inset_wr,
        }
        assert _hpo in _hpos2x, f"Invalid horizontal position: {_hpo}"
        loc_left = _hpos2x[_hpo]
    if loc_bottom is None:
        _vpos2y = {
            "bottom": 0,
            "center": 0.5 - inset_hr / 2,
            "top": 1 - inset_hr,
        }
        assert _vpo in _vpos2y, f"Invalid vertical position: {_vpo}"
        loc_bottom = _vpos2y[_vpo]
    if width is None:
        width = inset_wr
    if height is None:
        height = inset_hr

    inset_bounds = (loc_left, loc_bottom, width, height)
    ax_ins = ax.inset_axes(inset_bounds)
    ax_ins.set_xticks([])
    ax_ins.set_yticks([])
    ax_ins.set_xlim(inset_xmin, inset_xmax)
    ax_ins.set_ylim(inset_ymin, inset_ymax)
    return ax_ins


def with_inset(
    plot_func,
    main_bounds,
    inset_config=None,
    from_crs=CRS.from_epsg(4326),
    to_crs=None,
    lims_method="cross",
    resize_figure=True,
    ax=None,
):
    if to_crs is None:
        to_crs = from_crs
    main_bbox = limit_bbox(
        *main_bounds, from_crs=from_crs, to_crs=to_crs, method=lims_method
    )

    main_xmin, main_ymin, main_xmax, main_ymax = main_bbox
    main_width = main_xmax - main_xmin
    main_height = main_ymax - main_ymin

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if resize_figure:
        fig_width, fig_height = fig.get_size_inches()
        aspect_ratio = main_width / main_height
        new_fig_height = fig_width / aspect_ratio
        fig.set_size_inches((fig_width, new_fig_height))
        pass

    inset_axes = []
    for config in inset_config:
        inset_bounds = config.pop("bounds")
        ax_ins = config_inset(
            ax,
            inset_bounds,
            main_width,
            main_height,
            from_crs=from_crs,
            to_crs=to_crs,
            **config,
        )
        plot_func(ax_ins)
        inset_axes.append(ax_ins)
    plot_func(ax)
    ax.set_xlim(main_xmin, main_xmax)
    ax.set_ylim(main_ymin, main_ymax)
    ax.axis("off")
    return fig, ax, inset_axes
