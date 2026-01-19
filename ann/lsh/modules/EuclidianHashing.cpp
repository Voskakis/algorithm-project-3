#include "EuclidianHashing.h"
#define BIG_INT 4294967291

using namespace std;

void HashTable_Euclidian_Initialization(int L) {
    /* We have L hash tables with n/2 size each */

    n = get_number_of_lines();

    dim = get_dim_of_data();

    Euclidian_Hash_Tables.resize(
            L, vector<vector<long long unsigned int>>(n / 2, vector<long long unsigned int>(1000)));
}

void HashFunctions_Euclidian_Initialization(int k, int L) {
    /* First lets fill out the v vectors used for the euclidian hashing method */

    v.resize(k, vector<double>(dim));
    for (int i = 0; i < k; i++) {
        v[i].clear();

        for (int j = 0; j < dim; j++) {
            v[i].push_back(normal_distribution_generator());

            // cout << "i: " << i << " j: " << j << " is " << (double) v[i][j] << endl; /* DEBUG -
            // Printing out elements of Hash_Function */
        }
    }

    /* Now lets initialize the w which will be used */

    w = 2;

    /* Initialize Amplified_Euclidian_Functions */

    Euclidian_Amplified_Functions.resize(L, vector<int>(k));

    srand(time(0));

    int func_num;

    int j;

    for (int i = 0; i < L; i++) {
        j = 0;

        Euclidian_Amplified_Functions[i].clear();

        do {
            func_num = rand() % k;

            // cout << "func_num is: " << func_num << "i is: " << i << endl;

            if (find(Euclidian_Amplified_Functions[i].begin(),
                     Euclidian_Amplified_Functions[i].end(),
                     func_num) == Euclidian_Amplified_Functions[i].end()) {
                // cout << "i got in here with value: " << func_num << " i is: " << i << endl;
                j++;

                Euclidian_Amplified_Functions[i].push_back(func_num);
            }

        } while (j < k);
    }

    /* Last but not least, lets initialize the t of each hash function */

    t.clear();

    float random;

    random_device generator;
    uniform_real_distribution<float> distribution(0.0, (float) w);

    for (int i = 0; i < k; i++) { /* Each hash function has its own t */

        random = distribution(generator); /* Generate a new double number */

        t.push_back(random);
    }
}

void Search_Euclidian_Hash_Tables(int line, int L) {
    for (int i = 0; i < L; i++) {
        for (int j = 0; j < n / 2; j++) {
            for (auto k = Euclidian_Hash_Tables[i][j].begin();
                 k != Euclidian_Hash_Tables[i][j].end(); k++) {
                if (*k == line)
                    cout << " FOUND " << line << "IN " << i << " hashtable and in pos " << j
                         << endl;
            }
        }
    }
}

void Euclidian_Hash_from_file(int line, int L, int k) {
    /* First lets get to the line pointed */

    move_input_to_line(line);

    /* Now onto hashing! */

    string string_to_hash;

    long double sum;

    double x;

    string str;

    long long unsigned int pos;

    for (int amp_func = 0; amp_func < L;
         amp_func++) { /* We have to hash each vector with each Amplified function */

        string_to_hash = "";

        for (int h = 0; h < k; h++) { /* We have to hash each vector with each Hash Function in the
                                         amp_func Amplified Function */

            sum = 0;

            for (int i = 0; i < dim;
                 i++) { /* In order to calculate the Inner product of the hash vecor and the data
                           vector we have to multiply all of their coordinates */

                // if( i == 0 ) inFile >> str; /* First int is an id, so skip it */

                inFile >> x; /* Get the first int from the file */

                // cout << "Adding to  " << sum << " with " << x* Hash_Function[
                // Amplified_Functions[amp_func][h] ][i] << endl;

                sum = sum + x * v[Euclidian_Amplified_Functions[amp_func][h]]
                                 [i]; /* Sum is calculating the inner product of the two vectors */
            }

            sum = sum + t[h];

            sum = floor(sum / (double) w);

            move_input_to_line(line); /* Reset the line for the next hash function */

            string_to_hash.append(to_string(sum));
        }

        // pos = modulo(hash<string>{}(string_to_hash), 200000);

        pos = modulo(hash<string>{}(string_to_hash), n / 2);

        // cout << "Pushing " << line << " to [" << amp_func << "][" << pos << "]" << endl;

        Euclidian_Hash_Tables[amp_func][pos].push_back(line);
    }
}

void Store_points_in_range_euc() {
    std::ofstream outpoints("points_in_range_euc");
    outpoints << points_in_range_euc.size() << '\n';
    for (int x : points_in_range_euc)
        outpoints << x << ' ';
}

