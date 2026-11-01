# half-hour-clock

Public dispatch clock for the private `pvhp-optimizer` heat-pump controller.
GitHub's own `schedule:` trigger fires only ~5-6 times/day for frequent crons (2026),
so this repo provides a reliable clock using GitHub-only features.

## Cadence (Europe/Warsaw) — aligned with `pvhp.tick_schedule`

| Period | Dispatch `pvhp-tick` |
|--------|----------------------|
| **06:00–21:59** | every **:00** and **:30** (~32/day) |
| **22:00–05:59** | only **:00** at **22, 00, 02, 04** (~4/night) |

The relay chain still wakes ~every 30 min (public repo, free minutes), but **pvhp-tick is
not dispatched** on skipped slots (e.g. night :30, 01:00, 03:00) — that saves **private**
Actions minutes.

## How it works
- `relay.yml` (workflow_dispatch only): environment `half-hour` wait **24 min** (unbilled),
  align to **:00 / :30 Warsaw**, dispatch successor, then **`dispatch_gate.py`** decides
  whether to dispatch `pvhp-tick.yml` in the private repo (`PVHP_DISPATCH_TOKEN`).
- `kick.yml` (cron `17 */2 * * *`): restarts the relay chain if it died; fails if the
  private tick has not run for **>2.5 h** (covers 04:00→06:00 gap). Until
  `PVHP_DISPATCH_TOKEN` is set it only warns.
- Public-repo relay minutes are free; the private repo pays ~**1 min per dispatched tick**
  (~**36/min/day** target ≈ **1080/month**).

## Secrets
- `PVHP_TARGET_REPO` = owner/name of the private repo (secret so it is masked in logs).
- `PVHP_DISPATCH_TOKEN` = fine-grained PAT: owner NXTRSS, only `pvhp-optimizer`,
  Repository permissions -> Actions: Read and write. Set by the owner.

## Start the chain (once, after the token is set)
    gh workflow run relay.yml -R NXTRSS/half-hour-clock --ref main
First tick may be dispatched on the next cadence slot (~24-30 min).

## Check
    gh run list -R NXTRSS/half-hour-clock -w relay.yml -L 5
    gh run list -R NXTRSS/pvhp-optimizer -w pvhp-tick.yml -e workflow_dispatch -L 5

## Stop
    gh workflow disable relay.yml -R NXTRSS/half-hour-clock   # stops the chain
    gh workflow disable kick.yml  -R NXTRSS/half-hour-clock   # stops auto-restart
    gh run list -R NXTRSS/half-hour-clock -w relay.yml --json databaseId,status \
      --jq '.[]|select(.status!="completed")|.databaseId' | xargs -n1 gh run cancel -R NXTRSS/half-hour-clock
Re-enable with `gh workflow enable ...` and start again as above.

## Notes
- Keep `.github/scripts/dispatch_gate.py` in sync with `pvhp-optimizer/pvhp/tick_schedule.py`.
- Any commit that edits `.github/workflows/*` must be followed by a non-workflow commit
  (GitHub bug: community discussion #185024), otherwise kick's schedule may not register.
- Public repos disable scheduled workflows after 60 days without commits; that only affects
  `kick.yml` (relay has no schedule). Re-enable it manually if GitHub emails about it.
