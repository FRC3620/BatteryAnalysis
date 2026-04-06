import collections
import csv
import json
import statistics

import matplotlib.pyplot as plt

data = collections.defaultdict(list)

with open('rollup.csv', 'r', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        id = row.get('battery_id')
        v = float(row.get('capacity_estimate'))

        data[id].append(v)

data = dict(sorted(data.items(), key=lambda item: statistics.mean(item[1]), reverse=True))
print(json.dumps(data,indent=1))


fig, ax = plt.subplots()
width = 0.2
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

# Iterate through groups to plot bars individually
for group_idx, (name, values) in enumerate(data.items()):
    n_bars = len(values)
    # Calculate starting offset to center the cluster
    start_offset = (n_bars - 1) * width / 2

    for bar_idx, val in enumerate(values):
        x_pos = group_idx - start_offset + (bar_idx * width)
        bars = ax.bar(x_pos, val, width, color=colors[bar_idx % len(colors)])
        ax.bar_label(bars, rotation=90, padding=3)

# Formatting
ax.set_xticks(range(len(data)))
ax.set_xticklabels(data.keys())
plt.show()
