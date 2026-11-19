# Plan Calibration Report: P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium

- **Plan Reference:**
  [`plans/P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium.md`](P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium.md)
- **Execution ID:** `E-1795129292-687283f9-antigravity-agent-gemini-3.8-flash-medium`
- **Execution Branch:**
  `I-1795129105-tmux-pane-cwd/P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium/E-1795129292-687283f9-antigravity-agent-gemini-3.8-flash-medium/_`
- **Intent Branch:** `I-1795129105-tmux-pane-cwd/_`
- **Evaluating Agent:** `antigravity-agent/gemini-3.8-flash-medium`
- **Evaluation Timestamp:** `2026-11-19T23:07:18.000Z`
- **Evaluated Commit SHA:** `61d86d64c42fe281b1ca32db3848c9160af61783`
- **Base SHA:** `912242fc87f2017725a542e3ecc2bfe9812a3d9a`
- **Merge-Base SHA:** `912242fc87f2017725a542e3ecc2bfe9812a3d9a`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.99`             | `1.00`            | `0.01`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.02`             | `0.18`            | `0.16`                                | High (≤ 1.0)    | Underestimated Risk        |
| **Impact**                                         | `90.00`            | `90.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `0.45`             | `0.50`            | `0.05`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `2.00`             | `2.00`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `89.64`            | `90.45`           | `0.81`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `89.64`            | `90.45`           | `0.81`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.99 - 1.00| = 0.01$
- **Entropy Error:** $|0.02 - 0.18| = 0.16$
- **Impact Error:** $|90.00 - 90.00| = 0.00$
- **Cost Error:** $|0.45 - 0.50| = 0.05$
- **Learning Value Error:** $|2.00 - 2.00| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.99 \times 90.0 + 0.5 \times 2.0 - 0.3 \times 0.02 - 0.45 = 89.64$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 90.0 + 0.5 \times 2.0 - 0.3 \times 0.18 - 0.50 = 90.45$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 90.0 + 0.5 \times 2.0 - 0.3 \times 0.18 - 0.50 = 90.45$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +0.81$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `0.5` (2 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795129122-cbe147ab-antigravity-agent-gemini-3.8-flash-medium` executed with minimal error ($p\_success\_error =
0.01$, $cost\_error = 0.05$). The calibration step successfully completed the execution lifecycle and delivered verified
post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** n/a
- **Recall (changed files the touch set covered):** n/a
