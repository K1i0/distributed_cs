import matplotlib.pyplot as plt


def plot_data(x, y, lables, y_limit=120000):
    for i in range(0, len(lables)):
        plt.plot(x, y[i], marker='o', linestyle='-', label=lables[i], alpha=0.7)

    plt.ylim(0, y_limit)
    plt.title('График относительных частот')
    plt.xlabel('Интервалы значений выборки')
    plt.ylabel('Относительные частоты')
    plt.legend()
    plt.show()