# Plan Calibration Report: P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794797638-0efc6fff-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794797329-wizard/P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium/E-1794797638-0efc6fff-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794797329-wizard/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-16T03:39:14.000Z`
- **Evaluated Commit SHA:** `19097334a1507a0605de6ec648ad92a8fb7d3215`
- **Base SHA:** `40cdf9457977ba9f0be59abb45ace6f1d3f6c6cf`
- **Merge-Base SHA:** `40cdf9457977ba9f0be59abb45ace6f1d3f6c6cf`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.94`             | `1.00`            | `0.06`                                | Moderate        | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.65`             | `3.04`            | `2.39`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `96.00`            | `96.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `14.50`            | `12.32`           | `2.18`                                | Moderate        | Conservative Cost Estimate |
| **Learning Value**                                 | `6.00`             | `6.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `78.55`            | `85.77`           | `7.22`                                | Moderate        | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `78.55`            | `85.77`           | `7.22`                                | Moderate        | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.94 - 1.00| = 0.06$
- **Entropy Error:** $|0.65 - 3.04| = 2.39$
- **Impact Error:** $|96.00 - 96.00| = 0.00$
- **Cost Error:** $|14.50 - 12.32| = 2.18$
- **Learning Value Error:** $|6.00 - 6.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.94 \times 96.0 + 0.5 \times 6.0 - 0.3 \times 0.65 - 14.50 = 78.55$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 96.0 + 0.5 \times 6.0 - 0.3 \times 3.04 - 12.32 = 85.77$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 96.0 + 0.5 \times 6.0 - 0.3 \times 3.04 - 12.32 = 85.77$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +7.22$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `10.0` (32 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794797347-a9fe7160-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.06$, $cost\_error = 2.18$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
