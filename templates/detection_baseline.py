"""AI for Security — 탐지/분류 베이스라인 (싸고 강한 것부터).

딥러닝 전에 먼저 돌려서 점수를 확보하는 용도. 표/텍스트/로그 공통.
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline


def tabular_baseline(X, y, seed=42):
    """표/피처형 → RandomForest. (xgboost/lightgbm 설치돼 있으면 교체 고려)"""
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
    clf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=seed)
    clf.fit(Xtr, ytr)
    print(classification_report(yte, clf.predict(Xte)))
    return clf


def text_baseline(texts, y, seed=42):
    """텍스트(피싱/이메일 등) → TF-IDF + 로지스틱."""
    Xtr, Xte, ytr, yte = train_test_split(texts, y, test_size=0.2, random_state=seed, stratify=y)
    clf = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
        LogisticRegression(max_iter=1000),
    )
    clf.fit(Xtr, ytr)
    print(classification_report(yte, clf.predict(Xte)))
    return clf


def anomaly_baseline(X, contamination=0.05, seed=42):
    """라벨 없는 로그/트래픽 이상탐지 → IsolationForest. 반환 -1=이상, 1=정상."""
    det = IsolationForest(contamination=contamination, random_state=seed, n_jobs=-1)
    pred = det.fit_predict(np.asarray(X))
    print(f"이상 {int((pred == -1).sum())} / 전체 {len(pred)}")
    return det, pred
