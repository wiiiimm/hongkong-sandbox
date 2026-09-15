# Shared agent-session reservations (HKS-217 / HKS-218)

Use this layer before two AI sessions work on overlapping model resources. The job queue protects one job ID; job IDs include the batch. Reservations additionally protect stable source keys **across all batches and devices** using the pinned `astra-modelling` Neon branch. They do not run modelling, alter inventory, publish assets, or change completed job results.

## Identity and scope

Use the exact same canonical key for the same source part everywhere, for example `building:landsd/123456:0`. Building keys must include the complete `OBJECTID:PART` source UID; the CLI rejects omitted part suffixes rather than guessing `:0`, and rejects leading-zero aliases such as `001:00`. Never put a batch name, local path, device, source revision, or session name into the resource key. A landmark with multiple known source parts should reserve every part in one group. Different aliases must resolve to those same source IDs before claiming. Missing or ambiguous identities cannot safely acquire an invented equivalent key.

The `--owner` is an explicit, unique AI-session identity (include device/session UUID). `--batch` is optional description only. A claim of 1–1000 sorted distinct keys is atomic: either every resource is claimed, or none is. Conflicts identify owner, batch, heartbeat, and expiry. Different resource groups can process in parallel; a brief database advisory lock serialises metadata changes, not processing.

## Normal workflow

From the repository root, using the existing pinned-branch `.env.modelling` and installed requirements:

```sh
python source-scripts/city/shared-modelling/reservations.py migrate
python source-scripts/city/shared-modelling/reservations.py claim \
  --owner mac-studio-session-unique-id --batch landmark-pass \
  --resource building:landsd/123456:0 --resource building:landsd/123457:0 \
  --ttl 1800 --lease-file /tmp/astra-session-lease.json
python source-scripts/city/shared-modelling/reservations.py check \
  --lease-file /tmp/astra-session-lease.json
python source-scripts/city/shared-modelling/reservations.py heartbeat \
  --lease-file /tmp/astra-session-lease.json --ttl 1800
python source-scripts/city/shared-modelling/reservations.py release \
  --lease-file /tmp/astra-session-lease.json
```

A local lease receipt contains ownership metadata, not database credentials. Keep it out of Git and use a different path for each reservation. The CLI refuses to overwrite an existing receipt. Heartbeats use its token and owner; the server determines current resources and expiry, so stale timestamps in the file are harmless.

Default lease is 30 minutes, with an explicit 1–3600 second limit. An actively working agent should heartbeat at least every five minutes. A crashed or disconnected session stops renewing and its claims expire automatically. Ordinary `claim` then reclaims them; no override is necessary. Do not run a detached heartbeat forever after the AI session has stopped, because that defeats recovery. For a concrete processing command, use the supervised wrapper below; a manual AI session still renews at checkpoints and otherwise expires. Session/group records and events are retained without automatic deletion, exceeding the required 24-hour history.

`check`, `heartbeat`, or `release` exits 2 if the receipt no longer owns the complete live group. **Stop all affected work when this happens.** A group heartbeat renews every member together or none. Release requires the current owner/token of the complete, unexpired group. Every acquisition has a fresh UUID and monotonically increasing per-resource generation; expired or replaced receipts cannot renew or release the newer owner even when owner names are reused.

## Automatic heartbeat for one supervised command

```sh
python source-scripts/city/shared-modelling/reservations.py run \
  --lease-file /tmp/astra-session-lease.json -- \
  python path/to/approved-processing-script.py
```

The wrapper atomically verifies/renews ownership before launching the command in a separate process group. It renews every five minutes only while that child is alive, without any AI calls. Completion releases the reservation and returns the command exit code. Failed renewal or lost ownership stops the process group, including descendants; SIGTERM is followed by SIGKILL after two seconds if necessary. Database renewal subprocesses have a 20-second timeout, leaving a large margin inside the 30-minute lease. No command starts when initial ownership cannot be verified. A command whose root exits cannot leave its ordinary descendants running under the wrapper.

The wrapper handles normal interrupt/termination signals, but cannot guarantee cleanup after its own SIGKILL, machine failure, or a child deliberately escaping its process group. Such workers must still enforce job ownership before shared publication. Do not detach this wrapper to keep an otherwise abandoned manual AI session alive. Use it only for an explicitly selected, concrete command; no background forever-heartbeat service is installed. Current process-group supervision supports macOS and Linux.

