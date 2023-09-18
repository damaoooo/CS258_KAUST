#include <iostream>
#include <vector>
#include <algorithm>

#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <sys/time.h>

#define MAX_LEN 10000
#define FORESEE_DIGITS 1
#define BIGGEST 0x7FFFFFFF

using namespace std;

namespace RandomGenerator
{
    class BigInt
    {
    public:
        vector<uint> num;

        BigInt();
        BigInt(const char *s);
        BigInt(string &s);
        BigInt(unsigned int s);

        bool CheckValidStr(string &s);
        bool IsDigit(char c);

        string to_string_value();

        bool operator>(const BigInt &num2) const;
        bool operator>=(const BigInt &num2) const;
        bool operator==(const BigInt &num2) const;
        bool operator<=(const BigInt &num2) const;
        bool operator<(const BigInt &num2) const;
        bool operator!=(const BigInt &num2) const;

        BigInt operator/(const BigInt &num2) const;
        BigInt operator%(const BigInt &num2) const;
        BigInt operator*(const BigInt &num2) const;
        BigInt operator+(const BigInt &num2) const;
        BigInt operator-(const BigInt &num2) const;

        int compare(const BigInt &num2) const;

        BigInt to_binary();
        BigInt to_demical();

        unsigned long long to_ullong() const;
        unsigned int to_uint() const;
    };

    BigInt::BigInt(void)
    {
        num.clear();
    }

    BigInt::BigInt(string &s)
    {
        if (!CheckValidStr(s))
        {
            throw "The input is not a correct number";
        }

        for (auto c = s.begin(); c != s.end(); c++)
        {
            num.push_back(*c - '0');
        }

        while (num[0] == 0 && num.size() > 1)
        {
            num.erase(num.begin());
        }
    }

    BigInt::BigInt(const char *s)
    {
        string temp(s);
        if (!CheckValidStr(temp))
        {
            throw "The input is not a correct number";
        }

        for (auto c = temp.begin(); c != temp.end(); c++)
        {
            num.push_back(*c - '0');
        }

        while (num[0] == 0 && num.size() > 1)
        {
            num.erase(num.begin());
        }
    }

    BigInt::BigInt(unsigned int s)
    {
        string temp = std::to_string(s);
        if (!CheckValidStr(temp))
        {
            throw "The input is not a correct number";
        }

        for (auto c = temp.begin(); c != temp.end(); c++)
        {
            num.push_back(*c - '0');
        }
    }

    unsigned long long BigInt::to_ullong() const
    {
        unsigned long long result = 0;
        for (auto c = this->num.begin(); c != this->num.end(); c++)
        {
            result = result * 10 + *c;
        }
        return result;
    }

    unsigned int BigInt::to_uint() const
    {
        unsigned int result = 0;
        for (auto c = this->num.begin(); c != this->num.end(); c++)
        {
            result = result * 10 + *c;
        }
        return result;
    }

    bool BigInt::IsDigit(char c)
    {
        return ('0' <= c && c <= '9');
    }

    bool BigInt::CheckValidStr(string &s)
    {
        for (auto c = s.begin(); c != s.end(); c++)
        {
            if (!IsDigit(*c))
            {
                return false;
            }
        }
        return true;
    }

    string BigInt::to_string_value()
    {
        string result;

        if (this->num.size() == 0)
            return "0";

        for (auto c = 0; c != this->num.size(); c++)
        {
            result += (char)('0' + this->num[c]);
        }
        return result;
    }

    int BigInt::compare(const BigInt &num2) const
    {
        if (this->num.size() != num2.num.size())
        {
            if (this->num.size() > num2.num.size())
                return 1;
            else
                return -1;
        }

        for (int index = 0; index != num.size(); index++)
        {
            if (num[index] > num2.num[index])
                return 1;
            else if (num[index] < num2.num[index])
                return -1;
        }
        return 0;
    }

