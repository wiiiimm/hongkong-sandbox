// normalize-pr-title.js
// Reusable PR-title → Conventional Commits normaliser, called from a
// github-script step (see pr-title-manager.yml). Pure + unit-testable.

const TYPES = [
  'feat', 'fix', 'docs', 'style', 'refactor',
  'perf', 'test', 'build', 'ci', 'chore', 'revert',
];

// A valid Conventional Commit header: type(scope)!: subject
const CONVENTIONAL = new RegExp(`^(${TYPES.join('|')})(\\([^)]+\\))?!?: .+`);
// Case-insensitive variant — to detect a title that IS conventional but mis-cased
// (e.g. "Feat: …"), so we just fix the case instead of double-prefixing it.
const CONVENTIONAL_I = new RegExp(`^(${TYPES.join('|')})(\\([^)]+\\))?!?: .+`, 'i');

// Human branch prefix → Conventional type. NOTE: agent/bot prefixes (claude/,
// cursor/, codex/, codegen-bot/, copilot/, dependabot/) are intentionally NOT here
// — their type comes from the PR's (conventional) commits; the branch prefix is
// only a last-resort fallback.
const BRANCH_TYPE = {
  feature: 'feat', feat: 'feat',
  fix: 'fix', bugfix: 'fix', hotfix: 'fix',
  docs: 'docs', chore: 'chore', refactor: 'refactor',
  perf: 'perf', test: 'test', ci: 'ci', build: 'build',
};

const RANK = { feat: 2, fix: 1, perf: 1 }; // release-signalling types; others = 0 (no release)

// Returns the strongest release-signalling type across the commits, plus how each
// commit signals a breaking change — tracked SEPARATELY because they behave
// differently on squash:
//   - bangBreaking (`type!:`): the `!` lives in the header and is LOST when commits
//     collapse into the squash body, so the TITLE must carry it or the release
//     under-bumps (minor/patch instead of major).
//   - footerBreaking (`BREAKING CHANGE:`/`BREAKING-CHANGE:`): a body footer that
//     SURVIVES in the concatenated squash body, so semantic-release still reads it —
//     the title needs no `!`.
// So a title `!` is only required when a break would otherwise be lost:
// `bangBreaking && !footerBreaking`.
function detectFromCommits(commits = []) {
  if (!Array.isArray(commits)) {
    return { type: null, scope: null, breaking: false, bangBreaking: false, footerBreaking: false };
  }
  let best = null;
  let bestScope = null;
  let bestRank = -1;
  let bangBreaking = false;
  let footerBreaking = false;
  for (const c of commits) {
    const msg = c.commit?.message || c.message || '';
    const m = msg.match(/^(\w+)(?:\(([^)]+)\))?(!)?:/);
    const isBang = !!(m && m[3] === '!');
    const isFooter = /^BREAKING[ -]CHANGE:/m.test(msg);
    if (isBang) bangBreaking = true;
    if (isFooter) footerBreaking = true;
    if (m) {
      const t = m[1].toLowerCase();
      if (TYPES.includes(t)) {
        // Rank BANG-breaking commits highest so an injected `!` + its scope come from
        // the SAME commit — else a breaking `fix(api)!:` could mis-attribute the `!`
        // to a higher-type-but-non-breaking `feat(ui):` scope. (A footer break needs
        // no title `!`, so it doesn't drive this attribution.)
        const rank = (isBang ? 100 : 0) + (RANK[t] || 0);
        if (rank > bestRank) {
          bestRank = rank;
          best = t;
          bestScope = m[2] || null;
        }
      }
    }
  }
  return {
    type: best,
    scope: bestScope,
    breaking: bangBreaking || footerBreaking,
    bangBreaking,
    footerBreaking,
  };
}

function detectTypeFromBranch(branchName = '') {
  const prefix = branchName.split('/')[0].toLowerCase();
  return BRANCH_TYPE[prefix] || null;
}

function toSubject(s) {
  s = s.trim().replace(/[.\s]+$/, ''); // drop trailing period/space
  if (s) s = s[0].toLowerCase() + s.slice(1); // conventional: lowercase start
  return s;
}