void Store_w() {
    std::ofstream outw("w");
    outw << w << '\n';
}

void Store_Euclidian_Amplified_Functions() {
    std::ofstream outeaf("eaf");
    outeaf << Euclidian_Amplified_Functions.size() << '\n';
    for (const auto& row : Euclidian_Amplified_Functions) {
        outeaf << row.size();
        for (int x : row)
            outeaf << ' ' << x;
        outeaf << '\n';
    }
}

void Store_n() {
    std::ofstream outn("n");
    outn << n << '\n';
}

void Store_dim() {
    std::ofstream outd("dim");
    outd << dim << '\n';
}

void Store_v() {
    std::ofstream outv("v");
    outv << v.size() << '\n';
    for (const auto& row : v) {
        outv << row.size();
        for (double x : row)
            outv << ' ' << x;
        outv << '\n';
    }
}

void Store_Euclidian_Hash_Tables() {
    std::ofstream outEuclidian_Hash_Tables("Euclidian_Hash_Tables");
    outEuclidian_Hash_Tables << Euclidian_Hash_Tables.size() << '\n';
    for (const auto& v2 : Euclidian_Hash_Tables) {
        outEuclidian_Hash_Tables << v2.size() << '\n';
        for (const auto& v3 : v2) {
            outEuclidian_Hash_Tables << v3.size();
            for (auto value : v3)
                outEuclidian_Hash_Tables << ' ' << value;
            outEuclidian_Hash_Tables << '\n';
        }
    }
}

void Store_Euclidian_Hash_Tables_In_Series(int file_number) {
    string fileName = "Euclidian_Hash_Tables_";
    fileName.append(to_string(file_number));
    std::ofstream outEuclidian_Hash_Tables(fileName);
    outEuclidian_Hash_Tables << Euclidian_Hash_Tables.size() << '\n';
    for (const auto& v2 : Euclidian_Hash_Tables) {
        outEuclidian_Hash_Tables << v2.size() << '\n';
        for (const auto& v3 : v2) {
            outEuclidian_Hash_Tables << v3.size();
            for (auto value : v3)
                outEuclidian_Hash_Tables << ' ' << value;
            outEuclidian_Hash_Tables << '\n';
        }
    }
}

void Store_tt() {
    std::ofstream outt("t");
    outt << t.size() << '\n';
    for (double value : t)
        outt << value << ' ';
    outt << '\n';
}

long long int calcute_euclidian_distance(int input_line, int query_line) {
    /* First lets get the vectors specified in both the input and the query file */

    get_query(query_line);

    move_input_to_line(input_line);

    // cout << "Calculating Distance Between input_line " << input_line << " and query_line " <<
    // query_line << endl;

    /* Now lets calcute the inner product of the two vectors and the norm of each one*/

    double x, y;

    long long int dist = 0;

    for (int i = 0; i < dim; i++) {
        inFile >> x;

        qFile >> y;

        dist = dist + (x - y) * (x - y);

        // cout << "x: " << x << " y: " << y << "dist: " << dist << endl;
    }

    // cout << "DIST: " << dist << endl;

    return dist;
}

void Euclidian_Hash_Tables_Finalization(int L) {
    int max = n / 2;

    for (int amp_func = 0; amp_func < L; amp_func++) {
        for (int pos = 0; pos < max; pos++) {
            Euclidian_Hash_Tables[amp_func][pos].erase(
                    remove(Euclidian_Hash_Tables[amp_func][pos].begin(),
                           Euclidian_Hash_Tables[amp_func][pos].end(), 0),
                    Euclidian_Hash_Tables[amp_func][pos].end());
        }
    }

    Euclidian_Hash_from_file(0, L, k);

    Store_Euclidian_Hash_Tables();
    Store_tt();
    Store_v();
    Store_n();
    Store_dim();
    Store_Euclidian_Amplified_Functions();
    Store_w();
    Store_points_in_range_euc();
}

