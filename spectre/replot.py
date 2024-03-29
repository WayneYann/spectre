#!/usr/bin/env python
import argparse
import os
import shutil
import sys

import h5py
import numpy as np
from navicat_volcanic.plotting2d import plot_2d
from scipy.signal import savgol_filter, wiener

from plot_function import plot_2d_combo

if __name__ == "__main__":

    # Input
    parser = argparse.ArgumentParser(
        description="""Replot with different arguement for filtering method\n
    Guideline:
    1. lower window size, more resemblance to the original
    2. higher polynomail, more resemblance to the original
    3. vice versa, smoother-looking curve but deviates more from the original
            """)

    parser.add_argument(
        "i",
        help="h5py file from km_volcanic"
    )
    parser.add_argument(
        "-f",
        "--f",
        dest="filter",
        type=str,
        default="savgol",
        help="Filtering method for smoothening the volcano (default: savgol) (savgol, wiener, None)",
    )
    parser.add_argument(
        "-w",
        "--w",
        dest="window_length",
        type=int,
        nargs='+',
        help="The length of the filter window (i.e., the number of coefficients), must be less than 200",
    )
    parser.add_argument(
        "-p",
        "--p",
        dest="polyorder",
        type=int,
        nargs='+',
        help="The order of the polynomial used to fit the sample, required if using savgol. polyorder must be less than window_length.",
    )
    parser.add_argument(
        "-s",
        "--s",
        dest="save",
        action="store_true",
        help="Flag to save a new data. (default: False)",
    )

    args = parser.parse_args()
    filename = args.i
    filtering_method = args.filter
    window_length = args.window_length
    polyorder = args.polyorder
    save = args.save

    try:
        with h5py.File(filename, 'r') as f:
            # access the group containing the datasets
            group = f['data']

            # load each dataset into a numpy array
            descr_all = group['descr_all'][:]
            prod_conc_ = group['prod_conc_'][:]
            descrp_pt = group['descrp_pt'][:]
            prod_conc_pt_ = group['prod_conc_pt_'][:]
            cb = group['cb'][:]
            ms = group['ms'][:]
            cb = np.char.decode(cb)
            ms = np.char.decode(ms)
            tag = group['tag'][:]
            xlabel = group['xlabel'][:]
            ylabel = group['ylabel'][:]
    except Exception as e:
        sys.exit(f"Likely wrong h5 file, {e}")

    xlabel = xlabel[0].decode()
    ylabel = ylabel[0].decode()
    tag = tag[0].decode()

    print(
        f"Detect {prod_conc_.shape[0]} profiles in the input, require {prod_conc_.shape[0]} input for polyorder and window_length")
    if filtering_method == "savgol":
        assert len(polyorder) == len(
            window_length), "Number of polyorder is not equal to number of window_length"
    assert len(
        window_length) == prod_conc_.shape[0], "Number of window_length is not equal to number of the plot"
    print("Passed!")

    prod_conc_sm_all = []
    for i, prod_conc in enumerate(prod_conc_):
        if filtering_method == "savgol":
            prod_conc_sm = savgol_filter(
                prod_conc, window_length[i], polyorder[i])
        elif filtering_method == "wiener":
            prod_conc_sm = wiener(prod_conc, window_length[i])
        else:
            sys.exit("Invalid filtering method (savgol, wiener)")
        prod_conc_sm_all.append(prod_conc_sm)
    prod_conc_sm_all = np.array(prod_conc_sm_all)

    if np.any(np.max(prod_conc_sm_all) > 10):
        print("Concentration likely reported as %yield, set y_base to 10")
        y_base = 10
    else:
        print("set y_base to 0.1")
        y_base = 0.1

    out = []
    if prod_conc_.shape[0] > 1:
        plot_2d_combo(
            descr_all,
            prod_conc_sm_all,
            descrp_pt,
            prod_conc_pt_,
            xmin=descr_all[0],
            xmax=descr_all[-1],
            ybase=y_base,
            xlabel=xlabel,
            ylabel=ylabel,
            filename=f"km_volcano_{tag}_combo_polished.png",
            plotmode=3)
        out.append(f"km_volcano_{tag}_combo_polished.png")

        for i in range(prod_conc_sm_all.shape[0]):
            plot_2d(
                descr_all,
                prod_conc_sm_all[i],
                descrp_pt,
                prod_conc_pt_[i],
                xmin=descr_all[0],
                xmax=descr_all[-1],
                ybase=y_base,
                cb=cb,
                ms=ms,
                xlabel=xlabel,
                ylabel=ylabel,
                filename=f"km_volcano_{tag}_profile{i}.png",
                plotmode=3)
            out.append(f"km_volcano_{tag}_profile{i}.png")
    else:
        plot_2d(
            descr_all,
            prod_conc_sm_all[0],
            descrp_pt,
            prod_conc_pt_[0],
            xmin=descr_all[0],
            xmax=descr_all[-1],
            ybase=y_base,
            cb=cb,
            ms=ms,
            xlabel=xlabel,
            ylabel=ylabel,
            filename=f"km_volcano_{tag}_polished.png",
            plotmode=3)
        out.append(f"km_volcano_{tag}_polished.png")

        if save:
            # create an HDF5 file
            cb = np.array(cb, dtype='S')
            ms = np.array(ms, dtype='S')
            with h5py.File('data_polished.h5', 'w') as f:
                group = f.create_group('data')
                # save each numpy array as a dataset in the group

                group.create_dataset('descr_all', data=descr_all)
                group.create_dataset('prod_conc_', data=prod_conc_)
                group.create_dataset('descrp_pt', data=descrp_pt)
                group.create_dataset('prod_conc_pt_', data=prod_conc_sm_all)
                group.create_dataset('prod_conc_sm', data=prod_conc_sm)
                group.create_dataset('cb', data=cb)
                group.create_dataset('ms', data=ms)
                group.create_dataset('tag', data=[tag.encode()])
                group.create_dataset('xlabel', data=[xlabel.encode()])
                group.create_dataset('ylabel', data=[ylabel.encode()])
            out.append('data_polished.h5')

    aktun = filename.split("/")
    if aktun[0] != filename:
        aktun = "/".join(aktun[:-1])
        for file in out:
            destination_file = os.path.join(
                aktun, file)
            shutil.move(file, destination_file)
