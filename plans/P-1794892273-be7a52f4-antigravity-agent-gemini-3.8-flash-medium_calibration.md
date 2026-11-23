# Plan Calibration Report: P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794892581-faded22f-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794892256-align-versions/P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium/E-1794892581-faded22f-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794892256-align-versions/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T05:31:51.000Z`
- **Evaluated Commit SHA:** `742de938e8fb65c07b3315a7d7cff8e82f7c428e`
- **Base SHA:** `03cf4eea6088dd4e7d74a3f5f9bfd334e6816c6c`
- **Merge-Base SHA:** `03cf4eea6088dd4e7d74a3f5f9bfd334e6816c6c`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.12`             | `0.65`            | `0.53`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `95.00`            | `95.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `2.50`             | `2.12`            | `0.38`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `5.00`             | `5.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `94.01`            | `95.19`           | `1.18`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `94.01`            | `95.19`           | `1.18`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.12 - 0.65| = 0.53$
- **Impact Error:** $|95.00 - 95.00| = 0.00$
- **Cost Error:** $|2.50 - 2.12| = 0.38$
- **Learning Value Error:** $|5.00 - 5.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 95.0 + 0.5 \times 5.0 - 0.3 \times 0.12 - 2.50 = 94.01$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 95.0 + 0.5 \times 5.0 - 0.3 \times 0.65 - 2.12 = 95.19$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 95.0 + 0.5 \times 5.0 - 0.3 \times 0.65 - 2.12 = 95.19$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.18$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `2.0` (7 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794892273-be7a52f4-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.01$, $cost\_error = 0.38$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
