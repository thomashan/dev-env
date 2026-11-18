# Plan Calibration Report: P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794973774-a6a79a4e-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794973331-dev-enhancements/P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium/E-1794973774-a6a79a4e-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794973331-dev-enhancements/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-18T04:32:34.000Z`
- **Evaluated Commit SHA:** `f417f1649a112fe3ad7014dd60b8b2f180075bcf`
- **Base SHA:** `d93058cb77af9b689ad48629e4ddaae69fa4a0d0`
- **Merge-Base SHA:** `d93058cb77af9b689ad48629e4ddaae69fa4a0d0`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.08`             | `1.25`            | `1.17`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `94.00`            | `94.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.20`             | `1.02`            | `0.18`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `92.90`            | `94.60`           | `1.70`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `92.90`            | `94.60`           | `1.70`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.08 - 1.25| = 1.17$
- **Impact Error:** $|94.00 - 94.00| = 0.00$
- **Cost Error:** $|1.20 - 1.02| = 0.18$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 94.0 + 0.5 \times 4.0 - 0.3 \times 0.08 - 1.20 = 92.90$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 94.0 + 0.5 \times 4.0 - 0.3 \times 1.25 - 1.02 = 94.60$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 94.0 + 0.5 \times 4.0 - 0.3 \times 1.25 - 1.02 = 94.60$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.70$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `4.0` (15 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794973348-a6487fd8-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.02$, $cost\_error = 0.18$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
