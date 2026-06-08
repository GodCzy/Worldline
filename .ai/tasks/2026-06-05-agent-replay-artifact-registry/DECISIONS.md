# Decisions

- Keep artifact storage file-backed in the existing run ledger to avoid schema churn before the durable storage contract is finalized.
- Require admin access through the existing run router dependency.
- Emit `artifact.registered` events so artifacts become part of the replay timeline instead of a detached export feature.
