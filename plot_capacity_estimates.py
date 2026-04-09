import collections
import csv
import statistics

import matplotlib as mpl
import matplotlib.pyplot as plt

capacity_by_battery_id = collections.defaultdict(list)

with open('rollup.csv', 'r', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        battery_id = row.get('battery_id')
        if battery_id is None or battery_id == '' or int(battery_id) < 110:
            continue
        v = float(row.get('capacity_estimate'))

        capacity_by_battery_id[battery_id].append(v)

for k, data1 in capacity_by_battery_id.items():
    average = statistics.mean(data1)
    data1.insert(0, average)

capacity_by_battery_id = dict(sorted(capacity_by_battery_id.items(), key=lambda item: item[1][0], reverse=True))

mpl.rcParams["savefig.directory"] = "."
mpl.rcParams["savefig.format"] = "pdf"

fig, ax = plt.subplots()
fig.suptitle("Capacity Estimates", fontsize=16, fontweight='bold')
fig.canvas.manager.set_window_title("Capacity Estimates")

width = 0.1
colors = ['#ff0000']
colors.extend(['#d0d0d0', '#e8e8e8']*10)

# Iterate through groups to plot bars individually
for group_idx, (name, values) in enumerate(capacity_by_battery_id.items()):
    n_bars = len(values)
    # Calculate starting offset to center the cluster
    start_offset = (n_bars - 1) * width / 2

    for bar_idx, val in enumerate(values):
        x_pos = group_idx - start_offset + (bar_idx * width)
        bars = ax.bar(x_pos, val, width, color=colors[bar_idx % len(colors)])
        # ax.bar_label(bars, rotation=90, padding=3)

# Formatting
ax.set_xticks(range(len(capacity_by_battery_id)))
ax.set_xticklabels(capacity_by_battery_id.keys())
ax.set_xlabel('Battery Id')
ax.set_ylabel('J')

plt.show()
