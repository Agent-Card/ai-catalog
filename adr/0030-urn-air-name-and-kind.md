# ADR-0030: Separate Publisher, Name, and Optional Kind in `urn:air`

**Status:** Proposed

**Date:** 2026-11-06

## Context

[ADR-0015](0015-agent-identifier-naming.md) uses colons for the publisher,
namespace segments, and artifact name. The discussion in
[issue #59](https://github.com/Agent-Card/ai-catalog/issues/59) adds an
optional conceptual kind. Using colons for both namespace segments and an
optional kind would leave their boundary ambiguous.

## Decision

Use `urn:air:{publisher}:{name}[:{kind}]`, where `{name}` has
publisher-defined internal structure and `{kind}` is optional. Publishers
may use slashes, dots, or other characters permitted by URN syntax for
their own namespace conventions, apart from the colon used to delimit
components. For example:

```text
urn:air:acme.com:code-review
urn:air:acme.com:engineering/code-review
urn:air:acme.com:engineering/code-review:skill
urn:air:acme.com:engineering.code-review:skill
```

The publisher assigns the name and optional kind and is responsible for
the uniqueness of the complete identifier. This proposal does not define
a vocabulary of kinds. The entry's `type` continues to describe how to
process the artifact.

For the identifier-derived display-name fallback in
[ADR-0016](0016-displayname-optional.md), use the entire `{name}` verbatim,
without interpreting its internal structure.

## Rationale

Colons separate the three concepts: publisher, publisher-relative name,
and conceptual kind. Treating the name as a single component makes the
optional kind recognizable regardless of the publisher's namespace
conventions.

Both name and kind remain within the namespace-specific string defined
by [RFC 8141 §2](https://www.rfc-editor.org/rfc/rfc8141.html#section-2).

The discussion in issue #59 considered `#kind` and `;kind` suffixes. A
`#kind` suffix is ignored when determining URN equivalence, so it cannot
distinguish otherwise identical identifiers. A semicolon participates in
the identifier but acts as a command separator in Bash when pasted
without quoting. Using a colon to introduce the optional kind avoids both
problems.

URN syntax also permits adjacent colons. A future revision could therefore
add components after an omitted kind by leaving its position empty, as in
`urn:air:acme.com:code-review::future-value`; this proposal does not define
those additional components or empty-kind behavior.
