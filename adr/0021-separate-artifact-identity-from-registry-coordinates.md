# ADR-0021: Separate Artifact Identity from Registry Coordinates

**Status:** Proposed

**Date:** 2026-08-26

**Related:** [Issue #102](https://github.com/Agent-Card/ai-catalog/issues/102)

**Supersedes if accepted:** The federated AIR requirement in
[ADR-0015](0015-agent-identifier-naming.md)

## Context

Existing registries commonly identify artifacts with native coordinates,
such as a registry namespace and artifact name. When projecting those
records as AI Catalog entries, the catalog operator may have no
publisher-assigned `urn:air` identifier.

Using the registry's domain in `urn:air` is easy, but the current format
defines that domain as the artifact publisher. Requiring the publisher's
domain is portable, but prevents automatic projection when the publisher
has not supplied or authorized an identifier.

The existing model already separates most roles: `publisher` identifies
the artifact publisher, `host` identifies the catalog operator, `url`
locates the artifact, and `extensions` can preserve registry-specific
coordinates.

## Decision

`entry.identifier` identifies the artifact represented by the entry and
remains stable across versions. A publisher-authorized `urn:air`
identifier is also portable across catalog locations. Other
identifier schemes remain valid but have no cross-catalog portability
guarantee. Consumers that do not recognize an identifier scheme treat
the value as opaque. Identifier syntax alone does not verify publisher
identity or establish trust.

The base format does not require a particular identifier scheme. A
globally unique absolute URI is recommended for open or federated use.
An artifact publisher that wants an identifier to be preserved when the
artifact appears in other catalogs should use the AI Catalog-specific
`urn:air` format in a namespace it controls.

A publisher-authorized `urn:air` identifier is one assigned by the
artifact publisher or its authorized delegate, with the artifact
publisher's domain in the `{publisher}` segment.

Catalog projection creates a Catalog Entry from either a source Catalog
Entry in another AI Catalog or a source record in another system. When
incorporating a projected entry for the first time, a catalog operator
selects its identifier by applying these rules in order:

1. If the source contains a publisher-authorized `urn:air` identifier,
   preserve it exactly.
2. Otherwise, the operator may preserve a non-`urn:air` source identifier
   or replace it. Non-`urn:air` identifiers have no guaranteed portability
   across catalogs.
3. When assigning a new identifier, an operator that becomes the artifact
   publisher should use `urn:air` with its own domain in the `{publisher}`
   segment. An operator acting as an authorized delegate should use
   `urn:air` with the delegating publisher's domain in that segment. An
   operator that is neither the artifact publisher nor its authorized
   delegate must use a non-`urn:air` identifier under its own control.

Operating a catalog or aggregating an entry does not make its operator the
artifact publisher.

Changing a previously published primary identifier requires an explicit
migration mechanism, which this decision does not define.

The catalog operator and artifact publisher are distinct roles. An
operator-assigned identifier does not imply that the operator published
the artifact.

A catalog operator may retain replaced source identifiers or source-system
coordinates. When retained, they should be stored in a namespaced entry
extension. They do not affect catalog uniqueness or establish publisher
identity, trust, or equivalence with another identifier.

## Consequences

- Publisher-authorized `urn:air` identifiers are preserved across
  catalogs and mirrors.
- Non-`urn:air` identifiers remain valid, but catalog operators may preserve
  or replace them.
- Legacy records can be projected without publisher enrollment by using
  an operator-assigned identifier.
- Two catalog operators may assign different identifiers to the same
  artifact when no publisher-authorized `urn:air` identity is available.
  The model does not claim equivalence it cannot establish.
- No new core field is added; source-system coordinates use `extensions`.
- Generic aliases and primary-identifier migration remain future work.

## Alternatives Considered

Always using a registry-domain `urn:air` was rejected because it makes the
registry appear to be the artifact publisher under the current format.

Requiring a publisher-domain `urn:air` was rejected as a universal rule
because it makes automatic projection depend on publisher enrollment.

Adding `aliases`, `nativeIdentifier`, or `identifiers[]` was deferred
because source-system coordinates do not necessarily assert logical
identity equivalence, and `extensions` is sufficient for the immediate
use case.
