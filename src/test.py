import sys
import math

class Data:
    def __init__(self):
        self.N_ = 0
        self.n_ = 0
        self.lam_ = 0.0
        self.mu_ = 0.0
        self.m_ = 0
        self.t_ = 0

c_R_star_opt = 0
c_U_star_opt = 0
c_S_opt = 0

c_N_opt = 0
c_n_opt = 0
c_lam_opt = 0.0
c_mu_opt = 0.0
c_m_opt = 0
c_t_opt = -1

eps = 1E-3

def R_star(data):
    def Q(i):
        result = 0
        prev_result = -1
        while result - prev_result >= eps:
            prev_result = result
            pi_sum = 0
            for r in range(i - data.n_ + l + 1):
                pi_sum += pi(r, i, data)
            result += u(l, i, data) * pi_sum
        return result

    result = 0
    P = P1
    for i in range(data.n_, data.N_ + 1):
        result += P(i, data) * Q(i)

    return min(result, 1)

def U_star(data):
    def Q(i):
        result = 0
        prev_result = -1
        while result - prev_result >= eps:
            prev_result = result
            u_sum = 0
            for l in range(data.n_ - 1 - i + r + 1):
                u_sum += u(l, i, data)
            result += pi(r, i, data) * u_sum
        return result

    result = 1
    P = P1
    for i in range(data.n_):
        result -= P(i, data) * Q(i)

    return result

def S(data):
    if data.m_ == data.N_:
        power = data.N_ - data.n_ + 1
        return 1 - math.pow(data.lam_, power) / math.pow(data.lam_ + data.mu_, power)

    result = 0
    P = P1
    for i in range(data.n_, data.N_ + 1):
        result += P(i, data)

    return result

def P1(i, data):
    mu_lam = data.mu_ / data.lam_
    P = math.pow(mu_lam, i) * (1 / fact(i))

    sum_val = 0
    for l in range(data.N_ + 1):
        sum_val += math.pow(mu_lam, l) * (1 / fact(l))

    P *= 1 / sum_val
    return P

def pi(r, i, data):
    i_lam_t = i * data.lam_ * data.t_
    return (math.pow(i_lam_t, r) / fact(r)) * math.exp(-i_lam_t)

def u(l, i, data):
    return (math.pow(data.mu_ * data.t_, l) / fact(l)) * (dt(data.N_ - i - data.m_) * math.pow(data.m_, l) * math.exp(-data.m_ * data.mu_ * data.t_) + dt(data.m_ - data.N_ + i) * math.pow(data.N_ - i, l) * math.exp(-(data.N_ - i) * data.mu_ * data.t_))

def fact(value):
    if value == 0 or value == 1:
        return 1
    pi_val = 3.141592653589793
    return math.sqrt(2 * pi_val * value) * math.pow(value / math.exp(1), value)

def dt(x):
    return 1 if x >= 0 else 0

def main():
    global c_R_star_opt, c_U_star_opt, c_S_opt, c_N_opt, c_n_opt, c_lam_opt, c_mu_opt, c_m_opt, c_t_opt

    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-R":
            c_R_star_opt = 1
        elif sys.argv[i] == "-U":
            c_U_star_opt = 1
        elif sys.argv[i] == "-S":
            c_S_opt = 1
        elif sys.argv[i] == "-N":
            c_N_opt = int(sys.argv[i + 1])
        elif sys.argv[i] == "-n":
            c_n_opt = int(sys.argv[i + 1])
        elif sys.argv[i] == "-lam":
            c_lam_opt = float(sys.argv[i + 1])
        elif sys.argv[i] == "-mu":
            c_mu_opt = float(sys.argv[i + 1])
        elif sys.argv[i] == "-m":
            c_m_opt = int(sys.argv[i + 1])
        elif sys.argv[i] == "-t":
            c_t_opt = int(sys.argv[i + 1])

    if c_R_star_opt == 0 and c_U_star_opt == 0 and c_S_opt == 0:
        print("Выберите -R или -U или -S")
    elif c_N_opt == 0:
        print("Заполните -N")
    elif c_n_opt == 0:
        print("Заполните -n")
    elif c_lam_opt == 0:
        print("Заполните -lam")
    elif c_mu_opt == 0:
        print("Заполните -mu")
    elif c_m_opt == 0:
        print("Заполните -m")
    elif c_t_opt == -1:
        print("Заполните -t")

    data = Data()
    data.N_ = c_N_opt
    data.n_ = c_n_opt
    data.lam_ = c_lam_opt
    data.mu_ = c_mu_opt
    data.m_ = c_m_opt
    data.t_ = c_t_opt

    if c_R_star_opt > 0:
        print(R_star(data))
    elif c_U_star_opt > 0:
        print(U_star(data))
    elif c_S_opt > 0:
        print(S(data))

if __name__ == "__main__":
    main()
