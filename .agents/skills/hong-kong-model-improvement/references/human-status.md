# Human model-work status — HKS-215 / HKS-203

Use this presentation contract in reports while preserving the original Neon
states, reasons, immutable evidence, review history and publication guards.
The user needs to know what is done, what has not started, and whether remaining
work needs compute, AI or a personal decision.

| Human status | Use when | Required report detail |
| --- | --- | --- |
| Installed | Current source form is integrated and verified in the stated viewer/branch | Installation evidence; distinguish preview from production when relevant |
| To do | Improvement work on this form has not started | Count within the original scope |
| Held for human decision | Progress depends on an actual unanswered user choice or approval | Exact question, why it is required and which forms are affected |
| Held for AI processing | Evidence identifies a need for per-model AI modelling or architectural judgement | Specific reason; AI work remains paused under the current user constraint |
| Held for unknown state | The blocker or next responsible action cannot yet be classified, or current state cannot be verified | What is unknown and the next diagnostic step |
| In process | Work started, is unfinished, and the next action is known scripted/compute work | Queued or running; next action and meaningful blocker/reason |

## Mapping rules

1. Verify the current batch, source identity/hashes and installed evidence first.
   Stale approval, a completed preparation job or an old asset is not installation.
2. Use one human status per source form. Counts must partition the original batch;
   an intermediate subset such as 61 of 200 must never replace the denominator.
3. Reuse detailed technical states as input. `pending`, `held`, `source-unavailable`,
   `identity-unresolved` and failed checks do not map to AI or human holds by name.
   Inspect the recorded reason and next step.
4. Source retrieval, additional compute, writing/fixing scripts, comparing native
   terrain, checking actual support geometry and deterministic identity lookup are
   scripted follow-up. Started forms with those next steps are **In process —
   queued/running**. A waiting queue is not proof a worker is currently executing.
5. AI-assisted software work stays in the compute/script route. **Held for AI
   processing** specifically means AI must work on the model or make the unresolved
   architectural judgement. No automatic AI fallback or per-model review loop.
6. **Held for human decision** requires a concrete choice the user must make.
   Existing delegated import/skip authority is sufficient for routine decisions;
   do not manufacture a new approval requirement from a technical failure.
7. If there is not enough evidence to establish the next route, use **Held for
   unknown state** and name the investigation. Do not assume AI is required, or
   promise a compute-only resolution before that has been demonstrated.
8. When multiple confirmed dependencies coexist, show one primary state and list
   the others as details. An unanswered human decision takes priority over AI;
   an established AI requirement takes priority over ordinary compute. Unknown
   additional details do not hide a known human/AI requirement. No known special
   requirement plus a known scripted next step remains In process.
9. Mapping is presentation only. It does not waive held acceptance checks, start
   an AI job, change the source ledger, mark a model installed, or complete a region.

## Report format

Start with a compact six-stage count table, including zeroes for human/AI holds so
absence of a decision requirement is explicit. Follow with the next work category:
**compute/scripts**, **AI**, **your decision**, or **unknown**, and the concrete next
step. Keep detailed terrain/identity/runtime flags available underneath; do not
make the user interpret internal pipeline terminology. Indicate the data checkpoint
and original scope. Mention an active worker only when its job/lease is verified.

For the first 200 government forms after the recorded pending-context pass:
**2 Installed; 198 In process — queued scripted investigation; 0 in the other four
stages**. Evidence identifies further terrain/source/support/identity checks; no
per-model AI requirement or user decision has been established. This is not a
claim that all 198 can already be resolved by existing scripts or will be installed.
Use fresh evidence for later batches rather than copying these example counts.
