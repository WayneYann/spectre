
import os
import shutil

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.ticker import FuncFormatter
from navicat_volcanic.helpers import bround
from navicat_volcanic.plotting2d import beautify_ax

matplotlib.use("Agg")


def plot_evo_save(
        result_solve_ivp,
        wdir,
        name,
        states,
        x_scale,
        more_species_mkm):

    r_indices = [i for i, s in enumerate(states) if s.lower().startswith("r")]
    p_indices = [i for i, s in enumerate(states) if s.lower().startswith("p")]

    if x_scale == "ls":
        t = np.log10(result_solve_ivp.t)
        xlabel = "log(time) (s)"
    elif x_scale == "s":
        t = result_solve_ivp.t
        xlabel = "time (s)"
    elif x_scale == "lmin":
        t = np.log10(result_solve_ivp.t / 60)
        xlabel = "log(time) (min)"
    elif x_scale == "min":
        t = result_solve_ivp.t / 60
        xlabel = "time (min)"
    elif x_scale == "h":
        t = result_solve_ivp.t / 3600
        xlabel = "time (h)"
    elif x_scale == "d":
        t = result_solve_ivp.t / 86400
        xlabel = "time (d)"
    else:
        raise ValueError(
            "x_scale must be 'ls', 's', 'lmin', 'min', 'h', or 'd'")

    fig, ax = plt.subplots(
        frameon=False, figsize=[4.2, 3], dpi=300, constrained_layout=True
    )
    # Catalyst--------------------------
    ax.plot(t,
            result_solve_ivp.y[0, :],
            "-",
            c="#797979",
            linewidth=1.5,
            alpha=0.85,
            zorder=1,
            label=states[0])

    # Reactant--------------------------
    color_R = [
        "#008F73",
        "#1AC182",
        "#1AC145",
        "#7FFA35",
        "#8FD810",
        "#ACBD0A"]

    for n, i in enumerate(r_indices):
        ax.plot(t,
                result_solve_ivp.y[i, :],
                "-",
                c=color_R[n],
                linewidth=1.5,
                alpha=0.85,
                zorder=1,
                label=states[i])

    # Product--------------------------
    color_P = [
        "#D80828",
        "#F57D13",
        "#55000A",
        "#F34DD8",
        "#C5A806",
        "#602AFC"]

    for n, i in enumerate(p_indices):
        ax.plot(t,
                result_solve_ivp.y[i, :],
                "-",
                c=color_P[n],
                linewidth=1.5,
                alpha=0.85,
                zorder=1,
                label=states[i])

    # additional INT-----------------
    color_INT = [
        "#4251B3",
        "#3977BD",
        "#2F7794",
        "#7159EA",
        "#15AE9B",
        "#147F58"]
    if more_species_mkm is not None:
        for i in more_species_mkm:
            ax.plot(t,
                    result_solve_ivp.y[i, :],
                    linestyle="dashdot",
                    c=color_INT[i],
                    linewidth=1.5,
                    alpha=0.85,
                    zorder=1,
                    label=states[i])

    beautify_ax(ax)
    plt.xlabel(xlabel)
    plt.ylabel('Concentration (mol/l)')
    plt.legend()
    # plt.grid(True, linestyle='--', linewidth=0.75)
    plt.tight_layout()
    fig.savefig(f"kinetic_modelling_{name}.png", dpi=400)

    np.savetxt(f't_{name}.txt', result_solve_ivp.t)
    np.savetxt(f'cat_{name}.txt', result_solve_ivp.y[0, :])
    np.savetxt(
        f'Rs_{name}.txt', result_solve_ivp.y[r_indices])
    np.savetxt(f'Ps_{name}.txt',
               result_solve_ivp.y[p_indices])

    if wdir:
        out = [
            f't_{name}.txt',
            f'cat_{name}.txt',
            f'Rs_{name}.txt',
            f'Ps_{name}.txt',
            f"kinetic_modelling_{name}.png"]

        if not os.path.isdir("output"):
            os.makedirs("output")

        for file_name in out:
            source_file = os.path.abspath(file_name)
            destination_file = os.path.join(
                "output/", os.path.basename(file_name))
            shutil.move(source_file, destination_file)

        if not os.path.isdir(os.path.join(wdir, "output/")):
            shutil.move("output/", os.path.join(wdir, "output"))
        else:
            print("Output already exist")
            move_bool = input("Move anyway? (y/n): ")
            if move_bool == "y":
                shutil.move("output/", os.path.join(wdir, "output"))
            elif move_bool == "n":
                pass
            else:
                move_bool = input(
                    f"{move_bool} is invalid, please try again... (y/n): ")


def plot_ci(ci, x2, y2, ax=None):
    if ax is None:
        try:
            ax = plt.gca()
        except Exception as m:
            return

    ax.fill_between(x2, y2 + ci, y2 - ci, color="#b9cfe7", alpha=0.6)

    return


