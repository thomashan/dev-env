# Plan Calibration Report: P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794918600-7a31f6d7-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794918292-multi-sh/P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium/E-1794918600-7a31f6d7-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794918292-multi-sh/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T13:01:03.000Z`
- **Evaluated Commit SHA:** `bf5e9eae7e6096a128d24647f69a306fce5bb50d`
- **Base SHA:** `1a0e1be019561d3d6ef68b01c4039f95b2e2ef6c`
- **Merge-Base SHA:** `1a0e1be019561d3d6ef68b01c4039f95b2e2ef6c`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.07`             | `0.91`            | `0.84`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `93.00`            | `93.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.70`             | `1.44`            | `0.26`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `5.00`             | `5.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `92.85`            | `93.79`           | `0.94`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `92.85`            | `93.79`           | `0.94`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.07 - 0.91| = 0.84$
- **Impact Error:** $|93.00 - 93.00| = 0.00$
- **Cost Error:** $|1.70 - 1.44| = 0.26$
- **Learning Value Error:** $|5.00 - 5.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 93.0 + 0.5 \times 5.0 - 0.3 \times 0.07 - 1.70 = 92.85$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 93.0 + 0.5 \times 5.0 - 0.3 \times 0.91 - 1.44 = 93.79$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 93.0 + 0.5 \times 5.0 - 0.3 \times 0.91 - 1.44 = 93.79$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.94$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `2.9` (4 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794918308-e7c22976-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.01$, $cost\_error = 0.26$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
