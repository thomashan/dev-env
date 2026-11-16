# Plan Calibration Report: P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794817852-83fda13c-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794817597-getting-started/P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium/E-1794817852-83fda13c-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794817597-getting-started/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-16T08:53:08.000Z`
- **Evaluated Commit SHA:** `7110de7c6980bece29674570f7b1da418cf4a8c6`
- **Base SHA:** `28e6071ce9621f7b32ee8ec98fc4704ab156ddd5`
- **Merge-Base SHA:** `28e6071ce9621f7b32ee8ec98fc4704ab156ddd5`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.35`             | `1.28`            | `0.93`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `95.00`            | `95.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `6.00`             | `5.10`            | `0.90`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `3.50`             | `3.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `88.74`            | `91.27`           | `2.53`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `88.74`            | `91.27`           | `2.53`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.35 - 1.28| = 0.93$
- **Impact Error:** $|95.00 - 95.00| = 0.00$
- **Cost Error:** $|6.00 - 5.10| = 0.90$
- **Learning Value Error:** $|3.50 - 3.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 95.0 + 0.5 \times 3.5 - 0.3 \times 0.35 - 6.00 = 88.74$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 95.0 + 0.5 \times 3.5 - 0.3 \times 1.28 - 5.10 = 91.27$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 95.0 + 0.5 \times 3.5 - 0.3 \times 1.28 - 5.10 = 91.27$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +2.53$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `4.1` (8 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794817616-69c1360c-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.02$, $cost\_error = 0.90$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