def plotpoints(ax, px, py, cb, ms, plotmode):
    if plotmode == 1:
        s = 30
        lw = 0.3
    else:
        s = 15
        lw = 0.25
    for i in range(len(px)):
        ax.scatter(
            px[i],
            py[i],
            s=s,
            c=cb[i],
            marker=ms[i],
            linewidths=lw,
            edgecolors="black",
            zorder=2,
        )


def plotpoints_(ax, px, py, c, m, plotmode):
    if plotmode == 1:
        s = 30
        lw = 0.3
    else:
        s = 15
        lw = 0.25
    ax.scatter(
        px,
        py,
        s=s,
        c=c,
        marker=m,
        linewidths=lw,
        edgecolors="black",
        zorder=2,
    )


def plot_2d_combo(
    x,
    y,
    px,
    py,
    ci=None,
    ms=None,
    xmin=0,
    xmax=100,
    xbase=20,
    ybase=10,
    xlabel="X-axis",
    ylabel="Y-axis",
    filename="plot.png",
    rid=None,
    rb=None,
    plotmode=1,
    labels=None
):

    color = [
        "#FF6347",
        "#32CD32",
        "#4169E1",
        "#FFD700",
        "#8A2BE2",
        "#00FFFF"]

    marker = [
        "o",
        "^",
        "s",
        "P",
        "*",
        "X"
    ]
    fig, ax = plt.subplots(
        frameon=False, figsize=[4.2, 3], dpi=300, constrained_layout=True,
    )
    # Labels and key
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(xmin, xmax)
    plt.xticks(np.arange(xmin, xmax + 0.1, xbase))

    # no scatter plot
    if plotmode == 0:

        for i in range(y.shape[0]):
            ax.plot(
                x,
                y[i],
                "-",
                linewidth=1.5,
                color=color[i],
                alpha=0.95,
                label=labels[i])
            ax = beautify_ax(ax)
            if rid is not None and rb is not None:
                avgs = []
                rb.append(xmax)
                for i in range(len(rb) - 1):
                    avgs.append((rb[i] + rb[i + 1]) / 2)
                for i in rb:
                    ax.axvline(
                        i,
                        linestyle="dashed",
                        color="black",
                        linewidth=0.75,
                        alpha=0.75,
                    )
    # mono color scatter plot
    elif plotmode == 1:

        for i in range(y.shape[0]):
            ax.plot(
                x,
                y[i],
                "-",
                linewidth=1.5,
                color=color[i],
                alpha=0.95,
                zorder=1,
                label=labels[i])
            ax = beautify_ax(ax)
            if rid is not None and rb is not None:
                avgs = []
                rb.append(xmax)
                for i in range(len(rb) - 1):
                    avgs.append((rb[i] + rb[i + 1]) / 2)
                for i in rb:
                    ax.axvline(
                        i,
                        linestyle="dashed",
                        color="black",
                        linewidth=0.75,
                        alpha=0.75,
                        zorder=3,
                    )
            if ci[i] is not None:
                plot_ci(ci[i], x, y[i], ax=ax)
            plotpoints(ax, px, py[i], color[i], marker[i], plotmode)

    elif plotmode == 2:
        for i in range(y.shape[0]):
            ax.plot(
                x,
                y[i],
                "-",
                linewidth=1.5,
                color=color[i],
                alpha=0.95,
                zorder=1,
                label=labels[i])
            ax = beautify_ax(ax)
            if rid is not None and rb is not None:
                avgs = []
                rb.append(xmax)
                for i in range(len(rb) - 1):
                    avgs.append((rb[i] + rb[i + 1]) / 2)
                for i in rb:
                    ax.axvline(
                        i,
                        linestyle="dashed",
                        color="black",
                        linewidth=0.5,
                        alpha=0.75,
                        zorder=3,
                    )
                yavg = (y[i].max() + y[i].min()) * 0.5
                for i, j in zip(rid, avgs):
                    plt.text(
                        j,
                        yavg,
                        i,
                        fontsize=7.5,
                        horizontalalignment="center",
                        verticalalignment="center",
                        rotation="vertical",
                        zorder=4,
                    )
            if ci[i] is not None:
                plot_ci(ci[i], x, y[i], ax=ax)
            plotpoints(ax, px, py[i], np.repeat(
                [color[i]], len(px)), ms, plotmode)

    # TODO color by the ranking
    elif plotmode == 3 and y.shape[0] > 1:
        for i in range(y.shape[0]):
            ax.plot(
                x,
                y[i],
                "-",
                linewidth=1.5,
                color=color[i],
                alpha=0.95,
                zorder=1,
                label=labels[i])
            ax = beautify_ax(ax)
            if rid is not None and rb is not None:
                avgs = []
                rb.append(xmax)
                for i in range(len(rb) - 1):
                    avgs.append((rb[i] + rb[i + 1]) / 2)
                for i in rb:
                    ax.axvline(
                        i,
                        linestyle="dashed",
                        color="black",
                        linewidth=0.75,
                        alpha=0.75,
                        zorder=3,
                    )
            if ci[i] is not None:
                plot_ci(ci[i], x, y[i], ax=ax)
            plotpoints(ax, px, py[i], np.repeat(
                [color[i]], len(px)), ms, plotmode)

    ymin, ymax = ax.get_ylim()
    ymax = bround(ymax, ybase, type="max")
    ymin = bround(ymin, ybase, type="min")
    plt.ylim(ymin, ymax)
    plt.yticks(np.arange(ymin, ymax + 0.1, ybase))
    plt.legend(fontsize=10, loc='best')
    plt.savefig(filename)


