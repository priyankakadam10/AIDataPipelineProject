from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

with open(
    "configs/column_synonyms.json",
    "r"
) as f:
    COLUMN_SYNONYMS = json.load(f)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def dictionary_match(column_name):

    column_name = column_name.lower()

    for canonical_col, aliases in COLUMN_SYNONYMS.items():

        if column_name == canonical_col.lower():
            return canonical_col, 1.0

        if column_name in [
            alias.lower()
            for alias in aliases
        ]:
            return canonical_col, 0.95

    return None, 0.0

def match_schema(
        source_columns,
        target_columns):

    mappings = {}

    target_embeddings = model.encode(
        target_columns
    )

    for src in source_columns:

        matched_col, confidence = (
            dictionary_match(src)
        )

        if matched_col:

            mappings[src] = {
                "matched_column": matched_col,
                "confidence": confidence,
                "match_type": "DICTIONARY"
            }

            continue

        src_embedding = model.encode(
            [src]
        )

        semantic_scores = cosine_similarity(
            src_embedding,
            target_embeddings
        )[0]

        best_match = None
        best_score = 0

        for idx, tgt in enumerate(
            target_columns
        ):

            lev_score = (
                fuzz.ratio(
                    src.lower(),
                    tgt.lower()
                ) / 100
            )

            semantic_score = (
                semantic_scores[idx]
            )

            final_score = (
                0.4 * lev_score
                +
                0.6 * semantic_score
            )

            if final_score > best_score:

                best_score = final_score
                best_match = tgt

        mappings[src] = {
            "matched_column": best_match,
            "confidence": round(
                float(best_score),
                2
            ),
            "match_type": "AI"
        }

    return mappings