# Source - https://stackoverflow.com/a/62478149
# Posted by desert_ranger
# Retrieved 2026-04-03, License - CC BY-SA 4.0

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

labels = ['G1', 'G2', 'G3', 'G4']
male = [1, 3, 10, 20]
female = [2, 7,np.nan,np.nan]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
ax.bar(x - width/2, male, width, label='male')
ax.bar(x + width/2, female, width, label='female')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

fig.tight_layout()
plt.show()
