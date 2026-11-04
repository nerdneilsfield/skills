"""Offline synthetic IID classification; not a project-quality benchmark."""
import json
import numpy as np
import sklearn
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def run():
    x, y = make_classification(n_samples=120, n_features=6, n_informative=4,
                               n_redundant=0, random_state=17)
    train_x, test_x, train_y, test_y = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=19)
    # Each CV clone fits its own scaler. The reserved test set never enters fit.
    search = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)),
                          {'logisticregression__C': [0.1, 1.0]},
                          cv=StratifiedKFold(3, shuffle=True, random_state=23),
                          scoring='balanced_accuracy', n_jobs=1, error_score='raise')
    search.fit(train_x, train_y)
    scaler = search.best_estimator_.named_steps['standardscaler']
    trained_mean = scaler.mean_.copy()
    np.testing.assert_allclose(trained_mean, train_x.mean(axis=0))
    prediction = search.predict(test_x)
    np.testing.assert_array_equal(trained_mean, scaler.mean_)
    baseline = DummyClassifier(strategy='most_frequent').fit(train_x, train_y)
    return {'sklearn_version': sklearn.__version__, 'train_only_scaler': True,
            'test_samples': len(test_y),
            'balanced_accuracy': float(balanced_accuracy_score(test_y, prediction)),
            'baseline_balanced_accuracy': float(balanced_accuracy_score(test_y, baseline.predict(test_x))),
            'scope': 'synthetic IID CPU smoke; not group/time generalization'}

if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, allow_nan=False))
