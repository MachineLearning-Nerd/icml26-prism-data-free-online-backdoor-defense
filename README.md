# PRISM: Source-Pinned Reproduction Audit

This repository tracks a source-pinned, claim-by-claim audit of **PRISM**:

> **From Internal Diagnosis to External Auditing: A VLM-Driven Paradigm for Data-Free Online Backdoor Defense**

The repository is intentionally evidence-first. It does **not** currently contain a full PRISM implementation or a completed reproduction of the paper's benchmark results.

| Resource | Link |
| --- | --- |
| Paper | [arXiv:2601.19448](https://arxiv.org/abs/2601.19448) |
| OpenReview submission | [l3yzuHKpNe](https://openreview.net/forum?id=l3yzuHKpNe) |
| Authors' reference implementation | [binyxu/PRISM](https://github.com/binyxu/PRISM) |

## Current status

**Overall result: inconclusive.** The completed work is a source-pinned CPU feasibility audit only. The literal CIFAR-10/ImageNet backdoor benchmarks and frozen VLM auditors were not executed under this repository's local-only compute policy.

The current policy allows local CPU and a local GTX 1050 only. It does not allow Hugging Face upgrades, remote compute, paid compute, or jobs. The machine-readable state records this as `publication_allowed: false`.

The next repository action is to independently review the Claim 1 source audit and then run a bounded Cornish–Fisher toy experiment.

## What the paper does

PRISM proposes an online, data-free backdoor defense that separates the defense signal from a potentially compromised victim model. For each incoming image, it runs two streams:

1. The suspicious/victim model produces the task prediction and logits.
2. A frozen vision-language model (VLM) acts as an external semantic auditor.

The auditor is adapted online without the original training set:

- **Hybrid VLM Teacher:** combines fixed text-anchor similarities with visual class prototypes refined from the test stream.
- **Adaptive Router:** compares the VLM's support for the victim prediction with the strongest competing class using an exponential logit margin.
- **Cornish–Fisher thresholding:** estimates a per-class threshold from the running mean, standard deviation, and skewness of those margins.
- **Selective online update:** updates prototypes and statistics only for samples accepted as clean, using cumulative moving averages rather than a replay buffer.

In the paper's design, a sample whose VLM margin passes the adaptive threshold keeps the victim prediction. A sample that fails the gate is routed to the VLM prediction instead.

The central method quantities are:

```text
S_VLM = λ · Sim(image, visual prototypes)
         + (1 − λ) · Sim(image, text anchors)

Δ = exp(S_VLM[victim prediction]
        − max(S_VLM[other classes]))

τ_k = μ_k + [ζ + γ_k / 6 · (ζ² − 1)] · σ_k
```

Here, `μ_k`, `σ_k`, and `γ_k` are online statistics for class `k`; the paper reports `ζ = -2` as its default setting.

## What this repository contains

| Path | Purpose |
| --- | --- |
| `AUTONOMOUS_STATE.json` | Machine-readable phase, compute policy, next action, and overall Claim 1 outcome |
| `STATUS.md` | Short human-readable status summary |
| `contract/live_claims.json` | Six paper claims tracked with an explicit verification status |
| `evidence/source/arxiv-2601.19448.pdf` | Pinned paper PDF |
| `evidence/source/arxiv-2601.19448.tar.gz` | Pinned arXiv source archive |
| `evidence/source/SHA256SUMS` | Checksums for the pinned source artifacts |
| `outputs/claim1_source_audit/summary.json` | Result of the completed source/CPU feasibility audit |
| `tests/test_contract.py` | Minimal checks for the state and claim contract |

The empty `contract/`, `evidence/`, `outputs/`, and `tests/` directories are part of the evidence layout. They are not separate implementations.

## Branch inventory

Only one branch currently exists:

| Branch | Purpose | Current state |
| --- | --- | --- |
| `main` | Source-pinned PRISM reproduction audit | Contains the initial audit, claim contract, source artifacts, and the inconclusive Claim 1 summary |

There are no feature, experiment, or results branches in this repository at the time of this audit. The current branch points to the initialization commit `29a8c3a` (`Initialize source-pinned PRISM reproduction audit`).

## Claim ledger: what each claim means and how it is produced

The following claims come from `contract/live_claims.json`. They describe claims made by the paper; they are not independent results produced by this repository. Every claim is currently marked `unverified` in the contract.

| ID | Paper claim | How the paper produces the claim | Evidence currently in this repo | Status |
| --- | --- | --- | --- | --- |
| C1 | On CIFAR-10, PRISM reports average ASR of `0.8%` across 11 attack types, with `93.2%` clean accuracy versus `92.0%` undefended. | Run the PRISM and baseline defenses on the CIFAR-10 attack suite, measure clean accuracy (CA) on clean samples and attack success rate (ASR) on triggered non-target samples, then aggregate the rows reported in Table 1. | Source-pinned paper and a source audit only; no VLM/backdoor benchmark output. | **Unverified** |
| C2 | The evaluation covers 17 datasets, 11 attack types, and six VLM backbones. | Execute the paper's dataset × attack × auditor matrix and record CA/ASR for each configuration, as described in Section 5 and Table 2. | No experiment manifest or result matrix is present. | **Unverified** |
| C3 | For clean-image attacks FLIP and GCB, PRISM reports ASR of `1.1–4.4%`, while listed baselines reach `28.5–100%`. | Reproduce the FLIP and GCB attack streams, evaluate PRISM and each baseline under the same victim/data-free setup, and compare the clean-image rows in Table 1. | No clean-image attack run or metric output is present. | **Unverified** |
| C4 | For dynamic attacks WaNet and BPP, PRISM reports ASR below `1%`, while some baselines reach `43–99%`. | Reproduce the WaNet and BPP triggered streams, compute ASR against the target label, and compare all methods under the paper's evaluation protocol. | No dynamic-attack run or metric output is present. | **Unverified** |
| C5 | The Adaptive Router uses a Cornish–Fisher correction and reports `ζ = -2` as a cross-dataset optimum. | Implement the hybrid VLM margin, maintain per-class `μ`, `σ`, and `γ`, compute the corrected threshold, and compare the sensitivity/ablation results with the paper's Section 4, Figure 5, Figure 8, and ablation tables. | The paper source and claim contract are pinned; no implementation or toy result is present. | **Unverified** |
| C6 | PRISM is external to the victim model and does not require victim weights or original training data. | Inspect the threat model and method implementation/configuration to verify that the VLM auditor is frozen and that adaptation uses only the unlabeled inference stream. | The repository records the paper's design claim, but has not independently validated an implementation. | **Unverified** |

### Metric definitions used by the paper

- **Clean accuracy (CA):** the fraction of clean samples classified correctly.
- **Attack success rate (ASR):** the fraction of triggered, non-target samples classified as the attacker's target label.

The paper's main CIFAR-10 setup uses target label `0`, a `50%` poison rate for clean-label attacks, and a `5%` poison rate for other listed attacks. Its default configuration uses a PreActResNet18 victim, CLIP auditor, batch size `256`, prototype-fusion weight `0.5`, and a one-batch unlabeled warm-up window. These are paper protocol details, not evidence that this repository has run those experiments.

## Reproduction boundary

It is important to distinguish three different statements:

1. **Paper-reported:** a number or conclusion appearing in the PRISM paper.
2. **Source-audited:** an artifact or method description has been pinned and inspected.
3. **Reproduced here:** this repository independently ran the relevant experiment and stored verifiable output.

At present, this repository supports the second category. It does not yet support the third category for the six claims above. The current audit explicitly reports:

```text
verdict: inconclusive
scope: source-pinned CPU feasibility audit only
benchmark executed: no VLM/backdoor benchmark
```

## Verification commands

From the repository root:

```bash
python3 -m pytest -q tests/test_contract.py
shasum -a 256 evidence/source/arxiv-2601.19448.pdf
shasum -a 256 evidence/source/arxiv-2601.19448.tar.gz
```

The expected artifact hashes are recorded in `evidence/source/SHA256SUMS`.

## Citation

If this audit or the paper is useful, please cite the paper:

```bibtex
@misc{xu2026internaldiagnosisexternalauditing,
  title={From Internal Diagnosis to External Auditing: A VLM-Driven Paradigm for Data-Free Online Backdoor Defense},
  author={Binyan Xu and Fan Yang and Xilin Dai and Di Tang and Kehuan Zhang},
  year={2026},
  eprint={2601.19448},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2601.19448}
}
```

## Thank you

Thank you to **Binyan Xu, Fan Yang, Xilin Dai, Di Tang, and Kehuan Zhang** for making the PRISM paper and reference implementation available. The paper provides a useful starting point for studying external semantic auditing, data-free test-time defense, and reproducibility of security claims.
