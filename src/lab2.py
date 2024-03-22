import argparse
import json
import math
import sys
import plot as pt

EPS = 1e-3

def calc_RSTAR(t, N, n, lamb, meow, m):
    res = 0.0

    for i in range(n, N + 1):
        res += calc_Pj(i, meow, lamb, N) * calc_QR(i, t, n, lamb, meow, N, m)
    
    return 1 if res > 1 else res


def calc_USTAR(t, N, n, lamb, meow, m):
    res = 1.0

    for i in range(0, n):
        res -= calc_Pj(i, meow, lamb, N) * calc_QU(i, t, n, lamb, meow, N, m)
    
    return res


def calc_QR(i, t, n, lamb, meow, N, m):
    res = 0.0
    prev = -1.0

    l = 0
    while res - prev >= EPS:
        prev = res

        sum_pi = 0.0
        for r in range(0, i - n + l + 1):
            sum_pi += calc_pi(r, t, i, lamb)
        
        res += calc_u(l, t, meow, N, m, i) * sum_pi
        l += 1
    
    return res


def calc_QU(i, t, n, lamb, meow, N, m):
    res = 0.0
    prev = -1.0

    r = 0
    while res - prev >= EPS:
        prev = res

        sum_u = 0.0
        for l in range(0, n - i + r):
            sum_u += calc_u(l, t, meow, N, m, i)
        
        res += calc_pi(r, t, i, lamb) * sum_u
        r += 1
    
    return res


def calc_S(N, n, m, lamb, meow):
    if m == N:
        return (
            1.0 -
            (
                math.pow(lamb, N - n + 1) /
                math.pow(lamb + meow, N - n + 1)
            )
        )

    s = 0.0
    for i in range(n, N + 1):
        s += calc_Pj(i, meow, lamb, N)
    
    return s

def calc_delta_x(x):
    return 1 if x >= 0 else 0


def calc_Pj(j, meow, lamb, N):
    melamb = meow / lamb

    mul1 = math.pow(melamb, j)
    mul2 = 1 / calc_factorial(j)
    mul3 = 0.0

    for l in range(0, N + 1):
        mul3 += math.pow(melamb, l) * (1 / calc_factorial(l))
    
    return mul1 * mul2 * (1.0 / mul3)


def calc_pi(r, t, i, lamb):
    return (
        (math.pow(i * lamb * t, r) / calc_factorial(r)) *
        math.exp(-i * lamb * t)
    )


def calc_u(l, t, meow, N, m, i):
    return (
        (math.pow(meow * t, l) / calc_factorial(l)) *
        (
            calc_delta_x(N - i - m) * 
            math.pow(m, l) *
            math.exp(-m * meow * t) +
            calc_delta_x(m - N + i) *
            math.pow(N - i, l) *
            math.exp(-(N - i) * meow * t)
        )
    )


# Вычисление факториала факториал числа с использованием формулы Стирлинга, приближенно вычисляя значение через гамма-функцию
def calc_factorial(num):
    if num == 0 or num == 1:
        return 1
    return math.sqrt(2 * math.pi * num) * math.pow(num / math.exp(1), num)


def create_rstar_list(t_start, t_end, t_step, N, n, lamb, meow, m):
    rstars = []
    for t in range(t_start, t_end + t_step, t_step):
        rstars.append(calc_RSTAR(t, N, n, lamb, meow, m))
    
    return rstars


def create_ustar_list(t_start, t_end, t_step, N, n, lamb, meow, m):
    ustars = []
    for t in range(t_start, t_end + t_step, t_step):
        ustars.append(calc_USTAR(t, N, n, lamb, meow, m))
    
    return ustars

def create_s_list(n_start, n_end, n_step, N, lamb, meow, m):
    s = []
    for n in range(n_start, n_end + n_step, n_step):
        s.append(calc_S(N, n, m, lamb, meow))
    return s


def main():
    parser = argparse.ArgumentParser(description="Command line arguments parser")
    # Добавляем аргументы
    parser.add_argument("-R", action="store_true", help="Если флаг установлен, производится вычисление функции оперативной надежности")
    parser.add_argument("-U", action="store_true", help="Если флаг установлен, производится вычисление функции оперативной восстановимости")
    parser.add_argument("-S", action="store_true", help="Если флаг установлен, производится вычисление коэффициента готовности")
    
    parser.add_argument('--input', type=str, default='input_files/lab2/2.json', help='Файл с входными данными для вычислений в фромате json')
    parser.add_argument('--output', type=str, default='output_files/lab2/2.json', help='Файл с выходными данными для результатов вычислений в фромате json')

    parser.add_argument('--scale', type=int, default=300, help='Граница шкалы по Y')
    parser.add_argument('--xlabel', type=str, default='Момент времени t', help='Лейбл для оси X')
    parser.add_argument('--ylabel', type=str, default='Матожидание времени безотказной работы', help='Лейбл для оси Y')
    parser.add_argument('--gtitle', type=str, default='Средняя наработка до отказа', help='Титульный лейбл для графика')

    args = parser.parse_args()

    if not (args.R or args.U or args.S):
        sys.stderr.write("Необходимо указать флаг для определения вычислений (-R, -U или -S)\n")
        sys.exit()

    with open(args.input, 'r') as jfile:
        data = json.load(jfile)
        _N = int(data["N"])
        _n_start = int(data["n_start"])
        _n_end = int(data["n_end"])
        _n_step = int(data["n_step"])
        _lamb = data["lamb"]
        _meow = data["meow"]
        _m = data["m"]
        if args.R or args.U:
            _t_start = int(data["t_start"])
            _t_end = int(data["t_end"])
            _t_step = int(data["t_step"])

        
        print('N: {}\nlamb: {}\nm: {}\nmeow: {}\nn_start: {}\nn_end: {}\nn_step: {}'.format(_N, _lamb, _m, _meow, _n_start,
                                                                                        _n_end, _n_step))
    
    results = []
    if args.R:
        for n in range(_n_start, _n_end + _n_step):
            results.append(create_rstar_list(_t_start, _t_end, _t_step, _N, n, _lamb, _meow, _m))
    elif args.U:
        for n in range(_n_start, _n_end + _n_step):
            results.append(create_ustar_list(_t_start, _t_end, _t_step, _N, n, _lamb, _meow, _m))
    elif args.S:
        for m in _m:
            results.append(create_s_list(_n_start, _n_end, _n_step, _N, _lamb, _meow, m))
    else:
        sys.exit()

    if args.R:
        labels = ['n = 8', 'n = 9', 'n = 10']
    elif args.U:
        labels = ['n = 10', 'n = 11', 'n = 12', 'n = 13','n = 14','n = 15','n = 16']

    if args.R or args.U:
        ts = []
        for t in range(_t_start, _t_end + _t_step, _t_step):
            ts.append(t) 
        pt.plot_data(ts, results, labels, args.xlabel, args.ylabel, args.scale, args.gtitle)
    
    with open(args.output, 'w') as ofile:
        ofile.write(json.dumps(results))



if __name__ == '__main__':
    main()