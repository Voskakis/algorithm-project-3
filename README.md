# 3η Προγραμματιστική Εργασία (Χειμερινό 2025–26)
## Υπολογιστική Βιολογία & Αναζήτηση Δεδομένων  
**Θέμα:** Αναζήτηση “Απομακρυσμένων” Ομολόγων με Προσεγγιστικές Μεθόδους (ANN) & ESM-2

Η εργασία υλοποιείται σε Linux με Python 3.10+ και χρησιμοποιεί embeddings πρωτεϊνών από το μοντέλο **facebook/esm2_t6_8M_UR50D**.  
Στόχος είναι η αναζήτηση γειτόνων (ANN) στο χώρο των embeddings και η σύγκριση με αναφορά το **BLAST (local alignment)**.

---

## Περιεχόμενα
- [Απαιτήσεις](#απαιτήσεις)
- [Δεδομένα](#δεδομένα)
- [Δομή Project](#δομή-project)
- [Εγκατάσταση](#εγκατάσταση)
- [Εκτέλεση](#εκτέλεση)
  - [A. Παραγωγή Embeddings](#a-παραγωγή-embeddings)
  - [B. Αναζήτηση & Benchmark](#b-αναζήτηση--benchmark)
- [Παράμετροι / Πειράματα](#παράμετροι--πειράματα)
- [Μορφή Εξόδου](#μορφή-εξόδου)
- [Αναφορά](#αναφορά)
- [Git / Αναπαραγωγιμότητα](#git--αναπαραγωγιμότητα)
- [Troubleshooting](#troubleshooting)

---

## Απαιτήσεις
- Linux
- Python **3.10+**
- (Προαιρετικά αλλά προτεινόμενο) GPU + CUDA για πιο γρήγορο embedding
- BLAST+ εγκατεστημένο στο σύστημα (για το reference alignment)
  - Ενδεικτικά: `blastp` διαθέσιμο στο PATH

---

## Δεδομένα
Το project αναμένει τα παρακάτω αρχεία:
- `data/swissprot.fasta` : βάση δεδομένων πρωτεϊνών
- `data/targets.fasta` : πρωτεΐνες-στόχοι (queries)

Παράγονται επιπλέον:
- `data/protein_vectors.dat` : embeddings για το swissprot
- `data/blast_results/` : cache BLAST αποτελεσμάτων (αν ενεργοποιηθεί)

---

## Δομή Project
```text
assignment3/
├── data/
├── embeddings/
├── ann/
├── blast/
├── evaluation/
├── reporting/
├── scripts/
├── experiments/
├── report/
├── requirements.txt
└── readme.md
