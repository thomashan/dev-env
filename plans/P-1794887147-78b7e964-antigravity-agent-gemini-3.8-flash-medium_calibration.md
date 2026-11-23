# Plan Calibration Report: P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794887556-7b533bed-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794887131-conda-detect/P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium/E-1794887556-7b533bed-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794887131-conda-detect/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T04:06:47.000Z`
- **Evaluated Commit SHA:** `c19f659143fac9413831fa28f4778943d730d63f`
- **Base SHA:** `45989693be7768f6fff45bfa1bd4370245960786`
- **Merge-Base SHA:** `45989693be7768f6fff45bfa1bd4370245960786`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.14`             | `0.48`            | `0.34`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `90.00`            | `90.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `4.00`             | `3.40`            | `0.60`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `87.06`            | `88.46`           | `1.40`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `87.06`            | `88.46`           | `1.40`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.14 - 0.48| = 0.34$
- **Impact Error:** $|90.00 - 90.00| = 0.00$
- **Cost Error:** $|4.00 - 3.40| = 0.60$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 90.0 + 0.5 \times 4.0 - 0.3 \times 0.14 - 4.00 = 87.06$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 90.0 + 0.5 \times 4.0 - 0.3 \times 0.48 - 3.40 = 88.46$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 90.0 + 0.5 \times 4.0 - 0.3 \times 0.48 - 3.40 = 88.46$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.40$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.5` (3 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794887147-78b7e964-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
(`p_success_error = 0.01`, `cost_error = 0.60`). The calibration step successfully completed the execution lifecycle and
delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
