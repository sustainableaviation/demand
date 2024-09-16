import matplotlib.pyplot as plt
import numpy as np

# Define the labels for rows and columns
labels = ['LSZH', 'LSGG', 'KJFK', 'KSFO', 'DNAA', 'DNMM', '...']

# Define your 7x7 matrix of numeric values
matrix_values = np.array([
    [0, 1307, 946, 356, 0, 0, 0],
    [1185, 0, 323, 0, 0, 0, 0],
    [983, 366, 0, 3186, 0, 0, 0],
    [356, 0, 3428, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2213, 0],
    [0, 0, 0, 0, 2048, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
])

# Plotting as a table
plt.figure(figsize=(12, 9))  # Larger figure size

# Create the table plot
table = plt.table(cellText=matrix_values,
                  rowLabels=labels,
                  colLabels=labels,
                  loc='center',
                  cellLoc='center',
                  colWidths=[0.1]*len(labels),
                  rowColours=['lightblue'] * len(labels),  # First row light blue, rest white
                  colColours=['lightblue'] * len(labels))  # First column light blue, rest white

# Hide axes
ax = plt.gca()
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

# Save the figure as PNG without title and border
plt.savefig('custom_matrix.png', bbox_inches='tight', pad_inches=0, dpi=1000)

plt.show()
