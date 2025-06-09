import json
import pandas as pd
from pathlib import Path

# load json
def load_claims(jsonl_file):
    claims = []
    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in file:
            claims.append(json.loads(line))
    return claims

# loads wiki index from a json file
def load_wiki_index(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# retrieve a specific sentence from a wiki page using indexes
def find_sentence_with_index(title, sentence_idx, wiki_index):
    entry = wiki_index.get(title)
    if not entry:
        return None

    file_path = Path(entry['file'])
    offset = entry['offset']

    with file_path.open('r', encoding='utf-8') as f:
        f.seek(offset)
        line = f.readline()
        record = json.loads(line)
        for line_text in record.get('lines', '').split('\n'):
            if line_text.startswith(f"{sentence_idx}\t"):
                return line_text.split('\t', 1)[1]
    return None

# given a claim, return list of evidence sentences relying on the index
def get_evidence_sentences(claim_obj, wiki_index):
    """
    Given a claim object, return a list of gold evidence sentences using the index.
    """
    sentences = []
    for evidence_set in claim_obj.get("evidence", []):
        for _, page, sentence_id in evidence_set:
            sentence = find_sentence_with_index(page, sentence_id, wiki_index)
            if sentence:
                sentences.append(sentence)
    return sentences

# build final dataframe with appropriate columns
def build_preprocessed_dataframe(claims, wiki_index_path):
    # load index
    wiki_index = load_wiki_index(wiki_index_path)
    rows = []

    for claim_obj in claims:
        label = claim_obj.get("label")

        if label == "NOT ENOUGH INFO":
            continue

        claim_text = claim_obj.get("claim")
        evidence_sentences = get_evidence_sentences(claim_obj, wiki_index)

        for sent in evidence_sentences:
            rows.append({
                "claim": claim_text,
                "evidence": sent,
                "label": label
            })
    return pd.DataFrame(rows)

def main():
    print("hello world")

if __name__ == "__main__":
    main()