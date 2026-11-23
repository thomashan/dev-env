# Plan Calibration Report: P-1795405074-ANA-G4A

- **Plan Reference:**
  [`plans/I-1795405058-dev-env-user-and-wsl-wizard/P-1795405074-ANA-G4A.md`](P-1795405074-ANA-G4A.md)
- **Execution ID:** `E-1795405235-ANA-G4A`
- **Execution Branch:** `I-1795405058-dev-env-user-and-wsl-wizard/P-1795405074-ANA-G4A/E-1795405235-ANA-G4A/_`
- **Intent Branch:** `I-1795405058-dev-env-user-and-wsl-wizard/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-argon`
- **Evaluation Timestamp:** `2026-11-23T03:50:49.000Z`
- **Evaluated Commit SHA:** `0c5a6a8088433c4c4069d055f83a3d9174d46dab`
- **Base SHA:** `1d222bb730070ce9eb90de99eca2a7ec98c4b5a7`
- **Merge-Base SHA:** `1d222bb730070ce9eb90de99eca2a7ec98c4b5a7`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.10`             | `0.81`            | `0.71`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `95.00`            | `95.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.25`             | `1.06`            | `0.19`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.50`             | `4.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `95.02`            | `95.95`           | `0.93`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `95.02`            | `95.95`           | `0.93`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.10 - 0.81| = 0.71$
- **Impact Error:** $|95.00 - 95.00| = 0.00$
- **Cost Error:** $|1.25 - 1.06| = 0.19$
- **Learning Value Error:** $|4.50 - 4.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 95.0 + 0.5 \times 4.5 - 0.3 \times 0.10 - 1.25 = 95.02$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 95.0 + 0.5 \times 4.5 - 0.3 \times 0.81 - 1.06 = 95.95$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 95.0 + 0.5 \times 4.5 - 0.3 \times 0.81 - 1.06 = 95.95$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.93$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `2.6` (4 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795405074-ANA-G4A` executed with minimal error ($p\_success\_error = 0.01$, $cost\_error = 0.19$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
