# Plan Calibration Report: P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794888886-db094d5c-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794888693-dotfiles-syntax-fix/P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium/E-1794888886-db094d5c-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794888693-dotfiles-syntax-fix/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T04:23:09.000Z`
- **Evaluated Commit SHA:** `bac16c03dda0c4bc7c4f5d683ab0b19faddd7c32`
- **Base SHA:** `0a22bd146ddaede251a4fe61a2acce8e7a834adb`
- **Merge-Base SHA:** `0a22bd146ddaede251a4fe61a2acce8e7a834adb`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.08`             | `0.38`            | `0.30`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `88.00`            | `88.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `2.00`             | `1.70`            | `0.30`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `87.10`            | `88.19`           | `1.09`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `87.10`            | `88.19`           | `1.09`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.08 - 0.38| = 0.30$
- **Impact Error:** $|88.00 - 88.00| = 0.00$
- **Cost Error:** $|2.00 - 1.70| = 0.30$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 88.0 + 0.5 \times 4.0 - 0.3 \times 0.08 - 2.00 = 87.10$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 88.0 + 0.5 \times 4.0 - 0.3 \times 0.38 - 1.70 = 88.19$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 88.0 + 0.5 \times 4.0 - 0.3 \times 0.38 - 1.70 = 88.19$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.09$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.1` (3 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794888709-ed336de4-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.01$, $cost\_error = 0.30$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
