// modules/lsh_interface.cpp
#include "lsh_interface.h"
#include "UserInputHandling.h"
#include "CosineHashing.h"
#include "EuclidianHashing.h"

#include <iostream>

using namespace std;

// These come from globals.cpp
extern ifstream inFile;
extern ifstream qFile;
extern ofstream outFile;
extern int k;
extern int L;
extern bool metric;

void lsh_set_files(const std::string& input_path,
                   const std::string& query_path,
                   const std::string& output_path)
{
    if (inFile.is_open()) inFile.close();
    if (qFile.is_open()) qFile.close();
    if (outFile.is_open()) outFile.close();

    inFile.open(input_path);
    qFile.open(query_path);
    outFile.open(output_path);

    if (!inFile.is_open()) {
        throw std::runtime_error("Failed to open input file: " + input_path);
    }
    if (!qFile.is_open()) {
        throw std::runtime_error("Failed to open query file: " + query_path);
    }
    if (!outFile.is_open()) {
        throw std::runtime_error("Failed to open output file: " + output_path);
    }
}

void lsh_set_parameters(int k_val, int L_val, bool metric_val)
{
    k = k_val;
    L = L_val;
    metric = metric_val;
}

void lsh_build()
{
    // This basically replicates the "build index" part of main()
    long long unsigned int lines = get_number_of_lines();

    if (metric == 0) {

        HashTable_Euclidian_Initialization(L);
        HashFunctions_Euclidian_Initialization(k, L);
        Euclidian_Hash_Tables_Finalization(L);

        for (int i = 0; i < (int)lines; ++i) {
            Euclidian_Hash_from_file(i, L, k);
        }
    } else {

        HashTable_Cosine_Initialization(L, k);
        HashFunctions_Cosine_Initialization(L, k);

        for (int i = 0; i < (int)lines; ++i) {
            Cosine_Hash_from_file(i, L, k);
        }

        Hash_Tables_Finalization(L, k);
    }
}

void lsh_run_all_queries()
{
    if (metric == 0) {
        Euclidian_LSH_File(L, k, N);   // This will use qFile and outFile
    } else {
        Cosine_LSH_File(L, k);
    }
}

void lsh_close_files()
{
    if (inFile.is_open()) inFile.close();
    if (qFile.is_open()) qFile.close();
    if (outFile.is_open()) outFile.close();
}
