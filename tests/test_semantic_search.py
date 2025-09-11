import sys
import types

import pytest

# Ensure a 'requests' stub is available before importing hermes.services.
import tests.requests_stub  # noqa: F401

# Stub out 'hermes.services.llm_interface' to avoid heavy dependencies.
sys.modules.setdefault(
    "hermes.services.llm_interface", types.ModuleType("llm_interface")
)


# Provide minimal sklearn stubs so semantic_search can be imported without the
# real scikit-learn dependency.
class _Array(list):
    def ravel(self):
        return self

    def argsort(self):
        return _Array(sorted(range(len(self)), key=self.__getitem__))


class TfidfVectorizer:
    def fit_transform(self, docs):
        vocab = set()
        tokenized = []
        for doc in docs:
            words = doc.lower().split()
            tokenized.append(words)
            vocab.update(words)
        self.vocab = sorted(vocab)
        matrix = []
        for words in tokenized:
            matrix.append([1.0 if w in words else 0.0 for w in self.vocab])
        return _Array(matrix)

    def transform(self, docs):
        matrix = []
        for doc in docs:
            words = doc.lower().split()
            matrix.append([1.0 if w in words else 0.0 for w in self.vocab])
        return _Array(matrix)


def cosine_similarity(query_vecs, matrix):
    q = query_vecs[0]
    sims = []
    qnorm = sum(a * a for a in q) ** 0.5
    for doc in matrix:
        dnorm = sum(b * b for b in doc) ** 0.5
        if qnorm == 0 or dnorm == 0:
            sims.append(0.0)
            continue
        dot = sum(a * b for a, b in zip(q, doc))
        sims.append(dot / (qnorm * dnorm))
    return _Array(sims)


sklearn = types.ModuleType("sklearn")
feature_extraction = types.ModuleType("sklearn.feature_extraction")
text = types.ModuleType("sklearn.feature_extraction.text")
text.TfidfVectorizer = TfidfVectorizer
feature_extraction.text = text
metrics = types.ModuleType("sklearn.metrics")
pairwise = types.ModuleType("sklearn.metrics.pairwise")
pairwise.cosine_similarity = cosine_similarity
metrics.pairwise = pairwise
sklearn.feature_extraction = feature_extraction
sklearn.metrics = metrics
sys.modules.setdefault("sklearn", sklearn)
sys.modules.setdefault("sklearn.feature_extraction", feature_extraction)
sys.modules.setdefault("sklearn.feature_extraction.text", text)
sys.modules.setdefault("sklearn.metrics", metrics)
sys.modules.setdefault("sklearn.metrics.pairwise", pairwise)

from hermes.data import database  # noqa: E402
from hermes.services import db as dao  # noqa: E402
from hermes.services.semantic_search import semantic_search  # noqa: E402


@pytest.fixture
def sample_ideas(tmp_path, monkeypatch):
    db_file = tmp_path / "semantic.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    monkeypatch.setattr(dao, "DB_PATH", str(db_file))
    database.inicializar_banco()

    user1 = dao.add_user("Alice", "tipo")
    user2 = dao.add_user("Bob", "tipo")

    dao.add_idea(
        user1,
        "Kanban",
        "We should manage tasks with kanban columns for better flow.",
    )
    dao.add_idea(user1, "Misc", "Something unrelated")
    dao.add_idea(
        user2,
        "Remote Kanban",
        "Sharing work across kanban columns in remote teams.",
    )

    return {"user1": user1, "user2": user2}


def test_semantic_search_returns_relevant_idea(sample_ideas):
    results = semantic_search("kanban conims")
    assert results
    assert "kanban columns" in results[0]["body"].lower()


def test_semantic_search_filters_by_user(sample_ideas):
    user1 = sample_ideas["user1"]
    user2 = sample_ideas["user2"]

    res1 = semantic_search("kanban conims", user_id=user1)
    assert len(res1) == 2
    assert all(r["user_id"] == user1 for r in res1)
    assert "kanban columns" in res1[0]["body"].lower()

    res2 = semantic_search("kanban conims", user_id=user2)
    assert len(res2) == 1
    assert res2[0]["user_id"] == user2
    assert "kanban columns" in res2[0]["body"].lower()
