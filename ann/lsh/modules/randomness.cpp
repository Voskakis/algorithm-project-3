#include "randomness.h"
std::mt19937 gen(42);

double normal_distribution_generator(){
        //static std::mt19937 gen(seed);          // seeded once per execution
        static std::normal_distribution<double> d(0.0, 1.0);

        return std::round(d(gen));
    }

double uniform_distribution_generator(int w){
    //static std::mt19937 gen(seed);          // seeded once per execution
    uniform_real_distribution<float> d(0.0, (float) w);

    return std::round(d(gen));
}