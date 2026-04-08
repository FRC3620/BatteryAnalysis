import matplotlib.pyplot as plt

import collections
import csv
import json
import statistics

import matplotlib.pyplot as plt

ce = collections.defaultdict(list)
rint = collections.defaultdict(list)

with open('rollup.csv', 'r', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        battery_id = row.get('battery_id')
        if battery_id is None or int(battery_id) < 110:
            continue
        ce[battery_id].append(float(row.get('capacity_estimate')))
        rint[battery_id].append(float(row.get('rint_reverse_start')))

x = []
y = []
labels = []

for battery_id in ce.keys():
    labels.append(battery_id)
    x.append(statistics.mean(ce[battery_id]))
    y.append(statistics.mean(rint[battery_id]))

plt.scatter(x, y)
plt.xlabel("Capacity")
plt.ylabel("rInt @ start")
plt.title("Scatter Plot Title")
for i, txt in enumerate(labels):
    plt.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

#fig, ax = plt.subplots()
#ax.scatter(x, y)

#for i, txt in enumerate(labels):
#    ax.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.show()