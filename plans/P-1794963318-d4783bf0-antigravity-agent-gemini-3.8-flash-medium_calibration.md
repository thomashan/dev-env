# Plan Calibration Report: P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794963485-6a934c22-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794963302-inject-ca/P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium/E-1794963485-6a934c22-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794963302-inject-ca/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-18T01:25:43.000Z`
- **Evaluated Commit SHA:** `b27c23277a35e5928bbc502f2e8f182f4817787f`
- **Base SHA:** `63ede9089764faa30b6ab4dbf726e968730785a8`
- **Merge-Base SHA:** `63ede9089764faa30b6ab4dbf726e968730785a8`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.05`             | `0.34`            | `0.29`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.10`             | `0.94`            | `0.16`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `91.05`            | `92.96`           | `1.91`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `91.05`            | `92.96`           | `1.91`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.05 - 0.34| = 0.29$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|1.10 - 0.94| = 0.16$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.05 - 1.10 = 91.05$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.34 - 0.94 = 92.96$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.34 - 0.94 = 92.96$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.91$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.0` (3 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794963318-d4783bf0-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.02$, $cost\_error = 0.16$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
