"""Every score the lab asks for, computed in one place.

"""
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    recall_score,
    roc_auc_score,
)


def false_alarm_rate(y_true, y_pred):
    """FAR: of all the traffic that was genuinely NORMAL, what fraction did we
    wrongly scream about?

        FAR = FP / (FP + TN)

    scikit-learn has no built-in function for this, so we compute it from the
    confusion matrix ourselves.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    denominator = fp + tn
    return float(fp / denominator) if denominator > 0 else 0.0


def evaluate_binary(model_name, y_true, y_pred, y_score=None, notes=""):
    """Return one row of the results table for a normal-vs-attack model.

    y_pred  = the model's yes/no decision  (0 = normal, 1 = attack)
    y_score = the model's confidence, 0.0 to 1.0. Needed for ROC-AUC.
    """
    row = {
        "model": model_name,
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
        "recall_attack": recall_score(y_true, y_pred, pos_label=1, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_score) if y_score is not None else np.nan,
        "FAR": false_alarm_rate(y_true, y_pred),
        "notes": notes,
    }
    return row


def macro_false_alarm_rate(y_true, y_pred, labels):
    """The multiclass version of FAR: work out the false alarm rate separately
    for every attack type, then average them.
    """
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    total = cm.sum()
    per_class = []
    for i in range(len(labels)):
        fp = cm[:, i].sum() - cm[i, i]
        tn = total - cm[i, :].sum() - cm[:, i].sum() + cm[i, i]
        per_class.append(fp / (fp + tn) if (fp + tn) > 0 else 0.0)
    return float(np.mean(per_class))


def print_row(row):
    """Print one result line in a readable way."""
    print(
        f"  {row['model']:<28} "
        f"acc={row['accuracy']:.4f}  "
        f"macroF1={row['macro_f1']:.4f}  "
        f"recall={row['recall_attack']:.4f}  "
        f"AUC={row['roc_auc']:.4f}  "
        f"FAR={row['FAR']:.4f}"
    )
