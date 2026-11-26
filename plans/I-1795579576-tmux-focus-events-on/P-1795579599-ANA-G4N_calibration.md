# Plan Calibration Report: P-1795579599-ANA-G4N

- **Plan Reference:** [`plans/I-1795579576-tmux-focus-events-on/P-1795579599-ANA-G4N.md`](P-1795579599-ANA-G4N.md)
- **Execution ID:** `E-1795579754-ANA-G4N`
- **Execution Branch:** `I-1795579576-tmux-focus-events-on/P-1795579599-ANA-G4N/E-1795579754-ANA-G4N/_`
- **Intent Branch:** `I-1795579576-tmux-focus-events-on/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-neon`
- **Evaluation Timestamp:** `2026-11-25T04:29:37.000Z`
- **Evaluated Commit SHA:** `b1dc27bbc553f2cda8d0f79f998931eb5db7ee8e`
- **Base SHA:** `7965ac596178904134a2e983584a9e1a5753b141`
- **Merge-Base SHA:** `7965ac596178904134a2e983584a9e1a5753b141`
- **Merged Commits:** `0`
- **Patch Size Base:** `plan`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.07`             | `0.43`            | `0.36`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `95.00`            | `95.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `0.50`             | `0.50`            | `0.00`                                | Exact           | Highly Accurate            |
| **Learning Value**                                 | `4.50`             | `4.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `94.83`            | `96.62`           | `1.79`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `94.83`            | `96.62`           | `1.79`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.07 - 0.43| = 0.36$
- **Impact Error:** $|95.00 - 95.00| = 0.00$
- **Cost Error:** $|0.50 - 0.50| = 0.00$
- **Learning Value Error:** $|4.50 - 4.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 95.0 + 0.5 \times 4.5 - 0.3 \times 0.07 - 0.50 = 94.83$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 95.0 + 0.5 \times 4.5 - 0.3 \times 0.43 - 0.50 = 96.62$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 95.0 + 0.5 \times 4.5 - 0.3 \times 0.43 - 0.50 = 96.62$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.79$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.3` (2 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795579599-ANA-G4N` executed with minimal error ($p\_success\_error = 0.02$, $cost\_error = 0.00$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
