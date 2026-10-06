# ADR-0030: Require JCS-Compatible Catalog Data

**Status:** Proposed

**Date:** 2026-10-05

## Context

Artifact digests for inline `entry.data` and whole-catalog signatures use
the JSON Canonicalization Scheme (JCS). A downstream catalog operator may
import entries or embed an entire catalog in `entry.data`. Values that
cannot be canonicalized prevent that operator from hashing or signing the
imported content unchanged.

Restricting only inline artifacts or entries would leave the same obstacle
in catalog-root metadata when embedding a complete catalog.

## Decision

Producers MUST ensure that each complete AI Catalog document is valid input
to JCS [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785), including all nested
values, whether or not the catalog is signed. Consumers MAY reject documents
that do not satisfy this requirement. This requirement does not mandate
validation during ingestion.

Producers need not serialize the JSON in canonical form. Existing input
checks for JCS-based signing and verification remain required.

## Rationale

A common input requirement lets conforming entries and complete catalogs be
embedded in other catalogs without introducing JCS incompatibilities.
Producers need not predict whether another catalog will later sign or hash
their content. The requirement applies to producers without adding a
mandatory validation pass for consumers that only use catalogs for discovery.

## Consequences

- Values that violate JCS input requirements are nonconforming even in
  unsigned catalogs, including in extensions and unrecognized members.
- Reserved `additionalSignatures` fields may still contain any JSON type or
  structure, subject to the same input requirements. Their verification
  semantics and signature-payload exclusions are unchanged.
- Whitespace and object-member order in transmitted JSON remain unrestricted.
- External artifact content is outside this requirement. An artifact that
  cannot be embedded can still be referenced by URL, with its digest
  computed over the exact retrieved bytes.
- Catalog operators remain responsible for signing their catalogs. This
  requirement removes input incompatibility as an obstacle; it does not
  supply a signature or establish trust.
