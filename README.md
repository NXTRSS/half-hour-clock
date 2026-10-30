# half-hour-clock

Public dispatch clock for the private `pvhp-optimizer` heat-pump controller.
GitHub's own `schedule:` trigger fires only ~5-6 times/day for frequent crons (2026),
so this repo provides a reliable ~30-min clock using GitHub-only features.

## How it works
- `relay.yml` (workflow_dispatch only): each run's job uses environment `half-hour`
  (wait timer **24 min**, not billed, no runner held), then aligns to the next :04 / :34 UTC,
  dispatches its own successor with `GITHUB_TOKEN`, and dispatches `pvhp-tick.yml` in the
  private repo with `PVHP_DISPATCH_TOKEN`. `concurrency: relay` keeps one chain.
- `kick.yml` (cron `17 */2 * * *`): restarts the relay chain if it died; fails loudly if the
  private tick has not run for >60 min. Until `PVHP_DISPATCH_TOKEN` is set it only warns.
- Public-repo minutes are free; the private repo pays ~1 min per tick (~1,490 min/month).

## Secrets
- `PVHP_TARGET_REPO` = owner/name of the private repo (secret so it is masked in logs).
- `PVHP_DISPATCH_TOKEN` = fine-grained PAT: owner NXTRSS, only `pvhp-optimizer`,
  Repository permissions -> Actions: Read and write. Set by the owner.

## Start the chain (once, after the token is set)
    gh workflow run relay.yml -R NXTRSS/half-hour-clock --ref main
First tick is dispatched ~24-30 min later.

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
- Any commit that edits `.github/workflows/*` must be followed by a non-workflow commit
  (GitHub bug: community discussion #185024), otherwise kick's schedule may not register.
- Public repos disable scheduled workflows after 60 days without commits; that only affects
  `kick.yml` (relay has no schedule). Re-enable it manually if GitHub emails about it.
