#include "modules/CosineHashing.h"
#include "modules/EuclidianHashing.h"
#include "modules/UserInputHandling.h"

using namespace std;

ifstream inFile;
ifstream qFile;
ofstream outFile;

int k = 4;  // number of LSH functions
int L = 5;  // number of hash tables
int N = 5;  // number of nearest neighbors
bool metric = 0;

int main(int argc, char* argv[]) {
    int input = user_input_handling(argc, argv);
    if (input == -1) {
        cout << "The program will now exit." << endl;
        return -1;
    }

    if (input != 1) {
        size_t d1;
        if (!(inFile >> d1))
            throw std::runtime_error("Failed to read outer dimension");

        Euclidian_Hash_Tables.resize(d1);

        for (size_t i = 0; i < d1; ++i) {
            size_t d2;
            if (!(inFile >> d2))
                throw std::runtime_error("Failed to read middle dimension");

            Euclidian_Hash_Tables[i].resize(d2);

            for (size_t j = 0; j < d2; ++j) {
                size_t d3;
                if (!(inFile >> d3))
                    throw std::runtime_error("Failed to read inner dimension");

                Euclidian_Hash_Tables[i][j].resize(d3);

                for (size_t k = 0; k < d3; ++k) {
                    if (!(inFile >> Euclidian_Hash_Tables[i][j][k]))
                        throw std::runtime_error("Failed to read value");
                }
            }
        }
        Euclidian_LSH_File(L, k, N);
    } else {
        long long unsigned int lines = get_number_of_lines();

        // ========================
        //   EUCLIDEAN LSH
        // ========================
        if (metric == 0) {
            HashTable_Euclidian_Initialization(L);
            HashFunctions_Euclidian_Initialization(k, L);

            // FIRST insert all dataset vectors
            for (int i = 0; i < lines; i++)
                Euclidian_Hash_from_file(i, L, k);

            // THEN finalize cleanup (removes zeros)
            Euclidian_Hash_Tables_Finalization(L);
        }

        // ========================
        //   COSINE LSH
        // ========================
        if (metric == 1) {
            HashTable_Cosine_Initialization(L, k);
            HashFunctions_Cosine_Initialization(L, k);

            for (int i = 0; i < lines; i++)
                Cosine_Hash_from_file(i, L, k);

            Hash_Tables_Finalization(L, k);

            // FIX: pass N
            Cosine_LSH_File(L, k);
        }

        outFile << Euclidian_Hash_Tables.size() << '\n';
        for (const auto& v2 : Euclidian_Hash_Tables) {
            outFile << v2.size() << '\n';
            for (const auto& v3 : v2) {
                outFile << v3.size();
                for (auto value : v3)
                    outFile << ' ' << value;
                outFile << '\n';
            }
        }
    }

    inFile.close();
    qFile.close();
    outFile.close();

    return 0;
}
