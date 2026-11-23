from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def semantic_match(
        source_cols,
        target_cols):

    target_embeddings = model.encode(
        target_cols
    )

    results = {}

    for col in source_cols:

        emb = model.encode([col])

        similarities = cosine_similarity(
            emb,
            target_embeddings
        )[0]

        best_idx = similarities.argmax()

        results[col] = {
            "match":
              target_cols[best_idx],

            "confidence":
              float(
                  similarities[best_idx]
              )
        }

    return results