def plot_evo(result_solve_ivp, name, states, x_scale, more_species_mkm=None):

    r_indices = [i for i, s in enumerate(states) if s.lower().startswith("r")]
    p_indices = [i for i, s in enumerate(states) if s.lower().startswith("p")]

    if x_scale == "ls":
        t = np.log10(result_solve_ivp.t)
        xlabel = "log(time) (s)"
    elif x_scale == "s":
        t = result_solve_ivp.t
        xlabel = "time (s)"
    elif x_scale == "lmin":
        t = np.log10(result_solve_ivp.t / 60)
        xlabel = "log(time) (min)"
    elif x_scale == "min":
        t = result_solve_ivp.t / 60
        xlabel = "time (min)"
    elif x_scale == "h":
        t = result_solve_ivp.t / 3600
        xlabel = "time (h)"
    elif x_scale == "d":
        t = result_solve_ivp.t / 86400
        xlabel = "time (d)"
    else:
        raise ValueError(
            "x_scale must be 'ls', 's', 'lmin', 'min', 'h', or 'd'")

    plt.rc("axes", labelsize=18)
    plt.rc("xtick", labelsize=18)
    plt.rc("ytick", labelsize=18)
    plt.rc("font", size=18)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)

    # Catalyst---------
    ax.plot(t,
            result_solve_ivp.y[0, :],
            c="#797979",
            linewidth=2,
            alpha=0.85,
            zorder=1,
            label=states[0])

    # Reactant--------------------------
    color_R = [
        "#008F73",
        "#1AC182",
        "#1AC145",
        "#7FFA35",
        "#8FD810",
        "#ACBD0A"]

    for n, i in enumerate(r_indices):
        ax.plot(t,
                result_solve_ivp.y[i, :],
                linestyle="--",
                c=color_R[n],
                linewidth=2,
                alpha=0.85,
                zorder=1,
                label=states[i])

    # Product--------------------------
    color_P = [
        "#D80828",
        "#F57D13",
        "#55000A",
        "#F34DD8",
        "#C5A806",
        "#602AFC"]

    for n, i in enumerate(p_indices):
        ax.plot(t,
                result_solve_ivp.y[i, :],
                linestyle="dashdot",
                c=color_P[n],
                linewidth=2,
                alpha=0.85,
                zorder=1,
                label=states[i])

    # additional INT-----------------
    color_INT = [
        "#4251B3",
        "#3977BD",
        "#2F7794",
        "#7159EA",
        "#15AE9B",
        "#147F58"]
    if more_species_mkm is not None:
        for i in more_species_mkm:
            ax.plot(t,
                    result_solve_ivp.y[i, :],
                    linestyle="dashdot",
                    c=color_INT[i],
                    linewidth=2,
                    alpha=0.85,
                    zorder=1,
                    label=states[i])

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible
    plt.xlabel(xlabel)
    plt.ylabel('Concentration [mol/l]')
    plt.legend(frameon=False)
    plt.grid(True, linestyle='--', linewidth=0.75)
    plt.tight_layout()

    ymin, ymax = ax.get_ylim()
    ybase = np.ceil(ymax) / 10
    ymax = bround(ymax, ybase, type="max")
    ymin = bround(ymin, ybase, type="min")
    plt.ylim(ymin, ymax)
    plt.yticks(np.arange(0, ymax + 0.1, ybase))

    fig.savefig(f"kinetic_modelling_{name}.png", dpi=400)