/**
 * Read-only validation of a PR title + its commits against the squash-merge
 * contract. Pure: returns the problems instead of failing. The same-repo (normalize)
 * workflow path imports and calls this; the fork/bot (validate) path can't check out
 * the PR-modifiable script, so it re-implements the SAME checks INLINE — keep the two
 * in sync. Returns `{ ok, errors }` — `errors` is empty when the title is release-ready.
 *
 * Mirrors the inline fork checks: (1) the title must be a lowercase Conventional
 * Commit (mis-cased `Feat:` doesn't match semantic-release's rules → no release),
 * and (2) a bang-style breaking commit (`feat!:`) must be reflected by a `!` in
 * the title, else the break is lost on squash and under-releases. A
 * `BREAKING CHANGE:` footer survives in the squash body, so it needs no title `!`.
 */
function validatePRTitle(currentTitle, commits = []) {
  const title = (currentTitle || '').trim();
  const errors = [];

  // STRICT (case-sensitive, lowercase types) on purpose — see (1) above.
  const conventional = new RegExp(`^(${TYPES.join('|')})(\\([^)]+\\))?!?: .+`);
  if (!conventional.test(title)) {
    errors.push(
      `PR title must be a lowercase Conventional Commit (e.g. "feat: …") — ` +
      `it becomes the squash commit that drives the release: "${title}"`
    );
    return { ok: false, errors };
  }

  const msgs = (Array.isArray(commits) ? commits : []).map(
    (c) => c.commit?.message || c.message || ''
  );
  const footerBreaking = msgs.some((m) => /^BREAKING[ -]CHANGE:/m.test(m));
  const bangBreaking = msgs.some((m) => /^\w+(\([^)]+\))?!:/.test(m));
  const titleBreaking = /^[a-z]+(\([^)]+\))?!:/.test(title);
  if (bangBreaking && !footerBreaking && !titleBreaking) {
    errors.push(
      `A commit is breaking (\`type!:\`) but the title has no "!" and there's ` +
      `no BREAKING CHANGE footer to survive the squash. Add "!" (e.g. ` +
      `"feat!: …") so the merge cuts a MAJOR release: "${title}"`
    );
  }
  return { ok: errors.length === 0, errors };
}

/**
 * @returns {{ newTitle: string, changed: boolean, reason: string }}
 */
function processPRTitle(currentTitle, commits = [], branchName = '') {
  const title = (currentTitle || '').trim();
  const det = detectFromCommits(commits);

  // The break is LOST on squash only when a `type!:` commit exists AND no
  // `BREAKING CHANGE:` footer survives in the body to carry it. A footer break
  // needs no title `!` — so we mirror validatePRTitle exactly and leave an
  // otherwise-valid title UNTOUCHED when the footer already covers the break.
  const lostBreak = det.bangBreaking && !det.footerBreaking;

  // Inject the breaking `!` only for that lost-break case — else a `feat!:` commit
  // under a `feat: …` title would under-release (minor instead of major) after squash.
  const withBreaking = (header) => {
    if (!lostBreak || /^[A-Za-z]+(\([^)]+\))?!:/.test(header)) return header;
    return header.replace(/^([A-Za-z]+(?:\([^)]+\))?)\s*:/, '$1!:');
  };

  if (CONVENTIONAL.test(title)) {
    const fixed = withBreaking(title);
    return fixed === title
      ? { newTitle: title, changed: false, reason: 'already_valid' }
      : { newTitle: fixed, changed: true, reason: 'breaking_marker' };
  }

  // Conventional except for the type's casing ("Feat: …") → lowercase the type.
  if (CONVENTIONAL_I.test(title)) {
    const fixed = withBreaking(title.replace(/^([A-Za-z]+)/, (t) => t.toLowerCase()));
    return { newTitle: fixed, changed: true, reason: 'case_correction' };
  }

  // Not conventional — synthesise `<type>: <subject>`. Strip any leading
  // "word(scope)!: " first so we never double-prefix (e.g. "WIP: foo", "Update: x").
  const type = det.type || detectTypeFromBranch(branchName) || 'chore';
  const scope = det.scope ? `(${det.scope})` : ''; // keep package scope for monorepos
  const bang = lostBreak ? '!' : ''; // carry the `!` only when a footer won't → major bump
  // Strip ONLY a leading real-type prefix (case-insensitive) so a mis-cased
  // "Feat: x" doesn't double-prefix, while a descriptive "Note: x" keeps its text.
  const stripped = title.replace(
    new RegExp(`^(${TYPES.join('|')})(\\([^)]+\\))?!?:\\s*`, 'i'),
    ''
  );
  const subject = toSubject(stripped || title) || 'update';
  return {
    newTitle: `${type}${scope}${bang}: ${subject}`,
    changed: true,
    reason: 'format_correction',
  };
}

module.exports = { processPRTitle, validatePRTitle, TYPES, CONVENTIONAL };