long long unsigned int euclidian_hash_query(int query_line, int amp_func, int k) {
    get_query(query_line);

    string string_to_hash;

    long double sum;

    double x;

    long long unsigned int pos;

    string_to_hash = "";

    for (int h = 0; h < k; h++) { /* We have to hash each vector with each Hash Function in the
                                     amp_func Amplified Function */

        sum = 0;

        for (int i = 0; i < dim;
             i++) { /* In order to calculate the Inner product of the hash vecor and the data vector
                       we have to multiply all of their coordinates */

            // if( i == 0 ) inFile >> x; /* First int is an id, so skip it */

            qFile >> x; /* Get the first int from the file */

            // cout << "Adding to  " << sum << " with " << x* Hash_Function[
            // Amplified_Functions[amp_func][h] ][i] << endl;

            sum = sum + x * v[Euclidian_Amplified_Functions[amp_func][h]]
                             [i]; /* Sum is calculating the inner product of the two vectors */
        }

        sum = sum + t[h];

        sum = floor(sum / (double) w);
        sum = floor(sum);

        get_query(query_line); /* Reset the line for the next hash function */

        string_to_hash = string_to_hash + to_string(sum);
    }

    pos = modulo(hash<string>{}(string_to_hash), BIG_INT);

    pos = modulo(pos, n / 2);

    // cout << "Pushing " << line << " to [" << amp_func << "][" << pos << "]" << endl;

    return pos;
}

void Euclidian_Full_Search_NN(int query_line, int N) {
    get_query(query_line);

    std::vector<std::pair<long long unsigned int, long long unsigned int>> best_true;
    // (dist, line)

    auto update_best = [&](long long unsigned int line_idx, long long unsigned int dist) {
        if (best_true.size() < static_cast<size_t>(N)) {
            best_true.emplace_back(dist, line_idx);
            std::sort(best_true.begin(), best_true.end(), [](const auto& a, const auto& b) {
                return a.first < b.first;  // sort by distance
            });
        } else if (dist < best_true.back().first) {
            best_true.emplace_back(dist, line_idx);
            std::sort(best_true.begin(), best_true.end(),
                      [](const auto& a, const auto& b) { return a.first < b.first; });
            best_true.resize(N);
        }
    };

    for (long long unsigned int i = 0; i < n; i++) {
        long long unsigned int dist = calcute_euclidian_distance(i, query_line);
        update_best(i, dist);
    }

    for (size_t rank = 0; rank < best_true.size(); ++rank) {
        std::cout << best_true[rank].second;
        if (rank + 1 < best_true.size())
            std::cout << " ";
    }
    std::cout << "\n";
}

void Euclidian_Full_Search_Range(int query_line, double radius) {
    /* Brute Force Range Search using Euclidian metric */

    get_query(query_line);

    std::cout << "R-Near Neighbours:" << endl;

    long long unsigned int dist;

    for (long long unsigned int i = 0; i < n; i++) {
        dist = calcute_euclidian_distance(i, query_line);

        if (dist < radius) {
            std::cout << "Item " << i << endl;
        }
    }
}

void Nearest_Query_Euclidian(int query_line, int L, int k, int N) {
    int amp_func, pos_in_hash_table;
    long long unsigned int dist;
    short int time_to_break = 3 * L;

    std::vector<std::pair<long long unsigned int, long long unsigned int>> best_lsh;
    // (dist, line)

    auto update_best = [&](long long unsigned int line_idx, long long unsigned int d) {
        // 1. Skip if this line_idx is already in best_lsh (avoid duplicates)
        for (const auto& p : best_lsh) {
            if (p.second == line_idx)
                return;  // already present, do nothing
        }

        // 2. Normal top-N logic
        if (best_lsh.size() < static_cast<size_t>(N)) {
            best_lsh.emplace_back(d, line_idx);
            std::sort(best_lsh.begin(), best_lsh.end(), [](const auto& a, const auto& b) {
                return a.first < b.first;  // sort by distance
            });
        } else if (d < best_lsh.back().first) {
            best_lsh.emplace_back(d, line_idx);
            std::sort(best_lsh.begin(), best_lsh.end(),
                      [](const auto& a, const auto& b) { return a.first < b.first; });
            best_lsh.resize(N);
        }
    };

    auto start1 = std::chrono::high_resolution_clock::now();

    for (amp_func = 0; amp_func < L; amp_func++) {
        pos_in_hash_table = euclidian_hash_query(query_line, amp_func, k);
        int widen = 0;
        int max = Euclidian_Hash_Tables[amp_func].size()-1;
        while (best_lsh.size() < N && widen < 25) {
            if (pos_in_hash_table + widen < max) {
                for (auto i = Euclidian_Hash_Tables[amp_func][pos_in_hash_table+widen].begin();
                     i != Euclidian_Hash_Tables[amp_func][pos_in_hash_table+widen].end(); ++i) {
                    dist = calcute_euclidian_distance(*i, query_line);

                    update_best(*i, dist);
                     }
            }
            if (widen==0 && pos_in_hash_table - widen > -1) {
                for (auto i = Euclidian_Hash_Tables[amp_func][pos_in_hash_table-widen].begin();
                 i != Euclidian_Hash_Tables[amp_func][pos_in_hash_table-widen].end(); ++i) {
                    dist = calcute_euclidian_distance(*i, query_line);

                    update_best(*i, dist);
                 }
            }
            widen++;
        }
    }

    if (best_lsh.empty()) {
        for (long long unsigned int i = 0; i < n; ++i) {
            long long unsigned int d = calcute_euclidian_distance(i, query_line);
            update_best(i, d);  // reuse same top-N logic
        }
    }

    auto finish1 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed1 = finish1 - start1;

    for (size_t rank = 0; rank < best_lsh.size(); ++rank) {
        std::cout << best_lsh[rank].second;
        if (rank + 1 < best_lsh.size())
            std::cout << " ";
    }
    std::cout << "\n";
    // auto start2 = std::chrono::high_resolution_clock::now();

    // Euclidian_Full_Search_NN(query_line, N);

    // auto finish2 = std::chrono::high_resolution_clock::now();
    // std::chrono::duration<double> elapsed2 = finish2 - start2;

    // outFile << "tLSH: " << elapsed1.count() << endl;
    // outFile << "tTrue: " << elapsed2.count() << endl;
    // outFile << "==================================================== " << endl;
}

