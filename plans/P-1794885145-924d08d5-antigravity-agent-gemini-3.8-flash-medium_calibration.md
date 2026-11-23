# Plan Calibration Report: P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794885445-63c07d72-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794885128-factory-defaults/P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium/E-1794885445-63c07d72-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794885128-factory-defaults/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T03:30:21.000Z`
- **Evaluated Commit SHA:** `0b1c4dd29bafbd467434b5e2c1d6dd3f05f0aaf0`
- **Base SHA:** `96a781cf60dcc755f926b339283b0397faeee5cc`
- **Merge-Base SHA:** `96a781cf60dcc755f926b339283b0397faeee5cc`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.25`             | `1.57`            | `1.32`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `7.00`             | `5.95`            | `1.05`                                | Moderate        | Conservative Cost Estimate |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `86.00`            | `87.58`           | `1.58`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `86.00`            | `87.58`           | `1.58`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.25 - 1.57| = 1.32$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|7.00 - 5.95| = 1.05$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.25 - 7.00 = 86.00$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 1.57 - 5.95 = 87.58$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 1.57 - 5.95 = 87.58$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.58$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `5.1` (17 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794885145-924d08d5-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.01$, $cost\_error = 1.05$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
