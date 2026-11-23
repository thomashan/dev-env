# Plan Calibration Report: P-1795401489-ANA-G4A

- **Plan Reference:** [`plans/I-1795401473-dev-env-ansible-wsl-skip/P-1795401489-ANA-G4A.md`](P-1795401489-ANA-G4A.md)
- **Execution ID:** `E-1795401676-ANA-G4A`
- **Execution Branch:** `I-1795401473-dev-env-ansible-wsl-skip/P-1795401489-ANA-G4A/E-1795401676-ANA-G4A/_`
- **Intent Branch:** `I-1795401473-dev-env-ansible-wsl-skip/_`
- **Evaluating Agent:** `antigravity-agent/gemini-4-argon`
- **Evaluation Timestamp:** `2026-11-23T03:08:53.000Z`
- **Evaluated Commit SHA:** `92b4df7a5a87513d1883594e53f87fb91843c1ad`
- **Base SHA:** `e8983ec961597939d211a5794605c5613a701c77`
- **Merge-Base SHA:** `e8983ec961597939d211a5794605c5613a701c77`
- **Merged Commits:** `0`

---

## 1. Executive Calibration Summary

| Metric                                             | Predicted (`pred`) | Actual (`actual`) | Absolute Error (`abs(pred - actual)`) | Accuracy Rating | Bias Direction             |
| :------------------------------------------------- | :----------------- | :---------------- | :------------------------------------ | :-------------- | :------------------------- |
| **$P(\text{success})$**                            | `0.98`             | `1.00`            | `0.02`                                | High (≤ 0.05)   | Slight Underconfidence     |
| **Entropy ($\Delta S$)**                           | `0.12`             | `1.15`            | `1.03`                                | Moderate        | Underestimated Risk        |
| **Impact**                                         | `94.00`            | `94.00`           | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Cost**                                           | `1.50`             | `1.27`            | `0.23`                                | High (≤ 1.0)    | Highly Accurate            |
| **Learning Value**                                 | `4.50`             | `4.50`            | `0.00`                                | Exact           | Perfectly Calibrated       |
| **Expected Value — Clean (without bugs)**          | `92.83`            | `94.64`           | `1.81`                                | High            | Conservative Underestimate |
| **Expected Value — Observed (with bugs included)** | `92.83`            | `94.64`           | `1.81`                                | High            | Conservative Underestimate |
| **Bug EV Drag**                                    | `0.00`             | `0.00`            | `0.00`                                | -               | Drag Penalty               |

---

## 2. Mathematical Derivations & Calibration Errors

- **Success Probability Error:** $|0.98 - 1.00| = 0.02$
- **Entropy Error:** $|0.12 - 1.15| = 1.03$
- **Impact Error:** $|94.00 - 94.00| = 0.00$
- **Cost Error:** $|1.50 - 1.27| = 0.23$
- **Learning Value Error:** $|4.50 - 4.50| = 0.00$
- **Expected Value Realization:**
  $$EV_{\text{pred}} = 0.98 \times 94.0 + 0.5 \times 4.5 - 0.3 \times 0.12 - 1.50 = 92.83$$
  $$EV_{\text{actual}} = EV_{\text{clean}} = 1.00 \times 94.0 + 0.5 \times 4.5 - 0.3 \times 1.15 - 1.27 = 94.64$$
  $$EV_{\text{with\_bugs}} = 1.00 \times 94.0 + 0.5 \times 4.5 - 0.3 \times 1.15 - 1.27 = 94.64$$
  $$\text{Bug EV Drag} = round(EV_{\text{clean}} - EV_{\text{with\_bugs}}, 2) = 0.00$$ $$\Delta EV = +1.81$$

---

## 3. Entropy Factor Breakdown

- **State Surface Area (SSA):** Predicted `0.6` vs Observed `3.7` (11 files modified).
- **Irreversibility (IRR):** Predicted `0.0` vs Observed `0.0` (Zero destructive or stateful changes).
- **Conflict Likelihood (CL):** Predicted `0.1` vs Observed `0.0` (Clean sequential branch merges).
- **Sandbox Escape Risk (SER):** Predicted `0.0` vs Observed `0.0` (Zero security exceptions).
- **Novelty (NOV):** Predicted `0.4` vs Observed `0.4` (Standard calibration reporting schema).

---

## 4. Calibration Assessment

Plan `P-1795401489-ANA-G4A` executed with minimal error ($p\_success\_error = 0.02$, $cost\_error = 0.23$). The
calibration step successfully completed the execution lifecycle and delivered verified post-execution analysis.

---

## 5. Touch Set Accuracy

- **Precision (declared entries the diff touched):** `100.0%`
- **Recall (changed files the touch set covered):** `100.0%`

Changed files outside the touch set:

- none

Declared entries the diff did not touch:

- none
