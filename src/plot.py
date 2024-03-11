import matplotlib.pyplot as plt


def plot_data(x, y, labels, xlabel, ylabel, y_limit=120000, main_title=''):
    for i in range(0, len(labels)):
        plt.loglog(x, y[i], marker='o', linestyle='-', label=labels[i], alpha=0.7)

    # plt.ylim(0, y_limit)
    plt.title(main_title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()