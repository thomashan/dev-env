# Plan Calibration Report: P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794988768-9b1c802a-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794988615-nvim-markdownlint/P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium/E-1794988768-9b1c802a-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794988615-nvim-markdownlint/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-18T08:20:20.000Z`
- **Evaluated Commit SHA:** `5ce13032f2a505f977e809aa0411edbb70d342ba`
- **Base SHA:** `cf3c8fc47dd7856df802fe3dad6e4041956e2909`
- **Merge-Base SHA:** `cf3c8fc47dd7856df802fe3dad6e4041956e2909`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.03`             | `0.25`            | `0.22`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `90.00`            | `90.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `0.50`             | `0.50`            | `0.00`                                | Exact           | Highly Accurate            |
| **Learning Value**                                 | `2.00`             | `2.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `89.59`            | `90.43`           | `0.84`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `89.59`            | `90.43`           | `0.84`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.03 - 0.25| = 0.22$
- **Impact Error:** $|90.00 - 90.00| = 0.00$
- **Cost Error:** $|0.50 - 0.50| = 0.00$
- **Learning Value Error:** $|2.00 - 2.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 90.0 + 0.5 \times 2.0 - 0.3 \times 0.03 - 0.50 = 89.59$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 90.0 + 0.5 \times 2.0 - 0.3 \times 0.25 - 0.50 = 90.43$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 90.0 + 0.5 \times 2.0 - 0.3 \times 0.25 - 0.50 = 90.43$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.84$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `0.7` (3 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794988632-ef2415b3-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
(`p_success_error = 0.01`, `cost_error = 0.00`). The calibration step successfully completed the execution lifecycle and
delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
