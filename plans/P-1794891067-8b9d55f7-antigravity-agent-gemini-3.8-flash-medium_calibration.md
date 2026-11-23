# Plan Calibration Report: P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794891238-b2ea28eb-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794891050-fish-path-order/P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium/E-1794891238-b2ea28eb-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794891050-fish-path-order/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T05:00:24.000Z`
- **Evaluated Commit SHA:** `5dea9f41a8c1a5a2638ab87e08f6b5e759ba84ea`
- **Base SHA:** `4a8c6233005835e9aea4b3f408c5ed8642f92262`
- **Merge-Base SHA:** `4a8c6233005835e9aea4b3f408c5ed8642f92262`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.06`             | `0.20`            | `0.14`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `88.00`            | `88.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.50`             | `1.27`            | `0.23`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `3.00`             | `3.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `87.10`            | `88.17`           | `1.07`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `87.10`            | `88.17`           | `1.07`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.06 - 0.20| = 0.14$
- **Impact Error:** $|88.00 - 88.00| = 0.00$
- **Cost Error:** $|1.50 - 1.27| = 0.23$
- **Learning Value Error:** $|3.00 - 3.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 88.0 + 0.5 \times 3.0 - 0.3 \times 0.06 - 1.50 = 87.10$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 88.0 + 0.5 \times 3.0 - 0.3 \times 0.20 - 1.27 = 88.17$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 88.0 + 0.5 \times 3.0 - 0.3 \times 0.20 - 1.27 = 88.17$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.07$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `0.5` (2 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794891067-8b9d55f7-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
(`p_success_error = 0.01`, `cost_error = 0.23`). The calibration step successfully completed the execution lifecycle and
delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
