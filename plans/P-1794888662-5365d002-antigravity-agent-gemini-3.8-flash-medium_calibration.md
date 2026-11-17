# Plan Calibration Report: P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794888891-437bc5d4-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794888646-node-26-lts/P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium/E-1794888891-437bc5d4-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794888646-node-26-lts/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T04:22:47.000Z`
- **Evaluated Commit SHA:** `de0f81067f94ad32e9fd4b76e3643bab3d062d44`
- **Base SHA:** `aac64d5673935b2a0e6d9cdcafd73a43b6227d2f`
- **Merge-Base SHA:** `aac64d5673935b2a0e6d9cdcafd73a43b6227d2f`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.10`             | `0.31`            | `0.21`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `85.00`            | `85.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `2.50`             | `2.12`            | `0.38`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `1.50`             | `1.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `82.37`            | `83.54`           | `1.17`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `82.37`            | `83.54`           | `1.17`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.10 - 0.31| = 0.21$
- **Impact Error:** $|85.00 - 85.00| = 0.00$
- **Cost Error:** $|2.50 - 2.12| = 0.38$
- **Learning Value Error:** $|1.50 - 1.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 85.0 + 0.5 \times 1.5 - 0.3 \times 0.10 - 2.50 = 82.37$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 85.0 + 0.5 \times 1.5 - 0.3 \times 0.31 - 2.12 = 83.54$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 85.0 + 0.5 \times 1.5 - 0.3 \times 0.31 - 2.12 = 83.54$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.17$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `0.9` (4 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794888662-5365d002-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.01$, $cost\_error = 0.38$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
