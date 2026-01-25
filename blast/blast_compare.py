import os
import subprocess
import tempfile
import textwrap
from Bio import SeqIO
def blast_identity_by_fasta_id(
        fasta_db,
        query_seq,
        subject_id,
        blast_exe="blastp"
):
    """
    Return BLAST % identity between two protein sequences
    """
    subject_seq = ""
    for record in SeqIO.parse(fasta_db, "fasta"):
        if record.id == subject_id:
            subject_seq = str(record.seq)
            break
    if subject_seq == "":
        raise ValueError(f"Missing FASTA entry: subject_id")
    # Write temporary FASTA files
    with open("blastp_qf", 'w') as qf, open("blastp_sf", 'w') as sf:
        qf.write(">query\n" + textwrap.fill(query_seq, 60) + "\n")
        sf.write(">subject\n" + textwrap.fill(subject_seq, 60) + "\n")
        qf.flush()
        sf.flush()
        # Run BLAST in forced pairwise mode
        cmd = [
            blast_exe,
            "-query", qf.name,
            "-subject", sf.name,
            "-outfmt", "\"6 pident\"",
            "-max_hsps", "1"
        ]
        result = subprocess.run(
            ' '.join(cmd),
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
    if not result.stdout.strip():
        return None  # no detectable alignment
    pident = float(result.stdout.strip().splitlines()[0])
    return pident