## Missing-agent recovery and deliberate takeover

For a missing agent, first inspect server-clock expiry. If a live lease must be overridden, inspect and save the exact intended scope:

```sh
python source-scripts/city/shared-modelling/reservations.py status \
  --resource building:landsd/123456:0 --resource building:landsd/123457:0 \
  --output /tmp/astra-reservation-before.json
python source-scripts/city/shared-modelling/reservations.py takeover \
  --owner replacement-session-unique-id \
  --resource building:landsd/123456:0 --resource building:landsd/123457:0 \
  --expected-file /tmp/astra-reservation-before.json \
  --reason 'User requested recovery after the original session stopped responding' \
  --lease-file /tmp/astra-replacement-lease.json
```

Takeover is an explicit operator action, never automatic or inferred from slow work. It checks the expected token of **every requested key** (including null for an absent key) against current ownership in one transaction. If any token changed, it changes nothing and reports `ownership-changed`; inspect the new owner rather than blindly retrying. Simultaneous takeovers from one snapshot yield only one winner. Expiry/renewal alone does not change identity; a new reservation always changes the token.

The audit table `astra_modelling.reservation_events` records claims/reclaims, releases, and takeovers with the actor, server time, previous owners/tokens/generations, new token, resource scope, and override reason. The implementation appends events and never rewrites them; this is an operational audit, not tamper-proof storage against a privileged database user. Heartbeat timestamps remain in `reservation_groups`.

Taking over part of a group invalidates the previous group's ownership checks and heartbeats. Its untouched members keep their original expiry. Reclaim or explicitly take over those members if needed; do not assume they were transferred too.

## Limits and agent contract

These are **cooperative reservations**, not authentication, filesystem locks, or a transaction spanning Neon and R2. An owner label and receipt token are coordination metadata; trusted agents already share database access. An old process can still write local files after losing its lease. Use separate worktrees/output directories, immutable attempt-specific artefact keys, and verify current ownership immediately before applying shared changes or publishing results. A check followed by a write still has a race unless that publication path enforces the token atomically. Do not claim that this layer alone fences arbitrary file or object-store writes.

The CLI does not automatically wrap every existing script or reserve source-code files. Both sessions must adopt the same resource keys and reservation workflow. Keep existing job tokens and immutable result handling: session reservations complement job leases rather than replacing them. End a session by releasing its group; it can also be left to expire if the process crashes.

## Python API

- `claim(owner, resources, ttl=1800, batch=None)` → `{ok, reservation}` or `{ok: false, error: reserved, conflicts}`.
- `status(resources=None, owner=None)` → resource ownership rows and `expectedTokens` snapshot.
- `owns(receipt)` → whether the whole group is still owned and unexpired.
- `heartbeat(receipt, ttl=1800)` / `release(receipt)` → explicit success or `lease-lost`.
- `takeover(owner, resources, expected_tokens, reason, ttl=1800, batch=None)` → all-or-nothing compare-and-swap replacement.

No automatic migration runs during claims. `migrate` only creates versioned reservation tables/indexes in `astra_modelling`; it never modifies the public schema or original jobs/inventory schema.

## Verification

```sh
python -m unittest discover -s source-scripts/city/shared-modelling -p 'test_reservation*.py' -v
MODELLING_INTEGRATION_TEST=1 python -m unittest discover \
  -s source-scripts/city/shared-modelling -p test_reservations.py -v
```

Supervisor tests cover child completion/failure, periodic heartbeat, bounded database timeouts, refusal to launch without ownership, lost-lease termination, orphan descendants, and SIGTERM-ignoring children. Live API and CLI supervisor smoke checks have also completed and released unique fixture groups on the pinned Neon branch.

Opt-in tests connect through the pinned branch guard. They use unique `reservation-test:<uuid>` keys (and one deliberately impossible large numeric building UID for canonical-key verification) and test concurrent cross-batch claims, partial conflict rollback, expiry/reclaim, stale tokens, takeover audit, lost-member group heartbeat, and simultaneous compare-and-swap recovery. They release their still-owned fixtures without deleting shared data or audit history.
