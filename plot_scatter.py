import matplotlib.pyplot as plt

import collections
import csv
import statistics

import matplotlib.pyplot as plt


def one_scatter_plot(axis, ce, rint, title, rint_min, rint_max):
    x = []
    y = []
    labels = []

    for battery_id in ce.keys():
        labels.append(battery_id)
        y.append(statistics.mean(ce[battery_id]))
        x.append(statistics.mean(rint[battery_id]))

    axis.scatter(x, y)
    # axis.set_xlim(rint_min, rint_max)
    axis.set_ylabel("Capacity (J)")
    axis.set_xlabel("rInt (\u03A9)")
    axis.set_title(title)
    for i, txt in enumerate(labels):
        axis.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(0, 5), ha='center')

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # Add text box (x, y, string, ...)
    axis.text(0.95, 0.95, "\u21d6 \u2261 \u263a", fontsize=12,
            bbox=props, transform=axis.transAxes, verticalalignment='top', horizontalalignment='right',)

ce = collections.defaultdict(list)
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
        ce[battery_id].append(float(row.get('capacity_estimate')))
        rint_reverse_start[battery_id].append(float(row.get('rint_reverse_start')))
        rint_reverse_end[battery_id].append(float(row.get('rint_reverse_end')))
        bb_rint_start[battery_id].append(float(row.get('Start Rint')))
        bb_rint_end[battery_id].append(float(row.get('End Rint')))

rint_min = float('inf')
rint_max = 0.0
for rint_collection in (rint_reverse_start, rint_reverse_end, bb_rint_start, bb_rint_end):
    for k, v in rint_collection.items():
        rint = statistics.mean(v)
        rint_min = min(rint_min, rint)
        rint_max = max(rint_max, rint)

rint_min = ((1000 * rint_min) - 1) / 1000
rint_max = ((1000 * rint_max) + 1) / 1000

fig, ax = plt.subplots(2, 2, layout="constrained")
one_scatter_plot(ax[0, 0], ce, rint_reverse_start, "rInt start (tester)", rint_min, rint_max)
one_scatter_plot(ax[1, 0], ce, rint_reverse_end, "rInt end (tester)", rint_min, rint_max)
one_scatter_plot(ax[0, 1], ce, bb_rint_start, "rInt start (beak)", rint_min, rint_max)
one_scatter_plot(ax[1, 1], ce, bb_rint_end, "rInt end (break)", rint_min, rint_max)

fig.suptitle("rInt vs Capacity", fontweight='bold')
fig.canvas.manager.set_window_title("rInt vs Capacity")

#plt.subplots_adjust(wspace=0.5, hspace=0.5)
plt.show()