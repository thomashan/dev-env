# Plan Calibration Report: P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794966616-24ee10ce-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794966349-neovim-brew/P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium/E-1794966616-24ee10ce-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794966349-neovim-brew/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-18T02:12:07.000Z`
- **Evaluated Commit SHA:** `4585f9a5ef960e37d81125199b6e8dce982dca9c`
- **Base SHA:** `5f99bb90f70ad489bfdf84aaa0266e0c3d3c8076`
- **Merge-Base SHA:** `5f99bb90f70ad489bfdf84aaa0266e0c3d3c8076`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.05`             | `0.80`            | `0.75`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.10`             | `0.94`            | `0.16`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.50`             | `4.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `91.30`            | `93.07`           | `1.77`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `91.30`            | `93.07`           | `1.77`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.05 - 0.80| = 0.75$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|1.10 - 0.94| = 0.16$
- **Learning Value Error:** $|4.50 - 4.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 92.0 + 0.5 \times 4.5 - 0.3 \times 0.05 - 1.10 = 91.30$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 4.5 - 0.3 \times 0.80 - 0.94 = 93.07$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 4.5 - 0.3 \times 0.80 - 0.94 = 93.07$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.77$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `2.5` (8 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794966366-f68ff38e-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.02$, $cost\_error = 0.16$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
