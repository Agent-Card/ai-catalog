# ADR-0028: Open the AI Catalog and Catalog Entry Objects to Unrecognized Members

**Status:** Proposed (exploratory draft; expect iteration)

**Date:** 2026-10-29

## Context

ADR-0012 closed the Catalog Entry schema and routed all custom data to a
dedicated extension object, which ADR-0017 and PR #77 later shaped into the
`extensions` map keyed by URL or reverse-DNS name. The rationale was strict
validation and a single, obvious place for non-standard data.

Since then the normative prose has moved toward openness without the schema
following it:

- Version Handling tells consumers to ignore unrecognized fields.
- The signature sections require unrecognized members to be retained in
  signed payloads, and the catalog snapshot explicitly covers "unknown
  fields".
- The CDDL preamble says the schema "describes recognized members".

Yet the CDDL maps for `AICatalog` and `CatalogEntry` are closed, so the
normative schema rejects exactly the documents the prose tells consumers to
accept. Implementers reading the schema and implementers reading the prose
build different validators.

At the same time, several parties have indicated a desire to describe
entries using conventions this specification does not define. The most
common request is a JSON-LD-style prefix map (`@context`) with namespaced
members at the entry level, so that terms from other vocabularies can sit
beside the core members and be addressed by a flat key. Other uses have come
up too: private annotations in internal catalogs that are never federated,
and shipping a candidate field to gather experience before proposing it.

The TSC does not want to adopt JSON-LD, or any other outside convention, into
the core data model. The question is whether the data model can leave room
for such conventions without endorsing one, and without creating a
dependency on anyone else's specification.

## Decision

The AI Catalog top-level object and Catalog Entry objects are explicitly
open. The CDDL gains `* text => any` on both maps, and a new
*Unrecognized Members* section defines four consumer rules:

1. Consumers MUST NOT reject a document for containing unrecognized members.
2. Consumers MUST NOT derive semantics defined by this specification from
   them.
3. Consumers SHOULD preserve them when republishing, on a best-effort basis.
4. Consumers MUST retain them in signed payloads (already required).

The section also states that any undefined member name may be defined by a
future version with no coordination with outside conventions, that
unrecognized members are outside the Trust Manifest `subject` and are not
publisher claims, and that `extensions` remains the only extension point
this specification defines.

Trust Manifest objects are not opened by this decision. They are signed
payloads with their own retention rule, and other specifications treat them
as opaque.

## Rationale

- **Simple and extensible without taking a stance.** The specification says
  nothing about what an unrecognized member means. A producer following a
  linked-data convention, an enterprise adding local annotations, and an
  implementer prototyping a field all get the same answer: the core reads
  what it defines and passes the rest through.
- **No dependency.** Nothing is referenced, interpreted, or imported from
  any other specification. The no-stability-guarantee clause states that
  this specification will define future members without checking whether an
  outside convention already uses the name. The collision risk sits with
  whoever relies on undefined names, which is where it belongs.
- **Resolves the prose/CDDL contradiction** in the direction the prose
  already went.
- **Consistent with signing.** Catalog signatures already cover unknown
  fields; the Trust Manifest `subject` already excludes everything but the
  bound artifact coordinates. The new section only makes both explicit.
- **`extensions` keeps a distinct job.** It is the *defined* extension
  point: namespaced keys, official extensions, no collision with future
  core members. Unrecognized members are the *absence* of a definition.
  Defined versus undefined is a real distinction, not two ways to do one
  thing.

## Trade-offs

What is lost, stated plainly:

- **Validators no longer catch misspelled member names.** A document with
  `identifer` instead of `identifier` fails for the missing required member,
  but a misspelled optional member such as `descripton` is silently an
  unrecognized member. Mitigation: conformance tooling MAY report
  unrecognized members as informational output.
- **Bare names share one namespace with future core members.** A producer
  using `lifecycle` today may find a future version defines it differently.
  The specification makes no promise here; `extensions` is the stable
  alternative.
- **Strongly typed bindings drop unknown members.** Preservation is a
  SHOULD because a fixed-schema SDK model cannot keep what it cannot
  represent. Ignoring is still satisfied.
- **A second place for data beside `extensions`.** Some producers will put
  data at the root that would have been better namespaced. The
  specification answers with the stability clause rather than a prohibition.

## Alternatives Considered

- **Keep the objects closed (status quo).** Leaves the prose/CDDL
  contradiction in place and rules out outside conventions entirely.
- **Reserve only a syntactic space**, for example member names beginning
  with `@` or containing `:`, and keep bare names closed. Covers prefixed
  terms but not terms a prefix map aliases to bare names, and adds a rule
  whose only purpose is to describe someone else's syntax.
- **Define a JSON-LD compatibility profile or publish a context document.**
  Takes a stance on a convention the TSC has declined to adopt, and pulls
  questions about `type` versus `@type`, `@id`, and value typing into this
  specification.
- **A media-type `profile` parameter.** Does not match how catalogs are
  published or discovered, and this group has already declined `profile`
  parameters for artifact types.

## Revisit

This decision is deliberately reversible. A future major version MAY narrow
or close these objects, depending on how the ecosystem uses them. If a
convention carried in unrecognized members proves its value, a later version
can define it, or define a core member that replaces it. This ADR supersedes
the closed-core rationale of ADR-0012; the `extensions` decision of ADR-0017
stands.
