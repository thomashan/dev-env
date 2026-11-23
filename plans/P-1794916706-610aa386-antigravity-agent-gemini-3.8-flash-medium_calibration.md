# Plan Calibration Report: P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium.md`](P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1794916935-f6847f1a-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1794916689-clean-wizard-prompts/P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium/E-1794916935-f6847f1a-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1794916689-clean-wizard-prompts/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-17T12:11:49.000Z`
- **Evaluated Commit SHA:** `314be9b97de045ed0befc3a5cac8931f8b6a17d4`
- **Base SHA:** `90f16db6ec2389a148617bd7f6ebb1f9616bef30`
- **Merge-Base SHA:** `90f16db6ec2389a148617bd7f6ebb1f9616bef30`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.07`             | `0.46`            | `0.39`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `92.00`            | `92.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.50`             | `1.27`            | `0.23`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.00`             | `4.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `91.56`            | `92.59`           | `1.03`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `91.56`            | `92.59`           | `1.03`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.07 - 0.46| = 0.39$
- **Impact Error:** $|92.00 - 92.00| = 0.00$
- **Cost Error:** $|1.50 - 1.27| = 0.23$
- **Learning Value Error:** $|4.00 - 4.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.07 - 1.50 = 91.56$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.46 - 1.27 = 92.59$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 92.0 + 0.5 \times 4.0 - 0.3 \times 0.46 - 1.27 = 92.59$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.03$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `1.4` (5 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1794916706-610aa386-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error
($p\_success\_error =
0.01$, $cost\_error = 0.23$). The calibration step successfully completed the execution lifecycle
and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