def plot_3d_(
    xint,
    yint,
    grid,
    px,
    py,
    ymin,
    ymax,
    x1min,
    x1max,
    x2min,
    x2max,
    x1base,
    x2base,
    x1label="X1-axis",
    x2label="X2-axis",
    ylabel="Y-axis",
    filename="plot.png",
    cb="white",
    ms="o",
):
    fig, ax = plt.subplots(
        frameon=False, figsize=[4.2, 3], dpi=300, constrained_layout=True
    )
    grid = np.clip(grid, ymin, ymax)
    norm = cm.colors.Normalize(vmax=ymax, vmin=ymin)
    ax = beautify_ax(ax)

    increment = np.round((ymax - ymin) / 10, 1)
    levels = np.arange(ymin, ymax + increment, increment / 100)

    cset = ax.contourf(
        xint,
        yint,
        grid,
        levels=levels,
        norm=norm,
        cmap=cm.get_cmap("jet", len(levels)),
    )

    # Labels and key
    plt.xlabel(x1label)
    plt.ylabel(x2label)
    plt.xlim(x1min, x1max)
    plt.ylim(x2max, x2min)
    plt.xticks(np.arange(x1min, x1max + 0.1, x1base))
    plt.yticks(np.arange(x2min, x2max + 0.1, x2base))

    def fmt(x, pos): return "%.0f" % x
    cbar = fig.colorbar(cset, format=FuncFormatter(fmt))
    cbar.set_label(ylabel, labelpad=15, rotation=270)
    tick_labels = ['{:.2f}'.format(value) for value in levels]
    cbar.set_ticklabels(tick_labels)

    for i in range(len(px)):
        ax.scatter(
            px[i],
            py[i],
            s=12.5,
            c=cb[i],
            marker=ms[i],
            linewidths=0.15,
            edgecolors="black",
        )
    plt.savefig(filename)


def plot_3d_np(
    xint,
    yint,
    grid,
    ymin,
    ymax,
    x1min,
    x1max,
    x2min,
    x2max,
    x1base,
    x2base,
    x1label="X1-axis",
    x2label="X2-axis",
    ylabel="Y-axis",
    filename="plot.png",
):
    fig, ax = plt.subplots(
        frameon=False, figsize=[4.2, 3], dpi=300, constrained_layout=True
    )
    grid = np.clip(grid, ymin, ymax)
    norm = cm.colors.Normalize(vmax=ymax, vmin=ymin)
    ax = beautify_ax(ax)

    increment = np.round((ymax - ymin) / 10, 1)
    levels = np.arange(ymin, ymax + increment, increment / 100)

    cset = ax.contourf(
        xint,
        yint,
        grid,
        levels=levels,
        norm=norm,
        cmap=cm.get_cmap("jet", len(levels)),
    )

    # Labels and key
    plt.xlabel(x1label)
    plt.ylabel(x2label)
    plt.xlim(x1min, x1max)
    plt.ylim(x2min, x2max)
    plt.xticks(np.arange(x1min, x1max + 0.1, x1base))
    plt.yticks(np.arange(x2min, x2max + 0.1, x2base))

    def fmt(x, pos): return "%.0f" % x
    cbar = fig.colorbar(cset, format=FuncFormatter(fmt))
    cbar.set_label(ylabel, labelpad=15, rotation=270)
    tick_labels = ['{:.2f}'.format(value) for value in levels]
    cbar.set_ticklabels(tick_labels)

    plt.savefig(filename)


def plot_3d_contour_regions_np(
    xint,
    yint,
    grid,
    x1min,
    x1max,
    x2min,
    x2max,
    x1base,
    x2base,
    x1label="X1-axis",
    x2label="X2-axis",
    ylabel="Y-axis",
    filename="plot.png",
    nunique=2,
    id_labels=[],
):
    fig, ax = plt.subplots(
        frameon=False, figsize=[4.2, 3], dpi=300, constrained_layout=True
    )
    ax = beautify_ax(ax)
    levels = np.arange(-0.1, nunique + 0.9, 1)
    cset = ax.contourf(
        xint,
        yint,
        grid,
        levels=levels,
        cmap=cm.get_cmap("Dark2", nunique + 1),
    )

    # Labels and key
    plt.xlabel(x1label)
    plt.ylabel(x2label)
    plt.xlim(x1min, x1max)
    plt.ylim(x2min, x2max)
    plt.xticks(np.arange(x1min, x1max + 0.1, x1base))
    plt.yticks(np.arange(x2min, x2max + 0.1, x2base))
    ax.contour(xint, yint, grid, cset.levels, colors="black", linewidths=0.1)
    def fmt(x, pos): return "%.0f" % x
    cbar = fig.colorbar(cset, format=FuncFormatter(fmt))
    cbar.set_ticks([])
    cbar.set_label(ylabel, labelpad=40, rotation=270)
    for j, tlab in enumerate(id_labels):
        cbar.ax.text(
            2,
            0.4 + j,
            tlab,
            ha="center",
            va="center",
            weight="light",
            fontsize=8,
            rotation=-90,
        )
        cbar.ax.get_yaxis().labelpad = 30
    plt.savefig(filename)
