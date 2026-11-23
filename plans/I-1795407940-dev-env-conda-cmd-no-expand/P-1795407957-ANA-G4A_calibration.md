# Plan Calibration Report: P-1795407957-ANA-G4A

- **Plan Reference:**
  [`plans/I-1795407940-dev-env-conda-cmd-no-expand/P-1795407957-ANA-G4A.md`](P-1795407957-ANA-G4A.md)
- **Execution ID:** `E-1795408113-ANA-G4A`
- **Execution Branch:** `I-1795407940-dev-env-conda-cmd-no-expand/P-1795407957-ANA-G4A/E-1795408113-ANA-G4A/_`
- **Intent Branch:** `I-1795407940-dev-env-conda-cmd-no-expand/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-argon`
- **Evaluation Timestamp:** `2026-11-23T04:38:10.000Z`
- **Evaluated Commit SHA:** `38c1a77d1b2afc7907a1c76a3d8d075635879db5`
- **Base SHA:** `be4e7f58ba58670eea69a45cdc4096f6fe483965`
- **Merge-Base SHA:** `be4e7f58ba58670eea69a45cdc4096f6fe483965`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.08`             | `0.39`            | `0.31`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `96.00`            | `96.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.00`             | `0.85`            | `0.15`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.50`             | `4.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `96.27`            | `97.28`           | `1.01`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `96.27`            | `97.28`           | `1.01`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.08 - 0.39| = 0.31$
- **Impact Error:** $|96.00 - 96.00| = 0.00$
- **Cost Error:** $|1.00 - 0.85| = 0.15$
- **Learning Value Error:** $|4.50 - 4.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 96.0 + 0.5 \times 4.5 - 0.3 \times 0.08 - 1.00 = 96.27$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 96.0 + 0.5 \times 4.5 - 0.3 \times 0.39 - 0.85 = 97.28$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 96.0 + 0.5 \times 4.5 - 0.3 \times 0.39 - 0.85 = 97.28$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.01$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.2` (3 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795407957-ANA-G4A` executed with minimal error ($p\_success\_error = 0.01$, $cost\_error = 0.15$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
