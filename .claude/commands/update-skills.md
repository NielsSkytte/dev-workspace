Update local Microsoft Fabric skills from the upstream git submodule. Run when you want to pick up new skill versions released by Microsoft.

Usage: /update-skills

## Instructions

### Step 1 — Pull the upstream submodule

```bash
git submodule update --remote .claude/vendor/skills-for-fabric
```

Report the new version from `vendor/skills-for-fabric/package.json` vs the previous HEAD.
If already up to date, say so and stop.

### Step 2 — Identify changed upstream skills

For each skill listed in `.claude/vendor/skills-for-fabric/.claude-plugin/marketplace.json`
(all bundles combined), check if a matching folder exists in `.claude/skills/`.

The mapping between vendor skill names and our local folders is 1:1 — e.g.
`vendor/skills/sqldw-authoring-cli/SKILL.md` → `.claude/skills/sqldw-authoring-cli/skill.md`.

For each match: diff the **body** (everything after the closing `---` of the frontmatter) of
vendor vs local. Build a list of skills with changed bodies.

### Step 3 — Show the diff summary

Present a table of skills with changes:

| Skill | Bundle | Change summary |
|---|---|---|
| sqldw-authoring-cli | fabric-authoring | N lines changed |

Ask: "Update all, select specific ones, or skip?"

### Step 4 — Apply updates

For each skill the user confirms:
1. Read the vendor SKILL.md
2. Read our local skill.md — extract the frontmatter block (between `---` markers)
3. Write the updated skill.md: **our frontmatter** (preserving `name:`, `bundle:`, our `description:`) + **vendor body** (everything after vendor's closing `---`)
4. Confirm each file written

### Step 5 — Report

List what was updated, what was skipped, and whether any vendor skills are new (present in
vendor but missing from our `.claude/skills/` — those need manual scaffolding).

## Notes

- Our frontmatter (`name:`, `bundle:`, `description:`) is intentionally different from vendor's — always preserve it
- Custom skills (`bundle: custom`) have no vendor counterpart — never overwrite them
- New vendor skills not yet in our collection should be flagged for manual addition
- The submodule lives at `C:\Dev\.claude\vendor\skills-for-fabric`
