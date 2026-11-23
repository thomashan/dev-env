# Plan Calibration Report: P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium.md`](P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1795057919-55750cff-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1795057633-node-extra-ca/P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium/E-1795057919-55750cff-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1795057633-node-extra-ca/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-19T03:23:32.000Z`
- **Evaluated Commit SHA:** `ee3ef1597d37f78fa106f0a691da9be16fb4f973`
- **Base SHA:** `a6b54113e9f7a8769b4865a22d41b56c470384ff`
- **Merge-Base SHA:** `a6b54113e9f7a8769b4865a22d41b56c470384ff`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.04`             | `0.54`            | `0.50`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `0.90`             | `0.77`            | `0.13`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `3.00`             | `3.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `91.67`            | `92.57`           | `0.90`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `91.67`            | `92.57`           | `0.90`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.04 - 0.54| = 0.50$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|0.90 - 0.77| = 0.13$
- **Learning Value Error:** $|3.00 - 3.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 92.0 + 0.5 \times 3.0 - 0.3 \times 0.04 - 0.90 = 91.67$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 3.0 - 0.3 \times 0.54 - 0.77 = 92.57$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 3.0 - 0.3 \times 0.54 - 0.77 = 92.57$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.90$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.7` (6 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795057650-d739e30f-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
(`p_success_error = 0.01`, `cost_error = 0.13`). The calibration step successfully completed the execution lifecycle and
delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
