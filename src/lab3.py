import json
import plot as pt
import argparse
import threading
from datetime import datetime
import sys
import time
import multiprocessing


stop_event = threading.Event()


def show_worktime(start_time):
    while not stop_event.is_set():
        current_time = datetime.now()
        sys.stdout.write('\r' + 'Duration: {} '.format(current_time - start_time))
        time.sleep(.1)
        sys.stdout.flush()


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
        uptime_result = calc_uptime(_N, n, _lamb, _m, _meows)
        uptime_list.append(uptime_result)
    return [round(val, 4) for val in uptime_list]


# Принимает кортеж args в качестве входных данных (start_j, end_j, n, _lamb, _N, _m и _meow)
# Вычисляет значение (частичное произведение) для непрерывного блока j
def calc_recovery_time_part(args):
    start_j, end_j, n, _lamb, _N, _m, _meow = args
    part2 = 0.0
    for j in range(start_j, end_j + 1):
        compos = 1.0
        for l in range(j, n - 1 + 1):
            compos *= (l * _lamb) / calc_meow(_N, l, _m, _meow)
        part2 += (1.0 / (j * _lamb)) * compos
    return part2


def calc_recovery_time(_N, n, _lamb, _m, _meow):
    if n == 1:
        return 1.0 / calc_meow(_N, 0, _m, _meow)
    elif n > 1:
        part1 = 1.0
        for l in range(1, n - 1 + 1):
            part1 *= (l * _lamb) / calc_meow(_N, l, _m, _meow)
        part1 *= 1.0 / calc_meow(_N, 0, _m, _meow)

        # Распараллелить вычисления части среднего времени восстановления
        # Настройка пула процессов для параллельного вычисления
        pool = multiprocessing.Pool()

        num_cores = multiprocessing.cpu_count()
        chunk_size = n // num_cores
        # print(f'cpu_count: {num_cores}, chunk_size: {chunk_size}')
        
        # Создаем аргументы для каждого блока
        args_list = []
        for start_j in range(1, n - 1, chunk_size):
            end_j = min(start_j + chunk_size - 1, n - 1)
            # print(f'start_j: {start_j}, end_j: {end_j}')
            args_list.append((start_j, end_j, n, _lamb, _N, _m, _meow))
        
        # Распараллеливаем вычисления
        part2_results = pool.map_async(calc_recovery_time_part, args_list)

        # Получаем результаты
        part2_values = part2_results.get()

        # Закрываем пул
        pool.close()
        pool.join()
        
        # Суммируем значения part2
        part2 = sum(part2_values)
        recovery_time = part1 + part2
        return recovery_time
    else:
        return None


def create_recovery_list(n_start, n_end, n_step, _N, lamb, m, meow):
    recovery_list = []
    for n in range(n_start, n_end + 1, n_step):
        recovery_result = calc_recovery_time(_N, n, lamb, m, meow)
        print(recovery_result)
        recovery_list.append(recovery_result)
    return [round(val, 4) for val in recovery_list]



def main():
    # N - Количество элементарных машин
    # m - Количество восстанавливающих устройств восстанавливающей системы
    # μ - Интенсивность потока восстановления элементарных машин одним восстанавливающим устройством (в часах)

    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Command line arguments parser")
    # Добавляем аргументы
    parser.add_argument('--input', type=str, default='input_files/lab1/21.json', help='Файл с входными данными для вычислений в фромате json')
    parser.add_argument('--output1', type=str, default='output_files/lab3/res_uptime.json', help='Файл с выходными данными для результатов вычислений в фромате json')
    parser.add_argument('--output2', type=str, default='output_files/lab3/res_recovery.json', help='Файл с выходными данными для результатов вычислений в фромате json')

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

    start_time = datetime.now()
    worktime_thread = threading.Thread(target=show_worktime, args=(start_time,), daemon=True)
    worktime_thread.daemon = True

    try:
        worktime_thread.start()
        print()
    except (KeyboardInterrupt, SystemExit):
        worktime_thread.join()
        sys.exit()

    uptimes_list = []
    recoveries_list = []

    conditions = [
        (len(_meows) > 1, _meows, False, False),
        (len(_lamb) > 1, _lamb, True, False),
        (len(_m) > 1, _m, False, True)
    ]

    # for condition, parameter, use_lamb, use_m in conditions:
    #     if condition:
    #         for i in range(len(parameter)):
    #             uptimes_list.append(
    #                     create_uptime_list(_n_start, _n_end, _n_step, _N, _lamb, _m, _meows))
    #             print(uptimes_list[i])
    #             recoveries_list.append(
    #                     create_recovery_list(_n_start, _n_end, _n_step, _N, _lamb, _m, _meows))
    #             print(recoveries_list[i])
                    

            # break  # Завершаем цикл после выполнения одного из условий

    index = 0
    for lamb in _lamb:
        print(f'lamb: {lamb}')
        for meow in _meows:
            print(f'meow: {meow}')
            for m in _m:
                print(f'm: {m}')
                # uptimes_list.append(
                #         create_uptime_list(_n_start, _n_end, _n_step, _N, lamb, m, meow))
                # print(uptimes_list[index])
                recoveries_list.append(
                        create_recovery_list(_n_start, _n_end, _n_step, _N, lamb, m, meow))
                print(recoveries_list[index])
                index += 1

    _ns = []
    for n in range(_n_start, _n_end + 1, _n_step):
        _ns.append(n)

    # if len(_meows) > 1:
    #     if args.mode == 'uptime':
    #         labels = ['μ = 1 1/hours', 'μ = 10 1/hours', 'μ = 100 1/hours', 'μ = 1000 1/hours']
    #     else:
    #         labels = ['μ = 1 1/hours', 'μ = 2 1/hours', 'μ = 4 1/hours', 'μ = 6 1/hours']
    # elif len(_lamb) > 1:
    #     labels = ['λ = 10^-5 1/hours', 'λ = 10^-6 1/hours', 'λ = 10^-7 1/hours', 'λ = 10^-8 1/hours', 'λ = 10^-9 1/hours']
    # else:
    #     labels = ['m = 1', 'm = 2', 'm = 3', 'm = 4']

    # if args.mode == 'uptime':
    #     pt.plot_data(_ns, uptimes_list, labels, args.xlabel, args.ylabel, args.scale, args.gtitle)
    # else:
    #     pt.plot_data(_ns, recoveries_list, labels, args.xlabel, args.ylabel, args.scale, args.gtitle)

    with open(args.output1, 'w') as ofile:
        ofile.write(json.dumps(uptimes_list))

    with open(args.output2, 'w') as ofile:
        ofile.write(json.dumps(recoveries_list))

    stop_event.set()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()