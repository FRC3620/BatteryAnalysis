import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [10, 20, 25, 30, 42]

plt.scatter(x, y)
plt.xlabel("X-Axis Label")
plt.ylabel("Y-Axis Label")
plt.title("Scatter Plot Title")

labels = ['A', 'B', 'C', 'D', 'E']

fig, ax = plt.subplots()
ax.scatter(x, y)

for i, txt in enumerate(labels):
    ax.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.show()