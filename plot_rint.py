import collections
import csv
import statistics

import matplotlib as mpl
import matplotlib.pyplot as plt

def plot_rint_bars(axis, rint, title):
    width = 0.1

    colors = ['#ff0000']
    colors.extend(['#d0d0d0', '#e8e8e8'] * 10)

    sorted_rint = dict(sorted(rint.items(), key=lambda item: item[1][0]))

    # Iterate through groups to plot bars individually
    for group_idx, (name, values) in enumerate(sorted_rint.items()):
        n_bars = len(values)
        # Calculate starting offset to center the cluster
        start_offset = (n_bars - 1) * width / 2

        for bar_idx, val in enumerate(values):
            x_pos = group_idx - start_offset + (bar_idx * width)
            bars = axis.bar(x_pos, val, width, color=colors[bar_idx % len(colors)])
            # ax.bar_label(bars, rotation=90, padding=3)

    # Formatting
    axis.set_xlabel("Battery Id")
    axis.set_ylabel("$r_{int}$ (\u03A9)")
    axis.set_title(title)
    axis.set_xticks(range(len(sorted_rint)))
    axis.set_xticklabels(sorted_rint.keys())


rint_reverse_start = collections.defaultdict(list)
rint_reverse_end = collections.defaultdict(list)
bb_rint_start = collections.defaultdict(list)
bb_rint_end = collections.defaultdict(list)

with open('rollup.csv', 'r', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        battery_id = row.get('battery_id')
        if battery_id is None or battery_id == '' or int(battery_id) < 110:
            continue
        rint_reverse_start[battery_id].append(float(row.get('rint_reverse_start')))
        rint_reverse_end[battery_id].append(float(row.get('rint_reverse_end')))
        bb_rint_start[battery_id].append(float(row.get('Start Rint')))
        bb_rint_end[battery_id].append(float(row.get('End Rint')))

for rint_collection in (rint_reverse_start, rint_reverse_end, bb_rint_start, bb_rint_end):
    for k, v in rint_collection.items():
        average = statistics.mean(v)
        v.insert(0, average)

mpl.rcParams["savefig.directory"] = "."
mpl.rcParams["savefig.format"] = "pdf"

fig, ax = plt.subplots(2, 2, layout="constrained")
plot_rint_bars(ax[0, 0], rint_reverse_start, "$r_{int}$ @ start (tester)")
plot_rint_bars(ax[0, 1], rint_reverse_end, "$r_{int}$ @ end (tester)")
plot_rint_bars(ax[1, 0], bb_rint_start, "$r_{int}$ @ start (beak)")
plot_rint_bars(ax[1, 1], bb_rint_end, "$r_{int}$ @ end (beak)")

fig.suptitle("$r_{int}$", fontweight='bold')
fig.canvas.manager.set_window_title("rInt")

plt.show()
