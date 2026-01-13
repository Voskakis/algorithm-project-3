#include <fstream>

std::ifstream inFile;  /* Input File */
std::ifstream qFile;   /* Query File */
std::ofstream outFile; /* Output File */

int k = 4;             /* Number of LSH Functions */
int L = 5;             /* Number of Hash Tables  */
bool metric = 0;
int M = 5;          /* Max number of points to be checked */
int N = 5;