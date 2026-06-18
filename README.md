# pyinset

`pyinset` helps you create map insets on Matplotlib axes, with optional CRS-aware bounds transformation.

Note: This is an early prototype. The API and functionality may change significantly in future releases.

## Installation

Install from source (not published on PyPI yet):

```bash
git clone https://github.com/fncokg/pyinset.git
cd pyinset
pip install -e .
```

## Quick usage

```python
from pyinset import with_inset

def plot_map(ax):
	# your plotting logic here
	pass

# main_bounds is (minx, miny, maxx, maxy) in the coordinate system of your data
main_bounds = (100, 20, 125, 42)
inset_config = [
    # add one inset at the right bottom corner with the same scale factor as main map (1.0)
	{
		"bounds": (118, 3, 123, 8),
		"loc": "right bottom",
		"scale_factor": 1.0,
	}
]

fig, ax, inset_axes = with_inset(
	plot_func=plot_map,
	main_bounds=main_bounds,
	inset_config=inset_config,
    # auto-adjust figure size to fit your map
    resize_figure=True,
)
```

## Notes

- `with_inset(...)` computes axis limits from geographic bounds and creates inset axes.
- You can pass `from_crs` / `to_crs` if your data uses different coordinate reference systems.
