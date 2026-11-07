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

Use `urn:air:{publisher}:{name}[:{kind}]`, where `{name}` can include
slash-separated namespaces and `{kind}` is optional. For example:

```text
urn:air:acme.com:code-review
urn:air:acme.com:engineering/code-review
urn:air:acme.com:engineering/code-review:skill
```

The publisher assigns the name and optional kind and is responsible for
the uniqueness of the complete identifier. This proposal does not define
a vocabulary of kinds. The entry's `type` continues to describe how to
process the artifact.

For the identifier-derived display-name fallback in
[ADR-0016](0016-displayname-optional.md), use the portion of `{name}` after
its final `/`, or all of `{name}` if it contains no `/`. All three examples
above yield `code-review`.

## Rationale

Colons separate the three concepts: publisher, publisher-relative name,
and conceptual kind. Slashes express namespaces within the name using
familiar path notation. Different separators make the optional kind
recognizable at any namespace depth.

[RFC 8141 §2.2](https://www.rfc-editor.org/rfc/rfc8141.html#section-2.2)
allows slashes inside the namespace-specific string. Both name and kind
remain within that string.

The discussion in issue #59 considered `#kind` and `;kind` suffixes. A
`#kind` suffix is ignored when determining URN equivalence, so it cannot
distinguish otherwise identical identifiers. A semicolon participates in
the identifier but acts as a command separator in Bash when pasted
without quoting. Using slashes within `{name}` makes a colon available
to introduce the optional kind, avoiding both problems.

## Consequences

Reserving `/` for namespace separation within `{name}` means it can no
longer appear as ordinary content in a non-namespaced name. The previous
format did not reserve or prohibit `/` within names.
