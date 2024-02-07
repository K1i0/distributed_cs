# Написать программу расчета частотным методом математического ожидания
# времени Θ безотказной работы и среднего времени T восстановления ВС
# со структурной избыточностью

import json
import matplotlib.pyplot as plt

def calc_meow(_N, _l, _m, _meow):
    if ((_N - _m) <= _l) and (_l <= _N):
        return (_N - _l) * _meow
    elif (0 <= _l) and (_l <= (_N - _m)):
        return (_m * _meow)
    else:
        print("Error! None (N: {}, _l: {}, m: {}, meow: {})".format(_N, _l, _m, _meow))
        return None

def calc_uptime(_N, _n, _lamb, _m, _meow):
    uptime = 0.0
    for j in range(_n + 1, _N + 1):
        mul = 1.0 / (j * _lamb)
        compos = 1.0
        for l in range(_n, j - 1 + 1):
            compos *= calc_meow(_N, l, _m, _meow) / (l * _lamb)

        uptime += mul * compos

    uptime += 1.0 / _n * _lamb
    return uptime

def calc_recovery_time(_N, _n, _lamb, _m, _meow):
    if _n > 1:
        recovery_time = 0.0

        part1 = 1.0
        for l in range(1, _n - 1 + 1):
            part1 *= l * _lamb / calc_meow(_N, l, _m, _meow)
        part1 *= 1.0 / calc_meow(_N, 0.0, _m, _meow)

        part2 = 0.0
        for j in range(1, _n - 1 + 1):
            mul = 1.0 / j * _lamb
            compos = 1.0
            for l in range(j, _n - 1 + 1):
                compos *= l * _lamb / calc_meow(_N, l, _m, _meow)
            part2 += mul * compos

        recovery_time = part1 + part2
        return recovery_time
    elif _n == 1:
        return 1.0 / calc_meow(_N, 0.0, _m, _meow)
    else:
        return None

# Количество элементарных машин
_N = 0
_lamb = 0.0
# Количество восстанавливающих устройств восстанавливающей системы
_m = 0
_n_start = 0
_n_end = 0
_n_step = 0
# Интенсивность потока восстановления элементарных машин одним восстанавливающим устройством (в часах)
_meows = []

with open('input_files/test.json', 'r') as jfile:
    data = json.load(jfile)
    _N = int(data["N"])
    _lamb = float(data["lamb"])
    _m = int(data["m"])
    _n_start = int(data["n_start"])
    _n_end = int(data["n_end"])
    _n_step = int(data["n_step"])
    _meows = data["meows"]

uptime_from_meow = {1: [], 10: [], 100: [], 1000: []}
_ns = []
for _meow in _meows:
    for _n in range (_n_start, _n_end):
        if (_meow == 1):
            _ns.append(_n)
        uptime = calc_uptime(_N, _n, _lamb, _m, _meow)
        uptime_from_meow[_meow].append(uptime)
        print("Uptime: {} (N: {}, _lamb: {}, m: {}, n: {}, meow: {})".format(uptime, _N, _lamb, _m, _n, _meow))


plt.plot(_ns, uptime_from_meow[1], marker='o', linestyle='-')
# plt.xticks(gaps)
plt.ylim(0, 300)
plt.title('График относительных частот')
plt.xlabel('Интервалы значений выборки')
plt.ylabel('Относительные частоты')
plt.show()


# recovery_time = calc_recovery_time(_N, _n_start, _lamb, _m, _meows[0])