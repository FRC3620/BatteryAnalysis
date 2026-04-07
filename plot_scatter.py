import matplotlib.pyplot as plt

import collections
import csv
import json
import statistics

import matplotlib.pyplot as plt

data = collections.defaultdict(list)

x = []
y = []
labels = []

with open('rollup.csv', 'r', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        labels.append(row.get('battery_id'))
        x.append(float(row.get('capacity_estimate')))
        y.append(float(row.get('rint_reverse_start')))

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