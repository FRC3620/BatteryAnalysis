import collections
import csv
import statistics

import matplotlib as mpl
import matplotlib.pyplot as plt


def plot_rint_bars(axis, rint_start, rint_end, title):
    width = 0.1

    start_colors = ['#00c000']
    start_colors.extend(['#d0d0d0', '#e8e8e8'] * 10)

    end_colors = ['#ff0000']
    end_colors.extend(['#d0d0d0', '#e8e8e8'] * 10)

    sorted_rint = dict(sorted(rint_end.items(), key=lambda item: item[1][0]))
    sorted_battery_ids = sorted_rint.keys()

    # Iterate through groups to plot bars individually
    group_idx = 0
    xtick_labels = []
    for battery_id in sorted_battery_ids:
        xtick_labels.append(battery_id + "\ns")
        values = rint_start.get(battery_id)

        n_bars = len(values)
        # Calculate starting offset to center the cluster
        start_offset = (n_bars - 1) * width / 2

        for bar_idx, val in enumerate(values):
            x_pos = group_idx - start_offset + (bar_idx * width)
            bars = axis.bar(x_pos, val, width, color=start_colors[bar_idx % len(start_colors)])

        group_idx += 1

        xtick_labels.append(battery_id + "\ne")
        values = rint_end.get(battery_id)

        n_bars = len(values)
        # Calculate starting offset to center the cluster
        start_offset = (n_bars - 1) * width / 2

        for bar_idx, val in enumerate(values):
            x_pos = group_idx - start_offset + (bar_idx * width)
            bars = axis.bar(x_pos, val, width, color=end_colors[bar_idx % len(end_colors)])

        group_idx += 1

    # Formatting
    axis.set_xlabel("Battery Id")
    axis.set_ylabel("$r_{int}$ (\u03A9)")
    axis.set_title(title + " $r_{int}$")
    axis.set_xticks(range(len(xtick_labels)))
    axis.set_xticklabels(xtick_labels)


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

fig, ax = plt.subplots(2, 1, layout="constrained")
# "$r_{int}$ @ start
plot_rint_bars(ax[0], rint_reverse_start, rint_reverse_end, "tester")
plot_rint_bars(ax[1], bb_rint_start, bb_rint_end, "beak")

fig.suptitle("$r_{int}$", fontweight='bold')
fig.canvas.manager.set_window_title("rInt")

plt.show()
