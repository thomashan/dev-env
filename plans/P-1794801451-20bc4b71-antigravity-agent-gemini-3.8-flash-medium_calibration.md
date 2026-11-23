# Plan Calibration Report: P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794801664-21f0fec4-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794801434-curl/P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium/E-1794801664-21f0fec4-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794801434-curl/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-16T04:36:27.000Z`
- **Evaluated Commit SHA:** `5858a308668bc9608e6c9e28240361a58a2c71c4`
- **Base SHA:** `eeaf6a6c20206538035b475776371e24964da781`
- **Merge-Base SHA:** `eeaf6a6c20206538035b475776371e24964da781`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.97`             | `1.00`            | `0.03`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.35`             | `0.45`            | `0.10`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `6.00`             | `5.10`            | `0.90`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `3.50`             | `3.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `84.88`            | `88.52`           | `3.64`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `84.88`            | `88.52`           | `3.64`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.97 - 1.00| = 0.03$
- **Entropy Error:** $|0.35 - 0.45| = 0.10$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|6.00 - 5.10| = 0.90$
- **Learning Value Error:** $|3.50 - 3.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.97 \times 92.0 + 0.5 \times 3.5 - 0.3 \times 0.35 - 6.00 = 84.88$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 3.5 - 0.3 \times 0.45 - 5.10 = 88.52$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 3.5 - 0.3 \times 0.45 - 5.10 = 88.52$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +3.64$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.4` (5 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794801451-20bc4b71-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.03$, $cost\_error = 0.90$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
