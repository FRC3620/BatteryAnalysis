import matplotlib.pyplot as plt

import collections
import csv
import statistics

import matplotlib.pyplot as plt


def one_scatter_plot(axis, ce, rint, title):
    x = []
    y = []
    labels = []

    for battery_id in ce.keys():
        labels.append(battery_id)
        x.append(statistics.mean(ce[battery_id]))
        y.append(statistics.mean(rint[battery_id]))

    axis.scatter(x, y)
    axis.set_xlabel("Capacity (J)")
    axis.set_ylabel("rInt (\u03A9)")
    axis.set_title(title)
    for i, txt in enumerate(labels):
        axis.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(0, 10), ha='center')

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

fig, ax = plt.subplots(2, 2)
one_scatter_plot(ax[0, 0], ce, rint_reverse_start, "rInt start (tester)")
one_scatter_plot(ax[1, 0], ce, rint_reverse_end, "rInt end (tester)")
one_scatter_plot(ax[0, 1], ce, bb_rint_start, "rInt start (beak)")
one_scatter_plot(ax[1, 1], ce, bb_rint_end, "rInt end (break)")

fig.suptitle("rInt vs Capacity", fontweight='bold')
fig.canvas.manager.set_window_title("rInt vs Capacity")

plt.show()