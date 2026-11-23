# Plan Calibration Report: P-1795414265-ANA-G4A

- **Plan Reference:**
  [`plans/I-1795414247-dev-env-e2e-converge-testing/P-1795414265-ANA-G4A.md`](P-1795414265-ANA-G4A.md)
- **Execution ID:** `E-1795414572-ANA-G4A`
- **Execution Branch:** `I-1795414247-dev-env-e2e-converge-testing/P-1795414265-ANA-G4A/E-1795414572-ANA-G4A/_`
- **Intent Branch:** `I-1795414247-dev-env-e2e-converge-testing/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-argon`
- **Evaluation Timestamp:** `2026-11-23T06:56:39.000Z`
- **Evaluated Commit SHA:** `55861fc57ae9fa08510aa1ecf0e3ae147730029a`
- **Base SHA:** `7face7dbb79bc28dcd3f1199c8f9c118cb97bc7f`
- **Merge-Base SHA:** `7face7dbb79bc28dcd3f1199c8f9c118cb97bc7f`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.14`             | `2.41`            | `2.27`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `98.00`            | `98.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.40`             | `1.19`            | `0.21`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `6.00`             | `6.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `97.60`            | `99.09`           | `1.49`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `97.60`            | `99.09`           | `1.49`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.14 - 2.41| = 2.27$
- **Impact Error:** $|98.00 - 98.00| = 0.00$
- **Cost Error:** $|1.40 - 1.19| = 0.21$
- **Learning Value Error:** $|6.00 - 6.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 98.0 + 0.5 \times 6.0 - 0.3 \times 0.14 - 1.40 = 97.60$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 98.0 + 0.5 \times 6.0 - 0.3 \times 2.41 - 1.19 = 99.09$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 98.0 + 0.5 \times 6.0 - 0.3 \times 2.41 - 1.19 = 99.09$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.49$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `7.9` (18 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795414265-ANA-G4A` executed with minimal error ($p\_success\_error = 0.02$, $cost\_error = 0.21$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `94.4%`

Changed files outside the touch set:

- `tests/test_templating.py`

Declared entries the diff did not touch:

- none
