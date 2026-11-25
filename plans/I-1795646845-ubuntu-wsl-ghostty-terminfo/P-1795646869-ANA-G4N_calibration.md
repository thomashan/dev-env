# Plan Calibration Report: P-1795646869-ANA-G4N

- **Plan Reference:**
  [`plans/I-1795646845-ubuntu-wsl-ghostty-terminfo/P-1795646869-ANA-G4N.md`](P-1795646869-ANA-G4N.md)
- **Execution ID:** `E-1795647071-ANA-G4N`
- **Execution Branch:** `I-1795646845-ubuntu-wsl-ghostty-terminfo/P-1795646869-ANA-G4N/E-1795647071-ANA-G4N/_`
- **Intent Branch:** `I-1795646845-ubuntu-wsl-ghostty-terminfo/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-neon`
- **Evaluation Timestamp:** `2026-11-25T23:31:24.000Z`
- **Evaluated Commit SHA:** `f2f0f26d2dec75b32b4a025f1cfb4e8c2d66c1f0`
- **Base SHA:** `96e505e892a2514d8446f6a508e29635c9c54381`
- **Merge-Base SHA:** `96e505e892a2514d8446f6a508e29635c9c54381`
- **Merged Commits:** `0`
- **Patch Size Base:** `plan`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.97`             | `1.00`            | `0.03`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.12`             | `1.15`            | `1.03`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `97.00`            | `97.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.00`             | `0.85`            | `0.15`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `6.00`             | `6.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `96.05`            | `98.81`           | `2.76`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `96.05`            | `98.81`           | `2.76`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.97 - 1.00| = 0.03$
- **Entropy Error:** $|0.12 - 1.15| = 1.03$
- **Impact Error:** $|97.00 - 97.00| = 0.00$
- **Cost Error:** $|1.00 - 0.85| = 0.15$
- **Learning Value Error:** $|6.00 - 6.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.97 \times 97.0 + 0.5 \times 6.0 - 0.3 \times 0.12 - 1.00 = 96.05$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 97.0 + 0.5 \times 6.0 - 0.3 \times 1.15 - 0.85 = 98.81$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 97.0 + 0.5 \times 6.0 - 0.3 \times 1.15 - 0.85 = 98.81$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +2.76$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `3.7` (5 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795646869-ANA-G4N` executed with minimal error ($p\_success\_error = 0.03$, $cost\_error = 0.15$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