void Range_Search_Euclidian(int query_line, double range, int L, int k) {
    /* Given a query line, performs LSH range search */

    short int already_in;

    int amp_func, pos_in_hash_table;

    long long unsigned int dist;

    auto start1 = std::chrono::high_resolution_clock::now();

    for (amp_func = 0; amp_func < L;
         amp_func++) { /* We have to look in each hash table for the query vector */

        pos_in_hash_table = euclidian_hash_query(query_line, amp_func, k);

        // cout << "pos in hash table: " << pos_in_hash_table << " amp_func: " << amp_func << " k: "
        // << k << " query_line: " << query_line << " range: " << range << endl;

        for (auto i = Euclidian_Hash_Tables[amp_func][pos_in_hash_table].begin();
             i != Euclidian_Hash_Tables[amp_func][pos_in_hash_table].end(); ++i) {
            dist = calcute_euclidian_distance(
                    *i, query_line); /* Calculate cosine distance between the two vectors */

            // cout << "Found distance between " << *i << " and " << query_line << " : " << dist <<
            // endl;

            if ((double) dist < range) {
                // cout << "possible point found: " << *i << endl;

                already_in = 0;

                for (auto j = points_in_range_euc.begin(); j != points_in_range_euc.end(); ++j) {
                    if (*j == *i)
                        already_in = 1;
                }

                if (already_in == 0)
                    points_in_range_euc.push_back(*i);
            }
        }
    }

    auto finish1 = std::chrono::high_resolution_clock::now();

    std::cout << "Query " << query_line << endl;
    std::cout << "R-Near Neighbours: " << endl;

    for (auto j = points_in_range_euc.begin(); j != points_in_range_euc.end(); ++j) {
        // cout << "Point " << *j << " is in range " << range << endl;
        std::cout << "Item " << *j << endl;
    }

    std::chrono::duration<double> elapsed1 = finish1 - start1;

    // auto start2 = std::chrono::high_resolution_clock::now();

    // Euclidian_Full_Search_Range(query_line,range);

    // auto finish2 = std::chrono::high_resolution_clock::now();

    // std::chrono::duration<double> elapsed2 = finish2 - start2;

    std::cout << "tLSH: " << elapsed1.count() << endl;

    // std::cout <<  "tTrue: " << elapsed2.count() << endl;

    std::cout << "==================================================== " << endl;
    points_in_range_euc.clear();
}

using ULL = unsigned long long;
using Vec3 = std::vector<std::vector<std::vector<ULL>>>;

Vec3 readEuclidianHashTables() {
    Vec3 tables;
    std::ifstream in("Euclidian_Hash_Tables");
    size_t outerSize;
    if (!(in >> outerSize))
        throw std::runtime_error("Failed to read outer size");

    tables.resize(outerSize);

    for (size_t i = 0; i < outerSize; ++i) {
        size_t midSize;
        in >> midSize;
        tables[i].resize(midSize);

        for (size_t j = 0; j < midSize; ++j) {
            size_t innerSize;
            in >> innerSize;
            tables[i][j].resize(innerSize);

            for (size_t k = 0; k < innerSize; ++k)
                in >> tables[i][j][k];
        }
    }

    return tables;
}


void testRead() {
    std::ifstream in("Euclidian_Hash_Tables");
    string output;
    while (!in.eof()) {
        in >> output;
        cout << output << endl;
    }
}

