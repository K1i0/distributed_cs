import json
import plot as pt
import argparse


def calc_meow(_N: int, _l: int, _m: int, _meow: int):
    if ((_N - _m) <= _l) and (_l <= _N):
        return (_N - _l) * _meow
    elif (0 <= _l) and (_l < (_N - _m)):
        return _m * _meow
    else:
        print("Error! None (N: {}, _l: {}, m: {}, meow: {})".format(_N, _l, _m, _meow))
        return None


def calc_uptime(_N, n, _lamb, _m, _meow):
    uptime = 0.0
    for j in range(n + 1, _N + 1):
        compos = 1.0
        for l in range(n, j - 1 + 1):
            compos *= calc_meow(_N, l, _m, _meow) / (l * _lamb)

        uptime += (1.0 / (j * _lamb)) * compos

    uptime += 1.0 / (n * _lamb)
    return uptime


def create_uptime_list(n_start, n_end, n_step, _N, _lamb, _m, _meows):
    uptime_list = []
    for n in range(n_start, n_end + 1, n_step):
        if use_lamb:
            uptime_result = calc_uptime(_N, n, _lamb[i], _m[0], _meows[0])
        elif use_m:
            uptime_result = calc_uptime(_N, n, _lamb[0], _m[i], _meows[0])
        else:
            uptime_result = calc_uptime(_N, n, _lamb[0], _m[0], _meows[i])
        uptime_list.append(uptime_result)
    return [round(val, 4) for val in uptime_list]


def calc_recovery_time(_N, n, _lamb, _m, _meow):
    if n > 1:
        part1 = 1.0
        for l in range(1, n - 1 + 1):
            part1 *= (l * _lamb) / calc_meow(_N, l, _m, _meow)
        part1 *= 1.0 / calc_meow(_N, 0, _m, _meow)

        part2 = 0.0
        for j in range(1, n - 1 + 1):
            compos = 1.0
            for l in range(j, n - 1 + 1):
                compos *= (l * _lamb) / calc_meow(_N, l, _m, _meow)
            part2 += (1.0 / (j * _lamb)) * compos

        recovery_time = part1 + part2
        return recovery_time
    elif n == 1:
        return 1.0 / calc_meow(_N, 0, _m, _meow)
    else:
        return None


def create_recovery_list(n_start, n_end, n_step, _N, _lamb, _m, _meows):
    recovery_list = []
    for n in range(n_start, n_end + 1, n_step):
        if use_lamb:
            recovery_result = calc_recovery_time(_N, n, _lamb[i], _m[0], _meows[0])
        elif use_m:
            recovery_result = calc_recovery_time(_N, n, _lamb[0], _m[i], _meows[0])
        else:
            recovery_result = calc_recovery_time(_N, n, _lamb[0], _m[0], _meows[i])
        recovery_list.append(recovery_result)
    return [round(val, 4) for val in recovery_list]


# N - Количество элементарных машин
# m - Количество восстанавливающих устройств восстанавливающей системы
# μ - Интенсивность потока восстановления элементарных машин одним восстанавливающим устройством (в часах)

# Создаем парсер аргументов
parser = argparse.ArgumentParser(description="Command line arguments parser")
# Добавляем аргументы
parser.add_argument('--input', type=str, default='input_files/21.json', help='Файл с входными данными для вычислений в фромате json')
parser.add_argument('--output', type=str, default='output_files/res.json', help='Файл с выходными данными для результатов вычислений в фромате json')
parser.add_argument('--mode', type=str, default='uptime', help='Выбор показателя для вычисления (uptime или recover)')
parser.add_argument('--scale', type=int, default=300, help='Граница шкалы по Y')

parser.add_argument('--xlabel', type=str, default='Число ЭМ в основной подсистеме', help='Лейбл для оси X')
parser.add_argument('--ylabel', type=str, default='Матожидание времени безотказной работы', help='Лейбл для оси Y')
parser.add_argument('--gtitle', type=str, default='Средняя наработка до отказа', help='Титульный лейбл для графика')
# Разбираем аргументы командной строки
args = parser.parse_args()

with open(args.input, 'r') as jfile:
    data = json.load(jfile)
    _N = int(data["N"])
    _lamb = data["lamb"]
    _m = data["m"]
    _n_start = int(data["n_start"])
    _n_end = int(data["n_end"])
    _n_step = int(data["n_step"])
    _meows = data["meows"]
    print('N: {}\nlamb: {}\nm: {}\nmeow: {}\nn_start: {}\nn_end: {}\nn_step: {}'.format(_N, _lamb, _m, _meows, _n_start,
                                                                                        _n_end, _n_step))

uptimes_list = []
recoveries_list = []

conditions = [
    (len(_meows) > 1, _meows, False, False),
    (len(_lamb) > 1, _lamb, True, False),
    (len(_m) > 1, _m, False, True)
]

for condition, parameter, use_lamb, use_m in conditions:
    if condition:
        for i in range(len(parameter)):
            if args.mode == 'uptime':
                uptimes_list.append(
                    create_uptime_list(_n_start, _n_end, _n_step, _N, _lamb, _m, _meows))
                print(uptimes_list[i])
            else:
                recoveries_list.append(
                    create_recovery_list(_n_start, _n_end, _n_step, _N, _lamb, _m, _meows))
                print(recoveries_list[i])

        break  # Завершаем цикл после выполнения одного из условий

_ns = []
for n in range(_n_start, _n_end + 1, _n_step):
    _ns.append(n)

if len(_meows) > 1:
    if args.mode == 'uptime':
        labels = ['μ = 1 1/hours', 'μ = 10 1/hours', 'μ = 100 1/hours', 'μ = 1000 1/hours']
    else:
        labels = ['μ = 1 1/hours', 'μ = 2 1/hours', 'μ = 4 1/hours', 'μ = 6 1/hours']
elif len(_lamb) > 1:
    labels = ['λ = 10^-5 1/hours', 'λ = 10^-6 1/hours', 'λ = 10^-7 1/hours', 'λ = 10^-8 1/hours', 'λ = 10^-9 1/hours']
else:
    labels = ['m = 1', 'm = 2', 'm = 3', 'm = 4']

if args.mode == 'uptime':
    pt.plot_data(_ns, uptimes_list, labels, args.xlabel, args.ylabel, args.scale, args.gtitle)
else:
    pt.plot_data(_ns, recoveries_list, labels, args.xlabel, args.ylabel, args.scale, args.gtitle)

with open(args.output, 'w') as ofile:
    if args.mode == 'uptime':
        ofile.write(json.dumps(uptimes_list))
    else:
        ofile.write(json.dumps(recoveries_list))
