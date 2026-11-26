# ADR-0031: Define a did:web Catalog Profile

**Status:** Proposed

**Date:** 2026-10-05

## Context

SDKs and other consumers need a common rule for verifying that a catalog
was signed by its declared operator. Without that rule, implementations must
define their own relationship between the authenticated signer and Host
Info. The Catalog Profile defines that relationship through exact identity
matching, allowing applications to delegate operator-attribution checks while
retaining their own policies about which operators to trust.

## Decision

Define a `did:web` Catalog Profile by composing the existing `did:web`
Signer Profile with these requirements:

- The signature MUST cover the catalog under the whole-catalog signing
  procedure.
- The catalog MUST contain `host.identifier`, and its value MUST exactly
  equal the authenticated signer identity.

The profile inherits the Signer Profile's root `did:web` identity restrictions,
key authorization, algorithm, and signature-acceptance requirements. It uses
the same `did-web-v1` selector; catalog attribution is an additional check,
not a different signer-authentication procedure.

## Rationale

Exact equality establishes a direct relationship between authenticated
identity and the operator declared in the signed catalog. It requires no
domain-suffix, organizational-ownership, or retrieval-location heuristics.
This follows the composition used by the `did:web` Publisher Profile.

## Consequences

- Consumers can establish that the declared operator signed the catalog.
- This establishes attribution, not the operator's reputation, legal
  identity, or the accuracy of its claims. Consumers retain their own trust
  policies.
- A catalog can be mirrored without changing this attribution. The profile
  does not authenticate a mirror's serving origin as the operator.
- Catalogs without a matching Host Info identifier cannot satisfy this
  profile, even if their signer can be authenticated.
