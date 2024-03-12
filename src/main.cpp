#include <cstring>

#include <cmath>
#include <iostream>
#include <string>

struct Data {
    int N_ = 0;
    int n_ = 0;
    double lam_ = 0.0;
    double mu_ = 0.0;
    int m_ = 0;
    int t_ = 0;
};
    int c_R_star_opt = 0;
    int c_U_star_opt = 0;
    int c_S_opt = 0;

    int c_N_opt = 0;
    int c_n_opt = 0;
    double c_lam_opt = 0.0;
    double c_mu_opt = 0.0;
    int c_m_opt = 0;
    int c_t_opt = -1;

const double eps = 1E-3;

static double R_star(const Data &data);
static double U_star(const Data &data);
static double S(const Data &data);

static double P1(int i, const Data &data);

static double pi(int r, int i, const Data &data);
static double u(int l, int i, const Data &data);

static double fact(int value);
static int dt(int x);

int main(int argc, char **argv) {
    for (int i = 1 ; i < argc ; i++){
        if (strcmp("-R", argv[i]) == 0 ){//оперативной надежности
            c_R_star_opt = 1;
        }else if (strcmp("-U", argv[i]) == 0 ){//оперативной восстановимости
            c_U_star_opt = 1;
        }else if (strcmp("-S", argv[i]) == 0 ){//коэффициент готовности
            c_S_opt = 1;
        }else if (strcmp("-N", argv[i]) == 0 ){//всего ЭМ
            c_N_opt = atoi(argv[i+1]);
        }else if (strcmp("-n", argv[i]) == 0 ){//основная подсистема
            c_n_opt = atoi(argv[i+1]);
        }else if (strcmp("-lam", argv[i]) == 0 ){//интенсивность потока отказов любой из N элементарных машин ([λ] = 1/ч)
            c_lam_opt = atof(argv[i+1]);
        }else if (strcmp("-mu", argv[i]) == 0 ){//интенсивность потока восстановления элементарных машин одним восстанавливающим устройством ([µ] = 1/ч)
            c_mu_opt = atof(argv[i+1]);
        }else if (strcmp("-m", argv[i]) == 0 ){//кол-во востанавливающих устройств
            c_m_opt = atoi(argv[i+1]);
        }else if (strcmp("-t", argv[i]) == 0 ){//кол-во востанавливающих устройств
            c_t_opt = atoi(argv[i+1]);
        };
    };
    if(c_R_star_opt == 0 &&  c_U_star_opt == 0 &&  c_S_opt == 0){
        std::cout << "Выберите -R или -U или -S\n";
    }else if(c_N_opt == 0){
        std::cout << "Заполните -N\n";
    }else if(c_n_opt == 0){
        std::cout << "Заполните -n\n";
    }else if(c_lam_opt == 0){
        std::cout << "Заполните -lam\n";
    }else if(c_mu_opt == 0){
        std::cout << "Заполните -mu\n";
    }else if(c_m_opt == 0){
        std::cout << "Заполните -m\n";
    }else if(c_t_opt == 0){
        std::cout << "Заполните -t\n";
    };


    const Data data = {c_N_opt, c_n_opt, c_lam_opt, c_mu_opt, c_m_opt, c_t_opt};

    if (c_R_star_opt > 0) {
        std::cout << R_star(data)<<"\n";
    } else if (c_U_star_opt > 0) {
        std::cout << U_star(data)<<"\n";
    }else if (c_S_opt > 0) {
        std::cout << S(data)<<"\n";
    };

    return 0;
}

static double R_star(const Data &data) {
    auto Q = [&data](int i) -> double {
        double result = 0;
        double prev_result = -1;
        for (int l = 0; result - prev_result >= eps; l++) {
            prev_result = result;

            double pi_sum = 0;
            for (int r = 0; r <= i - data.n_ + l; r++) {
                pi_sum += pi(r, i, data);
            }

            result += u(l, i, data) * pi_sum;
        }

        return result;
    };

    double result = 0;

    double (*P)(int, const Data &) = P1;
    // if (data.m_ == 1) {
    //     P = P1;
    // }

    for (int i = data.n_; i <= data.N_; i++) {
        result += P(i, data) * Q(i);
    }

    return result > 1 ? 1 : result;
}

static double U_star(const Data &data) {
    auto Q = [&data](int i) -> double {
        double result = 0;
        double prev_result = -1;
        for (int r = 0; result - prev_result >= eps; r++) {
            prev_result = result;

            double u_sum = 0;
            for (int l = 0; l <= data.n_ - 1 - i + r; l++) {
                u_sum += u(l, i, data);
            }

            result += pi(r, i, data) * u_sum;
        }

        return result;
    };

    double result = 1;

    double (*P)(int, const Data &) = P1;
    // if (data.m_ == 1) {
    //     P = P1;
    // }

    for (int i = 0; i <= data.n_ - 1; i++) {
        result -= P(i, data) * Q(i);
    }

    return result;
}

static double S(const Data &data) {
    if (data.m_ == data.N_) {
        const int power = data.N_ - data.n_ + 1;
        return 1 -
            std::pow(data.lam_, power) / std::pow(data.lam_ + data.mu_, power);
    }

    double result = 0;

    double (*P)(int, const Data &) = P1;
    // if (data.m_ == 1) {
    //     P = P1;
    // }

    for (int i = data.n_; i <= data.N_; i++) {
        result += P(i, data);
    }

    return result;
}

static double P1(int i, const Data &data) {
    const double mu_lam = data.mu_ / data.lam_;
    double P = std::pow(mu_lam, i) * (1 / fact(i));

    double sum = 0;
    for (int l = 0; l <= data.N_; l++) {
        sum += std::pow(mu_lam, l) * (1 / fact(l));
    }

    P *= 1 / sum;

    return P;
}

static double pi(int r, int i, const Data &data) {
    const double i_lam_t = i * data.lam_ * data.t_;
    return (std::pow(i_lam_t, r) / fact(r)) * std::exp(-i_lam_t);
}
// +
static double u(int l, int i, const Data &data) {
    return (std::pow(data.mu_ * data.t_, l) / fact(l)) *
        (dt(data.N_ - i - data.m_) * std::pow(data.m_, l) *
             std::exp(-data.m_ * data.mu_ * data.t_) +
         dt(data.m_ - data.N_ + i) * std::pow(data.N_ - i, l) *
             std::exp(-(data.N_ - i) * data.mu_ * data.t_));
}
// +
static double fact(int value) {
    if (value == 0 || value == 1) {
        return 1;
    }
    const double pi = 3.141592653589793;
    return std::sqrt(2 * pi * value) * std::pow(value / std::exp(1), value);
}
// +
static int dt(int x) {
    return x >= 0 ? 1 : 0;
}