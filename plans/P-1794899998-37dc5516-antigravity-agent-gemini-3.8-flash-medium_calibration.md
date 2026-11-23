# Plan Calibration Report: P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794900220-09a4f647-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794899982-python-prompt/P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium/E-1794900220-09a4f647-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794899982-python-prompt/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T07:35:06.000Z`
- **Evaluated Commit SHA:** `bfe8b212a02b198b6fa0b03517998f0c2f8fd4c8`
- **Base SHA:** `b6391550b839692fccb2201383ef721e5e5f5fef`
- **Merge-Base SHA:** `b6391550b839692fccb2201383ef721e5e5f5fef`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.08`             | `0.51`            | `0.43`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `95.00`            | `95.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.10`             | `0.94`            | `0.16`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `94.93`            | `95.91`           | `0.98`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `94.93`            | `95.91`           | `0.98`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.08 - 0.51| = 0.43$
- **Impact Error:** $|95.00 - 95.00| = 0.00$
- **Cost Error:** $|1.10 - 0.94| = 0.16$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 95.0 + 0.5 \times 4.0 - 0.3 \times 0.08 - 1.10 = 94.93$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 95.0 + 0.5 \times 4.0 - 0.3 \times 0.51 - 0.94 = 95.91$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 95.0 + 0.5 \times 4.0 - 0.3 \times 0.51 - 0.94 = 95.91$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.98$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.6` (6 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794899998-37dc5516-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.01$, $cost\_error = 0.16$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
