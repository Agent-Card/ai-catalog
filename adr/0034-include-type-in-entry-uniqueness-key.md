# ADR-0034: Include `type` in the Catalog Entry Uniqueness Key

**Status:** Proposed

**Date:** 2026-10-15

**Related:** [Issue #59](https://github.com/Agent-Card/ai-catalog/issues/59),
[ADR-0014](0014-media-type-to-type.md),
[ADR-0015](0015-agent-identifier-naming.md),
[ADR-0025](0025-bind-signed-trust-manifests-to-releases.md)

## Context

Issue #59 proposed moving an artifact type segment ahead of the publisher in
`urn:air`, so `urn:air:example.com:skill:code-review` would become
`urn:air:skill:example.com:code-review`. The discussion turned up several
problems with encoding type in the identifier. MCP alone has several artifact
formats (Server Cards, `server.json`, `mcp.json`), so a single `mcp` token
isn't enough to say what an entry is. Categories aren't mutually exclusive, an
agent can be exposed over MCP and a plugin can contain both MCP servers and
skills. A closed type vocabulary needs ongoing governance. String prefix
routing on the URN also opens cross-publisher matching problems, since
`urn:air:skill:acme.com` is a string prefix of
`urn:air:skill:acme.com.attacker.example`. On 2026-10-15 the TSC concluded
there will be no type segment in `urn:air`, and that publishers should use
tags for categorization.

That decision leaves a gap for identifier generation. Uniqueness was
`identifier` alone, or `identifier` plus `version` when a version is present,
so a publisher that exposes the same logical service as both an MCP server and
an A2A agent has to invent a namespace or name suffix purely to satisfy the
uniqueness rule, for example `urn:air:acme.com:agent:finance:mcp` and
`urn:air:acme.com:agent:finance:a2a`. That's the rejected type segment again,
chosen ad hoc by each publisher with no convention a consumer can rely on.

The entry's `type` already carries the artifact format, and ADR-0014 made it
the one place that does. The signed `subject` of a Trust Manifest already
restates `identifier` and `type`, and ADR-0025 added `version`, so a signed
Trust Manifest is already bound to an `(identifier, type, version)` tuple. The
catalog uniqueness rule didn't match what the signature binds.

## Decision

The uniqueness key of a Catalog Entry within a catalog is
`(identifier, type, version)`:

- When `version` is present, the combination of `identifier`, `type`, and
  `version` MUST be unique within the catalog.
- When `version` is absent, the combination of `identifier` and `type` MUST be
  unique within the catalog.
- The `identifier` SHOULD be stable across versions, unchanged from before.

A publisher can list the same `identifier` under more than one `type`, for
example an MCP Server Card and an A2A Agent Card for the same service, without
adding a type token to the identifier. The `urn:air` format is unchanged, and
the `{namespace}` segment stays publisher-defined with no requirement to
encode the artifact type.

The rule applies within a single catalog document. It doesn't change the
cross-catalog identifier preservation rules in [Catalog
Projection](../specification/ai-catalog.md#catalog-projection).

## Consequences

- A publisher can offer one logical artifact in several formats under one
  identifier, so the TSC outcome on #59 holds without forcing publishers to
  invent type suffixes.
- Every catalog that was valid under the old rule is still valid, since adding
  `type` to the key only loosens it.
- Catalog uniqueness now lines up with the signed `subject`, which already
  binds `identifier`, `type`, and `version`.
- Consumers already filter and route entries by `type` (Design Goal 2). A
  consumer that handles a single type sees the same uniqueness it saw before.
- Consumers that key caches, indexes, or latest-version selection on
  `identifier` alone need to add `type` to the key. Grouping by `identifier`
  alone now mixes formats, and a naive latest-version sort can pick an entry
  whose type the consumer can't process.
- An `identifier`, even an unversioned one, no longer resolves to exactly one
  entry. Any reference to an entry from outside the catalog, such as a link, a
  pin, or a future dependency expression (ADR-0002), has to carry `type` as
  well or accept that it resolves to a set of entries.
- The specification doesn't define precedence between types. When a consumer
  supports more than one of the types listed under an identifier, its own
  policy picks between them.
- Latest-version selection and specific-version matching in Multi-Version
  Entries group and match on `identifier` and `type`, and the consumer guide's
  `latest_entries()` example keys on the pair, so an MCP Server Card and an
  A2A Agent Card sharing an identifier don't collapse into one entry.
- The xRegistry mapping produces one Resource per `(identifier, type)` pair,
  since xRegistry can't hold two content types at the same `versionid` of a
  single Resource. The `ai-catalog.identifier` label is no longer unique
  across Resources in a Group.

## Alternatives Considered

A type segment in `urn:air`, as in the original #59 proposal, was rejected by
the TSC on 2026-10-15 for the reasons in Context.

Keeping `identifier` and `version` as the key, and leaving publishers to add a
type-specific namespace or suffix, works today but gives every publisher its
own convention. Consumers can't use it to relate the MCP and A2A forms of the
same service, and it reintroduces the type segment #59 rejected without a
definition in the specification.

An optional `artifactType` or semantic category field, raised by Sam Betts
and Jonathan Hefner on #59, addresses classification and search rather than
uniqueness. It's complementary to this decision and can be added later. The
TSC pointed to tags for categorization in the meantime.

