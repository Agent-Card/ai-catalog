# ADR-0035: Add an Optional Kind Suffix to `urn:air` Identifiers

**Status:** Accepted

**Date:** 2026-11-05

**Related:** [Issue #59](https://github.com/Agent-Card/ai-catalog/issues/59),
[ADR-0015](0015-agent-identifier-naming.md)

## Context

Issue #59 asked for an artifact's kind to be readable from its identifier. On
October 29, 2026 the TSC agreed on an optional suffix after the name, delimited
by `#`, rather than a type segment. However, RFC 8141 requires a fragment to be
ignored for URN equivalence, so `…#mcp` and `…#skill` would be the same URN.

## Decision

The `urn:air` format is:

```text
urn:air:{publisher}{:namespace+}:{name}{;kind}
```

`{namespace}` is optional, as ADR-0015 already described.

This reverses ADR-0015's use of `{namespace}` for artifact types (`mcp`, `skill`,
`agent`). The kind of artifact now belongs in `{kind}`, and `{namespace}` is for
the publisher's own categories. The specification and documentation examples no
longer use type-like namespaces.

The TSC chose `;` by vote at its November 5, 2026 call. As part of the namespace-specific
string, it counts toward URN equivalence, so identifiers that differ only in
`{kind}` are different identifiers. The uniqueness key remains `identifier`
plus `version`.

This specification does not define `{kind}` values or a relationship between
identifiers that share everything but `{kind}`.

## Alternatives Considered

- `#`: Ignored for URN equivalence.
- `+`: Needs percent-encoding in browsers.
- `@`: Reads as a version in package identifiers.
- `:` and `::`: The other options voted on.

## Consequences

- Existing `urn:air` identifiers that do not contain `;` remain valid. That includes
  identifiers with type-like namespaces, which are not disallowed.
- A `{namespace}` or `{name}` can no longer contain `;`.
- Identifiers that use the suffix need quoting in common shells.