    BigInt BigInt::operator+(const BigInt &num2) const
    {
        BigInt result;
        int carry = 0;
        int index1 = num.size() - 1;
        int index2 = num2.num.size() - 1;

        while (index1 >= 0 && index2 >= 0)
        {
            int temp = num[index1] + num2.num[index2] + carry;
            result.num.insert(result.num.begin(), temp % 10);
            carry = temp / 10;
            index1--;
            index2--;
        }

        while (index1 >= 0)
        {
            int temp = num[index1] + carry;
            result.num.insert(result.num.begin(), temp % 10);
            carry = temp / 10;
            index1--;
        }

        while (index2 >= 0)
        {
            int temp = num2.num[index2] + carry;
            result.num.insert(result.num.begin(), temp % 10);
            carry = temp / 10;
            index2--;
        }

        if (carry != 0)
        {
            result.num.insert(result.num.begin(), carry);
        }

        return result;
    }

    BigInt BigInt::operator-(const BigInt &num2) const
    {
        BigInt result;
        int carry = 0;
        int index1 = num.size() - 1;
        int index2 = num2.num.size() - 1;

        while (index1 >= 0 && index2 >= 0)
        {
            int temp = num[index1] - num2.num[index2] - carry;
            if (temp < 0)
            {
                temp += 10;
                carry = 1;
            }
            else
            {
                carry = 0;
            }
            result.num.insert(result.num.begin(), temp);
            index1--;
            index2--;
        }

        while (index1 >= 0)
        {
            int temp = num[index1] - carry;
            if (temp < 0)
            {
                temp += 10;
                carry = 1;
            }
            else
            {
                carry = 0;
            }
            result.num.insert(result.num.begin(), temp);
            index1--;
        }

        while (index2 >= 0)
        {
            int temp = num2.num[index2] - carry;
            if (temp < 0)
            {
                temp += 10;
                carry = 1;
            }
            else
            {
                carry = 0;
            }
            result.num.insert(result.num.begin(), temp);
            index2--;
        }

        if (carry != 0)
        {
            result.num.insert(result.num.begin(), carry);
        }

        while (result.num[0] == 0 && result.num.size() > 1)
        {
            result.num.erase(result.num.begin());
        }

        return result;
    }

    BigInt BigInt::operator*(const BigInt &num2) const
    {
        BigInt result;
        int carry = 0;
        int index1 = num.size() - 1;
        int index2 = num2.num.size() - 1;

        while (index2 >= 0)
        {
            BigInt temp;
            for (int i = 0; i < num2.num.size() - 1 - index2; i++)
            {
                temp.num.push_back(0);
            }

            for (int i = index1; i >= 0; i--)
            {
                int temp_num = num[i] * num2.num[index2] + carry;
                temp.num.insert(temp.num.begin(), temp_num % 10);
                carry = temp_num / 10;
            }

            if (carry != 0)
            {
                temp.num.insert(temp.num.begin(), carry);
                carry = 0;
            }

            result = result + temp;
            index2--;
        }

        return result;
    }

    BigInt BigInt::to_binary()
    {
        BigInt result;
        BigInt temp = *this;
        int carry = 0;
        BigInt new_temp;
        while (temp != BigInt("0"))
        {
            carry = 0;
            for (int index = 0; index < temp.num.size(); index++)
            {
                int temp_num = temp.num[index] + carry * 10;
                new_temp.num.push_back(temp_num / 2);
                carry = temp_num % 2;
            }
            result.num.push_back(temp.num[temp.num.size() - 1] % 2);
            temp = new_temp;
            while (temp.num[0] == 0 && temp.num.size() > 1)
            {
                temp.num.erase(temp.num.begin());
            }
            new_temp.num.clear();
        }
        reverse(result.num.begin(), result.num.end());
        return result;
    }

