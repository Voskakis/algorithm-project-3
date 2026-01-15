#include "modules/CosineHashing.h"
#include "modules/EuclidianHashing.h"
#include "modules/UserInputHandling.h"

using namespace std;

int main(int argc, char* argv[]) {
    int input = user_input_handling(argc, argv);
    if (input == -1) {
        cout << "The program will now exit." << endl;
        return -1;
    }

    if (input != 1) {
        Euclidian_LSH_File_With_Prints(L, k, N);
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
            Euclidian_LSH_File(L, k, N);
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
		
        
    }

    inFile.close();
    qFile.close();
    outFile.close();

    return 0;
}
