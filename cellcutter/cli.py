import logging

import click
import pandas as pd

from . import cut as cut_mod


@click.command()
@click.argument("image", type=click.Path(exists=True, dir_okay=False))
@click.argument("segmentation_mask", type=click.Path(exists=True, dir_okay=False))
@click.argument("cell_data", type=click.Path(exists=True, dir_okay=False))
@click.argument("destination", type=click.Path())
@click.option(
    "--window-size",
    default=None,
    type=click.INT,
    help="Size of the cell thumbnail in pixels. Defaults to size of largest cell.",
)
@click.option(
    "--mask-cells/--dont-mask-cells",
    default=True,
    help="Fill every pixel not occupied by the target cell with zeros.",
)
@click.option(
    "-t", default=1, help="Number of threads used.",
)
def cut(image, segmentation_mask, cell_data, destination, window_size, mask_cells, t):
    """Cut out thumbnail images of all cells.

    IMAGE - Path to image in TIFF format, potentially with multiple channels.
    Thumbnails will be created from each channel.

    SEGMENTATION_MASK - Path to segmentation mask image in TIFF format.
    Used to automatically chose window size and find cell outlines.

    CELL_DATA - Path to CSV file with a row for each cell.
    Must contain columns CellID (must correspond to the cell IDs in the segmentation mask),
    Y_centroid, and X_centroid.

    DESTINATION - Path to a new directory where cell thumbnails will be stored in Zarr format
    (https://zarr.readthedocs.io/en/stable/index.html).

    The output is a Zarr array with the dimensions [#channels, #cells, window_size, window_size].
    """
    logging.basicConfig(
        format="%(threadName)s %(asctime)s %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    img = cut_mod.Image(image)
    segmentation_mask_img = cut_mod.Image(segmentation_mask)
    logging.info("Loading cell data CSV")
    cell_data_df = pd.read_csv(
        cell_data, usecols=["CellID", "X_centroid", "Y_centroid"]
    )
    logging.info(f"Cutting {cell_data_df.nrows} cells")
    cut_mod.process_all_channels(
        img,
        segmentation_mask_img,
        cell_data_df,
        destination,
        window_size=window_size,
        mask_cells=mask_cells,
        processes=t,
    )
