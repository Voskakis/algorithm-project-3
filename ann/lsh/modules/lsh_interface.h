// modules/lsh_interface.h
#pragma once
#include <string>

void lsh_set_files(const std::string& input_path,
                   const std::string& query_path,
                   const std::string& output_path);

void lsh_set_parameters(int k_val, int L_val, bool metric_val);

void lsh_build();          // Build hash tables + hash all input vectors
void lsh_run_all_queries(); // Run LSH for all queries (writes to outFile)

void lsh_close_files();
