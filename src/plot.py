import matplotlib.pyplot as plt
import argparse
import json


def plot_data(x, y, labels, xlabel, ylabel, y_limit=120000, main_title=''):
    for i in range(0, len(labels)):
        plt.loglog(x, y[i], marker='o', linestyle='-', label=labels[i], alpha=0.7)

    # plt.ylim(0, y_limit)
    plt.title(main_title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Command line arguments parser")
    parser.add_argument('--input', type=str, default='input_files/plot_data1.json', help='Файл с входными данными для построения графика в фромате json')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as jfile:
        data = json.load(jfile)
        title = data["title"]
        legend = data["legend"]
        xlabel = data["xlabel"]
        ylabel = data["ylabel"]
        xdata = data["xdata"]
        ydata = data["ydata"]
    
    plot_data(xdata, ydata, legend, xlabel, ylabel, 1, title)


if __name__ == '__main__':
    main()