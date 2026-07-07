#!/bin/bash
# "Build-Skip Gate" — Vercel's "Ignored Build Step". Wire it up via vercel.json:
#   { "ignoreCommand": "bash ../../scripts/vercel-ignore.sh" }   # monorepo app
# or Project Settings → Git → Ignored Build Step.
#
# Vercel convention (NOTE the inversion): exit 1 = BUILD, exit 0 = SKIP.
#
# Goal: deploy a PREVIEW on every feature-branch push, but on `main` deploy ONLY
# a release commit (from semantic-release) or an explicit marker — so a normal
# merge to main does NOT ship to production.
set -euo pipefail

BRANCH="${VERCEL_GIT_COMMIT_REF:-$(git branch --show-current 2>/dev/null || true)}"
# Fail CLOSED: if git can't read the message, an empty MSG falls through to the
# main-branch skip below. (A raw failure under `set -e` would exit non-zero, which
# Vercel reads as BUILD — shipping prod on a git error. Don't let that happen.)
MSG="$(git log -1 --pretty=%B 2>/dev/null || true)"
echo "Branch: $BRANCH"
echo "Commit: ${MSG%%$'\n'*}"

# Explicit skip on any branch.
if [[ "$MSG" == *"[skip-deploy]"* ]]; then echo "[SKIP] skip marker"; exit 0; fi

# Feature branches -> always build (preview deployments).
if [[ "$BRANCH" != "main" ]]; then echo "[BUILD] preview branch"; exit 1; fi

# --- On main: strict. Only release commits or an explicit deploy marker. ---
if [[ "$MSG" == *"[deploy]"* ]]; then echo "[BUILD] deploy marker"; exit 1; fi

# semantic-release commit. Match BOTH flavors, and REQUIRE a SemVer version so a
# human "chore(docs): release notes for v2" can't accidentally trigger prod. The
# version is anchored on the RIGHT (end-of-string or whitespace) so a STABLE
# X.Y.Z ships but a prerelease like "1.2.3-next.1" / "1.2.3-beta.2" does NOT reach
# prod (semantic-release `next`/`beta` channels must stay off production):
#   single-package: "chore(release): 1.2.3"            (release is the scope)
#   monorepo:       "chore(my-app): release 1.2.3 …"   (release follows the colon)
if [[ "$MSG" =~ ^chore\(release\):\ v?[0-9]+\.[0-9]+\.[0-9]+($|[[:space:]]) ]] \
   || [[ "$MSG" =~ ^chore\(.+\):\ release\ v?[0-9]+\.[0-9]+\.[0-9]+($|[[:space:]]) ]]; then
  echo "[BUILD] release commit"; exit 1
fi

# Monorepo: also build when a dependency package released. Keep the SAME anchored
# SemVer requirement so a non-release "chore(shared-lib): prep release notes"
# can't trigger prod. Replace the scopes with your shared packages, e.g.:
# if [[ "$MSG" =~ ^chore\((shared-lib|design-system)\):\ release\ v?[0-9]+\.[0-9]+\.[0-9]+($|[[:space:]]) ]]; then exit 1; fi

echo "[SKIP] main, non-release commit"
exit 0
