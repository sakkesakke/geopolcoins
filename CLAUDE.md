# geopolcoins.xyz / Human Override

Owner: beginner, answer in simple Dutch with numbered steps and exact button names. "go" = build it all, report after.
Trust rules, facts and git/SQL workflow: the `maiga-ops` skill. Never type passwords, change account security,
put secrets anywhere, or post publicly / spend money without the owner's OK.

Current state and open items (keep it short and up to date after every larger task):

@docs/HANDOFF.md

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- Cloud session (repo cloned after start): the SessionStart hook did NOT run. First command after the clone:
  `bash tools/graphify_session.sh` (~35 s). Check with `ls graphify-out/graph.json`.
- The graph covers js/py/md/yml/java, NOT the ~180 .html pages (3.5 MB). For HTML: `grep -n` first, then Read
  with offset/limit around the hit. Never Read a whole .html file or `cat` it.
- Save tokens: one task per chat (start a new chat for the next task); no subagents unless the owner asks;
  test output via `| tail -20`; no full-page screenshots when one locator check is enough.
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- graphify-out/ is git-ignored (rebuilt locally each session); never commit it.
