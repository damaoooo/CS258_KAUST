#include <iostream>

#include <math.h>
#include <sys/time.h>
#include <stdlib.h>


using namespace std;

int64_t get_time_ms()
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

double random_number(){
    return (double)rand() / 2147483647;
}

int possion(int mean) {
    int k = 0;
    double p = 1.0;
    double l = exp(-mean);
    do {
        k++;
        p *= random_number();
    } while (p > l);
    return k - 1;
}

int main(){
    
    cout << "Please input how many numbers you want to generate(int):";
    int n = 1000;
    cin >> n;
    int mean = 0;
    cout << "Please input the mean of the possion distribution(int):";
    cin >> mean;
    for(int i = 0; i < n; i++)
        srand(get_time_ms());
        cout << possion(mean) << ",";
}