# Plan Calibration Report: P-1795391695-ANA-G4A

- **Plan Reference:** [`plans/I-1795391675-fish-conda-homebrew-hooks/P-1795391695-ANA-G4A.md`](P-1795391695-ANA-G4A.md)
- **Execution ID:** `E-1795391884-ANA-G4A`
- **Execution Branch:** `I-1795391675-fish-conda-homebrew-hooks/P-1795391695-ANA-G4A/E-1795391884-ANA-G4A/_`
- **Intent Branch:** `I-1795391675-fish-conda-homebrew-hooks/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-argon`
- **Evaluation Timestamp:** `2026-11-23T00:17:05.000Z`
- **Evaluated Commit SHA:** `3130e722db8299eb89d87e0ecff6bd4dbd7f0e47`
- **Base SHA:** `ecf31e04da26eff7a48aeeb8d3ba9b7e75ad0668`
- **Merge-Base SHA:** `ecf31e04da26eff7a48aeeb8d3ba9b7e75ad0668`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.12`             | `1.64`            | `1.52`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `94.00`            | `94.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.45`             | `1.23`            | `0.22`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.50`             | `4.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `92.88`            | `94.53`           | `1.65`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `92.88`            | `94.53`           | `1.65`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.12 - 1.64| = 1.52$
- **Impact Error:** $|94.00 - 94.00| = 0.00$
- **Cost Error:** $|1.45 - 1.23| = 0.22$
- **Learning Value Error:** $|4.50 - 4.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 94.0 + 0.5 \times 4.5 - 0.3 \times 0.12 - 1.45 = 92.88$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 94.0 + 0.5 \times 4.5 - 0.3 \times 1.64 - 1.23 = 94.53$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 94.0 + 0.5 \times 4.5 - 0.3 \times 1.64 - 1.23 = 94.53$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.65$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `5.3` (6 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795391695-ANA-G4A` executed with minimal error ($p\_success\_error = 0.02$, $cost\_error = 0.22$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