void readEuclidianHashTablesInSeries(int number_of_files) {
    Vec3 outer_tables;
    for (int t = 0; t <= number_of_files; t++) {
        Vec3 tables;
        string fileName = "Euclidian_Hash_Tables_";
        fileName.append(to_string(t));
        std::ifstream in(fileName);
        size_t outerSize;
        if (!(in >> outerSize))
            throw std::runtime_error("Failed to read outer size");

        tables.resize(outerSize);

        for (size_t i = 0; i < outerSize; ++i) {
            size_t midSize;
            in >> midSize;
            tables[i].resize(midSize);

            for (size_t j = 0; j < midSize; ++j) {
                size_t innerSize;
                in >> innerSize;
                tables[i][j].resize(innerSize);

                for (size_t k = 0; k < innerSize; ++k)
                    in >> tables[i][j][k];
            }
        }

        if (t==0) {
            outer_tables = tables;
        }
        else {
            for (size_t i = 0; i < tables.size(); ++i) {
                for (size_t j = 0; j < tables[i].size(); ++j) {
                    outer_tables[i][j].resize(tables[i][j].size()+outer_tables[i][j].size());
                    for (size_t k = 0; k < tables[i][j].size(); ++k)
                        outer_tables[i][j][k] = tables[i][j][k];
                }
            }
        }
    }
    Euclidian_Hash_Tables = outer_tables;
}

std::vector<double> readEuclidianT() {
    std::ifstream in("t");
    size_t dcount;
    in >> dcount;
    std::vector<double> doubles;
    doubles.resize(dcount);

    for (size_t i = 0; i < dcount; ++i)
        in >> doubles[i];

    return doubles;
}

std::vector<vector<double>> readEuclidianV() {
    std::ifstream in("v");
    size_t outerSize;
    in >> outerSize;
    std::vector<std::vector<double>> vecs;
    vecs.resize(outerSize);

    for (size_t i = 0; i < outerSize; ++i) {
        size_t innerSize;
        in >> innerSize;
        vecs[i].resize(innerSize);

        for (size_t j = 0; j < innerSize; ++j)
            in >> vecs[i][j];
    }

    return vecs;
}

long long int get_n() {
    std::ifstream in("n");
    long long int n;
    in >> n;
    return n;
}

int get_dim() {
    std::ifstream in("dim");
    int dim;
    in >> dim;
    return dim;
}

std::vector<std::vector<int>> readEuclidianAmplifiedFunctions() {
    std::ifstream in("eaf");
    size_t outerSize;
    in >> outerSize;
    std::vector<std::vector<int>> vecs;
    vecs.resize(outerSize);

    for (size_t i = 0; i < outerSize; ++i) {
        size_t innerSize;
        in >> innerSize;
        vecs[i].resize(innerSize);

        for (size_t j = 0; j < innerSize; ++j)
            in >> vecs[i][j];
    }

    return vecs;
}

int readEuclidianW() {
    std::ifstream in("w");
    int w;
    in >> w;
    return w;
}

std::vector<int> readEuclidianPointsInRangeEuc() {
    std::ifstream in("points_in_range_euc");
    size_t size;
    in >> size;
    std::vector<int> points;
    points.resize(size);

    for (size_t i = 0; i < size; ++i)
        in >> points[i];

    return points;
}

void Euclidian_LSH_File_With_Prints(int L, int k, int N) {
    Euclidian_Hash_Tables = readEuclidianHashTables();
    t = readEuclidianT();
    v = readEuclidianV();
    n = get_n();
    dim = get_dim();
    Euclidian_Amplified_Functions = readEuclidianAmplifiedFunctions();
    w = readEuclidianW();
    points_in_range_euc = readEuclidianPointsInRangeEuc();
    string str;
    qFile >> str;

    double radius;
    long long unsigned int queries;

    if (str.compare("Radius:") == 0) {
        qFile >> radius;
        cout << "radius is " << radius << endl;

        queries = get_number_of_queries();

        for (int q = 1; q < queries; q++) {
            Range_Search_Euclidian(q, radius, L, k);
        }
    } else {
        queries = get_number_of_queries();

        for (int q = 0; q < queries; q++) {
            Nearest_Query_Euclidian(q, L, k, N);
        }
    }
}

void Euclidian_LSH_File(int L, int k, int N) {
    string str;
    qFile >> str;

    double radius;
    long long unsigned int queries;

    if (str.compare("Radius:") == 0) {
        qFile >> radius;
        cout << "radius is " << radius << endl;

        queries = get_number_of_queries();

        for (int q = 1; q < queries; q++) {
            Range_Search_Euclidian(q, radius, L, k);
        }
    } else {
        queries = get_number_of_queries();

        for (int q = 0; q < queries; q++) {
            Nearest_Query_Euclidian(q, L, k, N);
        }
    }
}