    BigInt BigInt::to_demical()
    {
        BigInt result;
        BigInt temp = *this;
        reverse(temp.num.begin(), temp.num.end());

        for (int index = 0; index < temp.num.size(); index++)
        {
            BigInt temp_num;
            temp_num.num.push_back(temp.num[index]);
            for (int i = 0; i < index; i++)
            {
                temp_num = temp_num * BigInt("2");
            }
            result = result + temp_num;
        }
        return result;
    }

    bool BigInt::operator>(const BigInt &num2) const
    {
        return compare(num2) > 0;
    }

    bool BigInt::operator>=(const BigInt &num2) const
    {
        return compare(num2) >= 0;
    }

    bool BigInt::operator==(const BigInt &num2) const
    {
        return compare(num2) == 0;
    }

    bool BigInt::operator<=(const BigInt &num2) const
    {
        return compare(num2) <= 0;
    }

    bool BigInt::operator<(const BigInt &num2) const
    {
        return compare(num2) < 0;
    }

    bool BigInt::operator!=(const BigInt &num2) const
    {
        return compare(num2) != 0;
    }

}

unsigned int uniform_random(int n)
{
    unsigned int random_number = random();
    double ratio = ((double)random_number / BIGGEST);
    unsigned int result = (unsigned int)(n * ratio);
    // cout << "Random Number: " << result << endl;
    return result;
}

RandomGenerator::BigInt get_big_random(RandomGenerator::BigInt n)
{
    RandomGenerator::BigInt binary = n.to_binary();
    int blocks = binary.num.size() / 31;
    RandomGenerator::BigInt result;
    for (int i = 0; i < blocks; i++)
    {
        // 截取block指定的31位数，转化为十进制
        RandomGenerator::BigInt bigIntBlock;
        bigIntBlock.num = vector<uint>(binary.num.begin() + i * 31, binary.num.begin() + (i + 1) * 31);
        bigIntBlock = bigIntBlock.to_demical();

        // 生成随机数
        unsigned int random_number = uniform_random(bigIntBlock.to_uint());
        bigIntBlock = RandomGenerator::BigInt(random_number);

        // Insert 0 until 31 bits
        while (bigIntBlock.num.size() < 31)
        {
            bigIntBlock.num.insert(bigIntBlock.num.begin(), 0);
        }
        result.num.insert(result.num.end(), bigIntBlock.num.begin(), bigIntBlock.num.end());
    }
    RandomGenerator::BigInt remainBlock;
    remainBlock.num = vector<uint>(binary.num.begin() + blocks * 31, binary.num.end());
    remainBlock = remainBlock.to_demical();
    unsigned int random_number = uniform_random(remainBlock.to_uint());
    remainBlock = RandomGenerator::BigInt(random_number);
    while (remainBlock.num.size() < 31)
    {
        remainBlock.num.insert(remainBlock.num.begin(), 0);
    }
    result.num.insert(result.num.end(), remainBlock.num.begin(), remainBlock.num.end());
    result = result.to_demical();
    return result;
}

int64_t get_time_ms()
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

int main()
{
    srand((unsigned int)time(NULL));
    unsigned int biggest = -1;

    cout << "Input the N value (N is a positive integer):" << endl;
    // string n = "114514191981089311451419198108931145141919810893";
    string n;
    cin >> n;

    RandomGenerator::BigInt bigInt;
    try
    {
        RandomGenerator::BigInt temp(n);
        bigInt = temp;
    }
    catch (const char *msg)
    {
        cerr << msg << endl;
    }
    RandomGenerator::BigInt biggestLong(biggest);

    if (bigInt > biggestLong)
    {
        cout << "Will use big number algorithm" << endl;
        RandomGenerator::BigInt result = get_big_random(bigInt);
        cout << "Random Number: " << result.to_string_value() << endl;
    }
    else
    {
        cout << "Will use small number algorithm" << endl;
        unsigned long n = stoul(bigInt.to_string_value(), NULL, 10);
        cout << n << endl;

        unsigned int result = uniform_random(n);
        cout << "Random Number: " << result << endl;
    }
    return 0;
}