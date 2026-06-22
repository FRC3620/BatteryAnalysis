import matplotlib.pyplot as plt
import numpy as np

# Data: different lengths for each group
data = {
    'Group A': [5, 7, 3],
    'Group B': [4, 8],
    'Group C': [6, 2, 9, 4]
}

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
        ax.bar(x_pos, val, width, color=colors[bar_idx % len(colors)])

# Formatting
ax.set_xticks(range(len(data)))
ax.set_xticklabels(data.keys())
plt.show()
