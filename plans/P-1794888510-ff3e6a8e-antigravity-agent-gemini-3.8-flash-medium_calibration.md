# Plan Calibration Report: P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794888692-1d771723-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794888493-galaxy-check/P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium/E-1794888692-1d771723-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794888493-galaxy-check/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T04:23:30.000Z`
- **Evaluated Commit SHA:** `225420cb4daddd059c6f9bb23b3ac01d20a5616c`
- **Base SHA:** `6edd13006cd8c09f0e357fe5ff7940460a26e644`
- **Merge-Base SHA:** `6edd13006cd8c09f0e357fe5ff7940460a26e644`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.13`             | `0.46`            | `0.33`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `4.50`             | `3.82`            | `0.68`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `88.54`            | `90.04`           | `1.50`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `88.54`            | `90.04`           | `1.50`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.13 - 0.46| = 0.33$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|4.50 - 3.82| = 0.68$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.13 - 4.50 = 88.54$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.46 - 3.82 = 90.04$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.46 - 3.82 = 90.04$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.50$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.4` (4 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794888510-ff3e6a8e-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.01$, $cost\_error = 0.68$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
