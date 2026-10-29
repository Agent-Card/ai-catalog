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

Producers need not serialize the JSON in canonical form. Consumers may
reject duplicate member names or retain only the last occurrence of each
name after JSON escape processing, including when preparing data for signing
or verification. They need not perform a separate duplicate-detection pass.
The value supplied to JCS must still satisfy its input requirements, and
consumers must use the same resulting value for verification and subsequent
processing of authenticated claims.

## Rationale

A common input requirement lets conforming entries and complete catalogs be
embedded in other catalogs without introducing JCS incompatibilities.
Producers need not predict whether another catalog will later sign or hash
their content. This producer obligation does not require every consumer to
certify the original JSON text.

Ordinary JSON parsers may discard duplicate names before a verifier receives
the parsed value. Retaining the last occurrence, as in
[ECMAScript's `JSON.parse()`](https://tc39.es/ecma262/multipage/structured-data.html#sec-parsejson),
gives consumers a deterministic interpretation and matches
[JWT's consumer parsing policy](https://www.rfc-editor.org/rfc/rfc7519.html#section-4).

## Consequences

- Values that violate JCS input requirements are nonconforming even in
  unsigned catalogs, including in extensions and unrecognized members.
- Reserved `additionalSignatures` fields may still contain any JSON type or
  structure, subject to the same input requirements. Their verification
  semantics and signature-payload exclusions are unchanged.
- Duplicate member names remain nonconforming producer output. A consumer
  may reject such input; otherwise, it uses the last occurrence consistently
  for verification and authenticated claims. Conforming documents produce the
  same canonical bytes under either policy.
- This consumer policy relaxes source-message validation compared with
  [RFC 8785, Section 5](https://www.rfc-editor.org/rfc/rfc8785.html#section-5),
  without changing JCS's input-value constraints or serialization rules.
- Whitespace and object-member order in conforming transmitted JSON remain
  unrestricted.
- External artifact content is outside this requirement. An artifact that
  cannot be embedded can still be referenced by URL, with its digest
  computed over the exact retrieved bytes.
- Catalog operators remain responsible for signing their catalogs. This
  requirement removes input incompatibility as an obstacle; it does not
  supply a signature or establish trust.
