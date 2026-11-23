# Plan Calibration Report: P-1795395439-ANA-G4A

- **Plan Reference:** [`plans/I-1795395423-dev-env-ansible-wsl-tmux/P-1795395439-ANA-G4A.md`](P-1795395439-ANA-G4A.md)
- **Execution ID:** `E-1795395640-ANA-G4A`
- **Execution Branch:** `I-1795395423-dev-env-ansible-wsl-tmux/P-1795395439-ANA-G4A/E-1795395640-ANA-G4A/_`
- **Intent Branch:** `I-1795395423-dev-env-ansible-wsl-tmux/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-argon`
- **Evaluation Timestamp:** `2026-11-23T01:32:14.000Z`
- **Evaluated Commit SHA:** `bbe82a7b28dd36a3068be2045410996308c60a4b`
- **Base SHA:** `538ecdf21048fbd31df04d41928b81f9978c950b`
- **Merge-Base SHA:** `538ecdf21048fbd31df04d41928b81f9978c950b`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.08`             | `1.15`            | `1.07`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `94.00`            | `94.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.20`             | `1.02`            | `0.18`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `3.80`             | `3.80`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `93.74`            | `94.53`           | `0.79`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `93.74`            | `94.53`           | `0.79`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.08 - 1.15| = 1.07$
- **Impact Error:** $|94.00 - 94.00| = 0.00$
- **Cost Error:** $|1.20 - 1.02| = 0.18$
- **Learning Value Error:** $|3.80 - 3.80| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 94.0 + 0.5 \times 3.8 - 0.3 \times 0.08 - 1.20 = 93.74$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 94.0 + 0.5 \times 3.8 - 0.3 \times 1.15 - 1.02 = 94.53$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 94.0 + 0.5 \times 3.8 - 0.3 \times 1.15 - 1.02 = 94.53$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.79$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `3.7` (12 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795395439-ANA-G4A` executed with minimal error ($p\_success\_error = 0.01$, $cost\_error = 0.18$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
