# Plan Calibration Report: P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794808371-23cac9c7-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794808105-toolset/P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium/E-1794808371-23cac9c7-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794808105-toolset/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-16T06:36:08.000Z`
- **Evaluated Commit SHA:** `40aa2bb7795d06fc34cfbe7be1d9fe13c035e85e`
- **Base SHA:** `3773f4851af1569d2c7739282b3f375de177906f`
- **Merge-Base SHA:** `3773f4851af1569d2c7739282b3f375de177906f`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.35`             | `1.10`            | `0.75`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `94.00`            | `94.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `6.00`             | `5.10`            | `0.90`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `3.50`             | `3.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `87.77`            | `90.32`           | `2.55`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `87.77`            | `90.32`           | `2.55`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.35 - 1.10| = 0.75$
- **Impact Error:** $|94.00 - 94.00| = 0.00$
- **Cost Error:** $|6.00 - 5.10| = 0.90$
- **Learning Value Error:** $|3.50 - 3.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 94.0 + 0.5 \times 3.5 - 0.3 \times 0.35 - 6.00 = 87.77$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 94.0 + 0.5 \times 3.5 - 0.3 \times 1.10 - 5.10 = 90.32$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 94.0 + 0.5 \times 3.5 - 0.3 \times 1.10 - 5.10 = 90.32$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +2.55$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `3.5` (10 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794808123-11998ef9-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.02$, $cost\_error = 0.90$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
