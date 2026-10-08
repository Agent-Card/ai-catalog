# Introduction

The AI ecosystem comprises a growing number of protocols, artifact
formats, and service types. Model Context Protocol (MCP) servers,
Agent-to-Agent (A2A) agents, Claude Code plugins, datasets, model cards,
and other AI artifacts each define their own metadata and discovery
mechanisms. This fragmentation forces clients and registries to
implement bespoke logic for each artifact type, increasing complexity
and reducing interoperability.

This document defines the **AI Catalog**: a typed, nestable JSON
container for discovering heterogeneous AI artifacts. Each entry
declares its artifact type via a type identifier (which is an IANA media type) and may reference or
embed the native artifact metadata. A minimal catalog is simply a
list of entries — names, types, and URLs — requiring no additional
infrastructure.

For environments that need verifiable identity, compliance evidence,
or provenance tracking, this document also defines an optional **Trust
Manifest** object. An entry can carry independent Trust Manifests, each
identifying its contributor and containing attestations and provenance without
wrapping or modifying the artifact's native format. Each manifest can carry
one signature over its contents and a subject identifying the artifact release.
An optional catalog signature authenticates the catalog snapshot.
Implementations that do not need trust metadata can ignore these features.

The AI Catalog is intentionally agnostic about the artifacts it
indexes. It does not define or constrain the schema of MCP server
manifests, A2A agent cards, or any other artifact format. Instead, it
relies on type identifiers to indicate what each entry is, and delegates
the definition of artifact-specific metadata to the respective protocol
specifications.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
BCP 14 [[RFC2119]] [[RFC8174]] when, and only when, they appear in all
capitals, as shown here.

The following terms are used throughout this document:

AI Catalog
: A JSON document conforming to the `application/ai-catalog+json`
  media type that contains an ordered list of catalog entries.

Catalog Entry
: A single item in an AI Catalog, identified by a type identifier and
  referencing or embedding an AI artifact.

Trust Manifest
: A JSON object grouping one contributor's trust metadata about an AI
  artifact. The entry stores it in the `trustManifests` array. Its
  `contributor` identifies the party to whom the claims are attributed;
  its optional signature authenticates that contributor's claims.

Artifact
: Any AI resource described by a catalog entry, such as an MCP server
  manifest, an A2A agent card, a Claude Code plugin, a
  dataset descriptor, or a nested AI Catalog.

# Design Goals

1. **Artifact Agnosticism**: The catalog MUST be capable of indexing
   any type of AI artifact without requiring knowledge of the
   artifact's internal schema.

2. **Type Identification**: Each catalog entry MUST declare its
   artifact type using a type identifier, enabling clients to select,
   filter, and route entries without parsing artifact content.

3. **Composability**: The catalog format supports nesting — a catalog
   entry can reference another AI Catalog, enabling hierarchical
   organization and multi-artifact packaging.

4. **Progressive Complexity**: The simplest catalog is just entries
   with names and URLs. Trust, identity, and provenance metadata are
   available as optional extensions that never modify the catalog
   structure or artifact formats.

5. **Scalable Federation**: The catalog format enables partitioning
   into sub-catalogs to manage size, and supports delegation to
   sub-catalogs managed by independent publishers. Nested catalog
   entries support a federated model where each segment of the
   hierarchy may be authored, hosted, and updated independently.

6. **Location Independence**: An AI Catalog MAY be served from any URL.
   The standard defines a well-known URL convention to enable
   automated discovery, but catalogs are equally valid when hosted at
   arbitrary paths, embedded in registries, or distributed as files.

# AI Catalog

## Media Type

An AI Catalog document is identified by the media type:

    application/ai-catalog+json

## Top-Level Structure

Producers MUST ensure that each complete AI Catalog document is valid input
to JCS [[RFC8785]], including all nested values, whether or not the catalog is
signed. Consumers MAY reject documents that do not satisfy this requirement.
This requirement does not mandate validation during ingestion. Producers need
not serialize the JSON in canonical form. JCS-based signing and verification
require the input checks defined in their respective procedures.

An AI Catalog document is a JSON object that MUST contain the following
members:

`specVersion`
: A string indicating the version of this specification that the
  catalog conforms to, in "Major.Minor" format (e.g., "1.0").
  See [Version Handling](#version-handling) for compatibility rules.

`entries`
: An array of Catalog Entry objects as defined in [Catalog Entry](#catalog-entry).
  This array MAY be empty.

For example, a minimal catalog listing four AI artifacts:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:example.com:skill:code-review",
      "displayName": "Code Review Assistant",
      "type": "application/agent-skills+zip",
      "url": "https://skills.example.com/code-review/skill.zip"
    },
    {
      "identifier": "urn:air:example.com:mcp:weather",
      "type": "application/mcp-server-card+json",
      "url": "https://api.example.com/mcp/server-card"
    },
    {
      "identifier": "urn:air:example.com:a2a:research",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.example.com/researchAssistant"
    },
    {
      "identifier": "urn:air:example.com:agent:productivity-plugin",
      "displayName": "Productivity Plugin",
      "type": "application/agent-plugins+zip",
      "description": "Tools for common productivity workflows.",
      "tags": ["productivity", "workflows"],
      "url": "https://plugins.example.com/productivity.zip"
    }
  ]
}
```

The following members are OPTIONAL:

`host`
: A Host Info object as defined in [Host Info](#host-info) identifying the
  operator of this catalog.

`extensions`
: A JSON object (map) containing custom, vendor-specific, or
  non-standard fields. See [Extensions](#extensions) for definitions and
  official extension types.

`signature`
: A [Signature object](#signature-object) authenticating this catalog
  snapshot, as defined in [Catalog Snapshot Coverage](#catalog-snapshot-coverage).
  Signer authentication alone does not establish authority to represent the
  catalog operator; see [Catalog Authorization](#catalog-authorization).

`additionalSignatures`
: Reserved for future use. Producers SHOULD omit this member. Consumers MUST
  accept and ignore any value permitted by the catalog's JCS input
  requirements. It is excluded from this catalog's signature payload; it
  establishes no endorsement in this version.

## Host Info

The Host Info object identifies the operator of the catalog. It MUST
contain:

`displayName`
: A string containing the human-readable name of the host (e.g., the
  organization name).

The following members are OPTIONAL:

`identifier`
: A string containing a verifiable identifier for the host (e.g., a
  DID or domain name).

`documentationUrl`
: A string containing a URL to the host's documentation.

`logoUrl`
: A string containing a URL to the host's logo.

For example:

```json
{
  "displayName": "Acme Enterprise AI",
  "identifier": "did:web:acme-corp.com",
  "documentationUrl": "https://docs.acme-corp.com/ai",
  "logoUrl": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0c..."
}
```

## Catalog Entry

A Catalog Entry object describes a single AI artifact in the catalog.
It MUST contain the following members:

`identifier`
: A string uniquely identifying this artifact. This field is an open text format (e.g., any valid URI or URN is accepted). Consumers that do not recognize an identifier scheme MUST treat the value as opaque. Identifier syntax alone does not verify publisher identity or establish trust. For open or federated systems, a globally unique absolute URI is RECOMMENDED. An artifact publisher that wants an entry identifier to be preserved when the artifact appears in other catalogs SHOULD use the AI Catalog-specific `urn:air` naming structure with its own domain in the `{publisher}` segment. A catalog operator incorporating an entry for the first time with a publisher-authorized `urn:air` identifier MUST preserve that identifier exactly.

    **`urn:air` Identifier Format:**
    `urn:air:{publisher}:{namespace}:{name}`

    - `{publisher}`: The domain name of the organization publishing the artifact (e.g., `example.com`).
    - `{namespace}`: The logical namespace, which can contain one or more colon-separated categories (e.g., `mcp`, `skill`, `agent`, `finance:agent`).
    - `{name}`: The stable, unique name of the artifact within the publisher's namespace.

    *Examples:*

    - `urn:air:example.com:skill:code-review`
    - `urn:air:example.com:mcp:weather`

    For closed or local systems where a different identifier format is used, client implementations are responsible for parsing and processing the custom format as appropriate.

    See [Multi-Version Entries](#multi-version-entries) for uniqueness rules when multiple versions are present, and [Catalog Projection](#catalog-projection) for identifiers assigned while projecting an existing Catalog Entry or source-system record.

`type`
: A string containing the identifier that specifies the type of the
  referenced artifact. This field is an open text format, so any string value is accepted. However, to ensure interoperability, it is RECOMMENDED to use one of the following recognized "known types" in the ecosystem when applicable, partitioned by their respective governance boundaries:

    **Core Protocol Types (Governed by the AI Catalog WG):**

    - `application/ai-catalog+json` — a nested AI Catalog
    - `application/agent-card+json` — reserved for a generic Agent Card format

    **Integrated Ecosystem & Third-Party Types (Governed externally):**

    - `application/a2a-agent-card+json` — an A2A Agent Card
    - `application/mcp-server-card+json` — an MCP Server Card
    - `application/agent-skills+json` — Agent Skill Metadata json file
    - `application/agent-skills+md` — an Agent Skill defined in a standard Markdown file (the suffix `+md` is to be registered)
    - `application/agent-skills+zip` — an Agent Skill bundle (ZIP archive)
    - `application/agent-skills+gzip` — an Agent Skill bundle (gzipped tarball)
    - `application/agent-plugins+zip` — an Agent Plugin bundle (ZIP archive)
    - `application/agent-plugins+gzip` — an Agent Plugin bundle (gzipped tarball)

    These values are designed to align with official IANA media type registration standards. Standard ecosystem types use registered structured syntax suffixes (`+json`, `+zip`, `+gzip`). For any new or custom types not listed here, it is up to the specific client implementation to handle them correctly.

A Catalog Entry MUST contain exactly one of the following members to
provide the artifact content:

`url`
: A string containing a URL where the full artifact document can be
  retrieved. The document served at this URL SHOULD be served with
  the media type declared in the `type` field.

`data`
: A JSON value containing the complete artifact document inline. The
  structure of this value is determined by the `type` field and
  is opaque to this specification. Like all catalog data, it is subject to
  the JCS input requirements in [Top-Level Structure](#top-level-structure).

The following members are OPTIONAL:

`displayName`
: A string containing a human-readable name for the artifact.
  This field SHOULD be set only when the referenced artifact does not
  already carry its own canonical human-readable name — for example a
  raw dataset (`application/parquet`), a model blob, a skill bundle
  (`application/agent-skills+zip`), or an Agent Plugin bundle
  (`application/agent-plugins+zip`), none of which directly expose a
  self-describing name without processing the artifact. When the referenced
  artifact does carry such a name — for
  example the `name` field of an A2A Agent Card or the `title` field of
  an MCP Server Card — that artifact is the authoritative source and
  `displayName` SHOULD be omitted to avoid duplicating a value that can
  drift out of sync. When `displayName` *is* present, however, it takes
  precedence: it is the authoritative value for display, and a consumer
  SHOULD render it as given even when it differs from a name carried by
  the referenced artifact. Setting `displayName` is how a publisher
  deliberately overrides the artifact's own name. See
  [Resolving an Artifact's Display Name](#resolving-an-artifact-s-display-name)
  for the full consumer resolution order.

`description`
: A string containing a short description of the artifact. Like
  `displayName`, `description` is OPTIONAL and follows the same
  authoritative-source rule: when the referenced artifact carries its
  own canonical description — for example the `description` field of an
  A2A Agent Card or an MCP Server Card — that artifact is the
  authoritative source and entry `description` SHOULD be omitted to
  avoid duplicating a value that can drift out of sync. When entry
  `description` *is* present, however, it takes precedence: a consumer
  SHOULD render it as given even when it differs from a description
  carried by the referenced artifact, which is how a publisher provides
  a listing-specific blurb. See
  [Resolving an Artifact's Description](#resolving-an-artifact-s-description)
  for the full consumer resolution order.

`tags`
: An array of strings serving as keywords for filtering and discovery.

`version`
: A string containing the version of this artifact.
  [Semantic Versioning](https://semver.org/) is RECOMMENDED but not
  required. See [Multi-Version Entries](#multi-version-entries) for
  how versions interact with `identifier`.

    Like `displayName` and `description`, `version` can restate a value
    the referenced artifact already carries (an A2A Agent Card
    `version`, an MCP Server Card `version`), and when a single entry
    references such an artifact the entry `version` SHOULD be omitted to
    avoid drift — the consumer can read it from the artifact. An entry
    MAY include that version when it needs to be signed directly. Unlike
    `displayName` and `description`, however, `version` is not merely
    cosmetic: it is part of the entry's uniqueness key, so it is
    REQUIRED when a catalog lists multiple versions of the same
    `identifier` (see [Multi-Version Entries](#multi-version-entries)).
    A present `version` is used for catalog-level sorting and selection
    rather than as a free-form display override, so it SHOULD equal the
    version the referenced artifact reports; an entry `version` that
    contradicts the artifact's own version is a publishing error, not a
    deliberate override. See
    [Resolving an Artifact's Version](#resolving-an-artifact-s-version)
    for the full consumer resolution order.

`updatedAt`
: A string containing an ISO 8601 [[RFC3339]] timestamp indicating
  when this entry was last modified.

`extensions`
: A JSON object (map) containing custom data.

`publisher`
: A Publisher object as defined in [Publisher Object](#publisher-object)
  identifying the entity that publishes this artifact. This is the
  sole location for publisher information; it is not duplicated in
  the Trust Manifest.

`digest`
: A string containing the artifact content digest in [Digest Format](#digest-format).
  For `url`, hash the exact retrieved artifact bytes. For `data`, hash the
  UTF-8 JCS-canonicalized [[RFC8785]] JSON value. A digest alone does not
  authenticate its source; see
  [Entry Release Coverage](#entry-release-coverage).

`trustManifests`
: An array of [Trust Manifest](#trust-manifest) objects. Each manifest groups
  one contributor's claims about this artifact and can carry its own signature.
  A contributor's identity is attribution, not proof of authorship.

### Resolving an Artifact's Display Name

Because `displayName` is OPTIONAL, a consumer rendering a catalog entry
cannot assume it is present. To obtain a human-readable name, a consumer
SHOULD resolve one in the following order:

1. **`displayName` on the entry**, if present. A publisher-supplied
   `displayName` always wins, even when it differs from a name carried by
   the referenced artifact.
2. **The referenced artifact's own canonical name**, if the consumer has
   already fetched or cached the artifact — for example the `name` field
   of an A2A Agent Card or the `title` field of an MCP Server Card.
3. **The trailing segment of the entry's `identifier`** as a last
   resort — the portion after its final `:` or `/` delimiter. For
   example, `urn:air:example.com:mcp:weather` yields `weather` and
   `urn:air:anonymous.modelcontextprotocol.io:mcp:brave-search` yields
   `brave-search`.

A consumer SHOULD NOT dereference an artifact at render time solely to
obtain a name. A registry, directory, or other service built on top of a
catalog SHOULD resolve the name once at ingestion — alongside any other
derived metadata it attaches, such as relevance scores or tags — and
cache the result, rather than fetching artifacts on the rendering path.

This order also covers a referenced MCP Server Card whose `title` is
itself absent: step 2 yields no name, so the consumer falls through to
the `identifier` segment in step 3. A publisher MAY still set
`displayName` on such an entry to provide a better name than the bare
identifier segment.

### Resolving an Artifact's Description

Because `description` is OPTIONAL, a consumer that wants to show a
description cannot assume the entry carries one. It SHOULD resolve one in
the following order:

1. **`description` on the entry**, if present. A publisher-supplied
   `description` always wins, even when it differs from a description
   carried by the referenced artifact.
2. **The referenced artifact's own canonical description**, if the
   consumer has already fetched or cached the artifact — for example the
   `description` field of an A2A Agent Card or an MCP Server Card.
3. **No description**, if neither is available. Unlike a name, a
   description has no identifier-derived fallback; a consumer SHOULD
   simply render the entry without one.

As with name resolution, a consumer SHOULD NOT dereference an artifact at
render time solely to obtain a description. A registry, directory, or
other service built on top of a catalog SHOULD resolve the description
once at ingestion and cache the result, rather than fetching artifacts on
the rendering path.

### Resolving an Artifact's Version

Because `version` is OPTIONAL on a single entry — and present only when
the entry disambiguates others that share its `identifier` (see
[Multi-Version Entries](#multi-version-entries)) or deliberately restates
the artifact's version — a consumer cannot assume every entry carries
one. To obtain a version, a consumer SHOULD resolve one in the following
order:

1. **`version` on the entry**, if present. Unlike `displayName` and
   `description`, a present `version` is not a free-form display
   override: it is authoritative for catalog-level sorting and version
   selection. Within a multi-version listing it is REQUIRED and, combined
   with `identifier`, uniquely addresses the entry.
2. **The referenced artifact's own version**, if the consumer has already
   fetched or cached the artifact — for example the `version` field of an
   A2A Agent Card, an MCP Server Card, or an MCP Registry `server.json`.
   A single entry that omits `version` because the artifact already
   carries it is resolved here.
3. **No version**, if neither is available — the entry represents an
   unversioned artifact. A consumer that needs to order such entries
   SHOULD fall back to `updatedAt`, consistent with
   [Multi-Version Entries](#multi-version-entries).

When both the entry and the referenced artifact carry a `version` and
they disagree, the entry `version` is authoritative for catalog-level
sorting and selection; the mismatch is a publishing error (it breaks
latest-selection) that a consumer MAY surface but SHOULD NOT resolve by
silently preferring the artifact's value.

As with name and description resolution, a consumer SHOULD NOT dereference
an artifact at render time solely to obtain a version. A registry,
directory, or other service built on top of a catalog SHOULD resolve the
version once at ingestion and cache the result, rather than fetching
artifacts on the rendering path.

## Multi-Version Entries

A catalog MAY contain multiple entries with the same `identifier` and
different `version` values, representing a version history for a
single artifact — similar to a package registry.

When `version` is present, the combination of `identifier` and `version`
MUST be unique within the catalog. When `version` is absent, `identifier`
alone MUST be unique. The `identifier` SHOULD be stable across versions.
Only publisher-authorized `urn:air` identifiers receive a cross-catalog
preservation requirement, as defined in [Catalog Projection](#catalog-projection).

Clients that need only the latest version SHOULD sort entries
sharing the same `identifier` by `version` (when parseable as a semantic
version) or by `updatedAt`, and select the most recent. Clients
that need a specific version SHOULD match on both `identifier` and `version`.

For example, a catalog listing two versions of the same agent:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:acme.com:agent:finance",
      "version": "2.1.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance/v2.1.json",
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme.com:agent:finance",
      "version": "2.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance/v2.0.json",
      "updatedAt": "2026-01-20T08:00:00Z"
    }
  ]
}
```

Both entries share the same `identifier` but have distinct `version`
values, so the combination is unique.

## Catalog Projection

A publisher-authorized `urn:air` identifier is one assigned by the
artifact publisher or its authorized delegate, with the artifact
publisher's domain in the `{publisher}` segment.

Catalog projection creates a Catalog Entry from either a source Catalog
Entry in another AI Catalog or a source record in another system. When
incorporating a projected entry for the first time, a catalog operator
MUST select its identifier by applying these rules in order:

1. If the source contains a publisher-authorized `urn:air` identifier,
   the operator MUST preserve it exactly.
2. Otherwise, the operator MAY preserve a non-`urn:air` source identifier
   or replace it. Non-`urn:air` identifiers have no guaranteed portability
   across catalogs.
3. When assigning a new identifier, an operator that becomes the artifact
   publisher SHOULD use `urn:air` with its own domain in the `{publisher}`
   segment. An operator acting as an authorized delegate SHOULD use
   `urn:air` with the delegating publisher's domain in that segment. An
   operator that is neither the artifact publisher nor its authorized
   delegate MUST use a non-`urn:air` identifier under its own control.

Operating a catalog or aggregating an entry does not make its operator the
artifact publisher. A catalog operator MUST NOT infer publisher
authorization from the artifact's URL or an unsigned `publisher` field.

Adopting a different primary identifier after publication requires an
explicit migration mechanism, which this specification does not define.

An identifier assigned by a catalog operator identifies the artifact, not
a particular version or source record. It MUST remain stable across
versions, source-coordinate changes, and retrieval-URL changes, and MUST
NOT be reassigned to another artifact. The catalog operator and artifact
publisher are distinct roles. The operator is the entity identified by the
top-level `host` field when that field is present.

A catalog operator MAY retain replaced source identifiers or source-system
coordinates. If retained, they SHOULD be stored in a namespaced entry
extension. They do not participate in catalog uniqueness or establish
publisher identity, trust, or equivalence with another identifier.

```json
{
  "identifier": "https://registry.example/ids/artifacts/7bf4a8c2",
  "type": "application/a2a-agent-card+json",
  "url": "https://registry.example/apis/registry/v3/groups/payments/artifacts/fraud-agent",
  "publisher": {
    "identifier": "did:web:acme.example",
    "displayName": "Acme"
  },
  "extensions": {
    "com.example.registry.coordinates": {
      "registryUri": "https://registry.example",
      "sourceIdentifier": "foo",
      "namespace": "payments",
      "name": "fraud-agent"
    }
  }
}
```

The extension key is illustrative.

## Publisher Object

The Publisher object identifies the entity responsible for an artifact.
It appears on the Catalog Entry and is the canonical location for
publisher information. It MUST contain:

`identifier`
: A string containing a verifiable identifier for the publisher
  organization.

`displayName`
: A string containing the human-readable name of the publisher.

The following members are OPTIONAL:

`identityType`
: A string providing a type hint for the publisher identifier (e.g.,
  "did", "dns").

# Trust Manifest

A Trust Manifest is an OPTIONAL collection of one contributor's trust metadata
about the artifact represented by an entry. The entry's `trustManifests`
array contains these independent contributions. Each manifest MUST contain
`contributor` and MAY contain the optional members below.

## Contributor Identity

`contributor` MUST be an absolute URI [[RFC3986]] identifying the contributor
asserting this manifest's references or claims, not necessarily the issuer
of every referenced attestation or provenance statement. Authors SHOULD use
their existing identity URI, such as `did:web:assessor.example`. The value
MUST be preserved exactly when forwarding a Trust Manifest. Consumers MUST
NOT infer authentication from its spelling or mere presence.

A signed Trust Manifest's `signature.signer` MUST exactly equal `contributor`.
Consumers MUST compare these decoded JSON strings case-sensitively, without
URI normalization. Verifying the signature and this equality authenticates
the contributor attribution. Accepting the claims for an entry additionally
requires [entry release binding](#entry-release-coverage). A signature over
one manifest does not authenticate other manifests or other entry fields.

## Independent Contributions and Updates

Contributors can publish and update their manifests without modifying other
contributors' manifests or invalidating their signatures. This version
supports one signer per manifest and defines no references between manifests.

An entry MAY contain multiple manifests from the same contributor, including
manifests using different verification profiles. Array order does not imply
trust or precedence. Consumers evaluate each manifest independently.

A contributor MAY publish an updated Trust Manifest for the same release.
Two registries may retrieve that manifest at different times and hold
different signed versions. When choosing among updates for the same
contributor and release, consumers SHOULD prefer the manifest with the most
recent acceptable signature, comparing authenticated `issuedAt` instants.
An issuance time is the signer's assertion, not an independently trusted clock.
Equal issuance times with different content require local selection policy;
consumers MUST NOT infer an ordering from array order. Registries SHOULD
preserve the chosen manifest and its signature rather than merge separately
signed contents.

## Manifest Validity

A Trust Manifest MUST contain at least one of: a `signature`, a `trustSchema`,
a non-empty `attestations` array, a non-empty `provenance` array, or a non-empty
`extensions` object. A manifest containing a `signature` MUST also contain
`subject`. A signed manifest MAY endorse only the artifact release identified
by that subject, without additional trust evidence. These members' presence
does not establish verification. Empty manifests MUST be omitted.

## Optional Members

`subject`
: A [Subject object](#subject-object) identifying the artifact release and
  representation to which these claims apply. REQUIRED when `signature` is
  present. It lets the signed manifest travel independently of the entry.

`signature`
: A [Signature object](#signature-object) authenticating this manifest's
  contents, including its subject and contributor identity.

`additionalSignatures`
: Reserved for future use. Producers SHOULD omit this member. Consumers MUST
  accept and ignore any value permitted by the catalog's JCS input
  requirements. It is excluded from this manifest's signature payload; it
  establishes no endorsement in this version.

`trustSchema`
: A [Trust Schema object](#trust-schema-object) describing the framework the
  contributor applies to its claims about this artifact. The descriptor does
  not itself establish a trust root or override the consumer's policy.

`attestations`
: An array of [Attestation objects](#attestation-object) carrying references
  to evidence. Their formats or applicable profiles define evidence verification.

`provenance`
: An array of [Provenance Link objects](#provenance-link-object).

`extensions`
: A JSON object containing this contributor's additional trust metadata, using
  the namespaced keys defined in [Extensions](#extensions). Entry extensions
  describe shared artifact metadata; manifest extensions express a particular
  contributor's claims. A manifest signature covers only the latter.

For example, this unsigned entry carries independent contributions:

```json
{
  "identifier": "urn:air:acme.com:agent:finance",
  "type": "application/a2a-agent-card+json",
  "url": "https://acme.com/finance.json",
  "trustManifests": [
    {
      "contributor": "did:web:acme.com",
      "provenance": [{
        "relation": "publishedFrom",
        "sourceId": "https://github.com/acme/finance"
      }]
    },
    {
      "contributor": "did:web:assessor.example",
      "attestations": [{
        "type": "SOC2-Type2",
        "uri": "https://assessor.example/reports/acme.pdf"
      }]
    }
  ]
}
```

## Subject Object

A Subject object binds a Trust Manifest to the artifact it describes.
It MUST contain `identifier`, `type`, and at least one of `digest` or `url`.
It MAY contain both `digest` and `url`.

`identifier`
: A string containing the artifact's logical identifier. It MUST exactly
  equal the containing entry's `identifier`.

`type`
: A string containing the artifact's type identifier. It MUST exactly equal
  the containing entry's `type`.

`digest`
: The artifact content digest in [Digest Format](#digest-format).
  `subject.digest` MUST be present exactly when `entry.digest` is present,
  and its value MUST exactly equal `entry.digest`. For `url`, hash the exact
  retrieved artifact bytes. For `data`, hash the UTF-8 JCS-canonicalized
  JSON value.

`url`
: An absolute HTTPS URL identifying the artifact resource. When present,
  it MUST exactly equal the containing entry's `url`. It is REQUIRED when
  `digest` is absent. A URL binding identifies the resource at that location;
  it does not bind its current representation to particular bytes.

`version`
: A string containing the artifact release version. `subject.version` MUST
  be present exactly when `entry.version` is present, and its value MUST
  exactly equal `entry.version`.

These fields repeat entry values to make the signed manifest self-contained.
Accepting its claims for an entry
requires [Entry Release Coverage](#entry-release-coverage). Digest-only
binding permits mirrors serving identical bytes. When `subject.url` is
present, changing the entry's URL requires updating the signed subject too.
An inline `data` entry has no URL and therefore requires a digest to carry a
signed Trust Manifest. These rules apply to every artifact type.

## Trust Schema Object

A Trust Schema object describes the trust framework applied to the
artifact. It MUST contain:

`identifier`
: A string identifying the trust schema.

`version`
: A string indicating the schema version.

The following members are OPTIONAL:

`governanceUri`
: A string containing a URI to the governance policy document.

`verificationMethods`
: An array of strings identifying the verification methods supported
  (e.g., "did", "x509", "dns-01").

For example:

```json
{
  "identifier": "urn:trust:acme-enterprise-v1",
  "version": "1.0",
  "governanceUri": "https://acme-corp.com/trust/governance.pdf",
  "verificationMethods": ["did", "x509"]
}
```

## Attestation Object

An Attestation object provides verifiable proof of a claim. It MUST
contain:

`type`
: A string identifying the attestation type (e.g., "SOC2-Type2",
  "HIPAA-Audit", "ISO27001").

`uri`
: A string containing the location of the attestation document.
  This may be an HTTPS URL or an inline Data URI [[RFC2397]].

The following members are OPTIONAL:

`digest`
: A string containing a cryptographic hash for integrity verification
  (e.g., "sha256:abcd1234...").

`size`
: An unsigned integer indicating the size of the attestation in bytes.

`description`
: A string containing a human-readable label.

For example, a compliance attestation with integrity verification:

```json
{
  "type": "SOC2-Type2",
  "uri": "https://trust.acme-corp.com/reports/soc2-2026.pdf",
  "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
  "size": 245760,
  "description": "SOC2 Type 2 audit report for Acme Finance Agent (2026)"
}
```

## Provenance Link Object

A Provenance Link records lineage information. It MUST contain:

`relation`
: A string describing the relationship (e.g., "materializedFrom",
  "derivedFrom", "publishedFrom").

`sourceId`
: A string identifying the source artifact or data.

The following members are OPTIONAL:

`sourceDigest`
: A string containing the digest of the source.

`registryUri`
: A string containing the URI of the registry holding the source.

`statementUri`
: A string containing the URI of a provenance statement document.

`signatureRef`
: A string referencing the key used to sign the provenance statement.

For example, a provenance link recording that an artifact was built
from a specific source commit and published through an OCI registry:

```json
{
  "relation": "publishedFrom",
  "sourceId": "https://github.com/acme-corp/finance-agent",
  "sourceDigest": "sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
  "registryUri": "oci://registry.acme-corp.com/agents/finance",
  "statementUri": "https://trust.acme-corp.com/provenance/finance-agent-v2.1.json",
  "signatureRef": "did:web:acme-corp.com#key-1"
}
```

## Verification Procedures

This section describes how consumers verify Trust Manifests, catalog
snapshots, and the evidence referenced by Trust Manifests.
Verification is OPTIONAL — consumers that do not need trust assurance can
skip this entirely.

[The `did:web` Signer Profile](#the-did-web-signer-profile) defines an initial
interoperable authentication mechanism. Other signer profiles can use the
same data model. A signer profile MUST define permitted signer identities,
key discovery and authorization, algorithms, JWS header requirements, validity
checks, and any authority it establishes. Consumers MUST NOT authenticate an
identity using an unsupported profile.

### Safe Fetching

Verification procedures direct consumers to fetch artifact URLs, evidence
references (`attestation.uri`, `statementUri`, and `registryUri`), and
identity-resolution endpoints derived from signing metadata. These inputs
may be attacker-controlled before authentication, so these fetches are a
server-side request forgery (SSRF) and denial-of-service surface.
Consumers performing verification MUST:

- Resolve and reject URLs targeting private, loopback, link-local, or
  cloud metadata addresses (e.g., `127.0.0.0/8`, `::1`,
  `169.254.0.0/16`, `fc00::/7`, `10.0.0.0/8`, `172.16.0.0/12`,
  `192.168.0.0/16`), and re-check the resolved address after any
  redirect.
- Restrict fetches to the `https` scheme (or inline `data:` URIs) and
  refuse to follow redirects that cross into a disallowed address range.
- Enforce a maximum response size and a request timeout. When
  `attestation.size` is present, reject responses that exceed it; in all
  cases apply a consumer-defined ceiling.
- Treat every fetched document as untrusted input.

Consumers SHOULD prefer inline `data:` attestations and Data-URI logos
to avoid leaking verification activity to third-party endpoints.

### Digest Format

Digests in this specification use the format `algorithm:hex-value`,
where `algorithm` is a hash algorithm identifier and `hex-value` is
the lowercase hexadecimal encoding of the hash output. For example:

    sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08

Producers SHOULD use SHA-256 [[RFC6234]] or stronger. Consumers
MUST reject digest values using algorithms shorter than SHA-256.

### Signature Object

A Trust Manifest or catalog root MAY contain one `signature` object. A
Signature object MUST contain `signer`, `profile`, `issuedAt`, and `jws`, and
MAY contain `expiresAt`. Unrecognized members follow
[Version Handling](#version-handling) and remain part of the signed payload.

`signer`
: An absolute URI [[RFC3986]] identifying the party claimed to have issued
  this endorsement. The applicable signer profile MUST establish that the
  verification key is authorized to sign for this identity. Consumers MUST
  NOT infer authentication or authority from this field alone.

`profile`
: A non-empty string identifying the signer verification procedure, as defined
  in [Profile Selection](#profile-selection). It is authenticated as part of
  the payload but does not itself establish trust in the signer or authority
  to make the claims.

`issuedAt`
: An RFC 3339 [[RFC3339]] timestamp asserting when this endorsement was issued.
  The timestamp is authenticated as part of the payload.

`expiresAt`
: An OPTIONAL RFC 3339 timestamp after which this endorsement is stale.
  If present it MUST denote an instant later than `issuedAt`.

`jws`
: A detached compact JWS [[RFC7515]] over the
  [payload](#signed-payload-and-jws-construction). The stored form is
  `encodedProtectedHeader..encodedSignature`.

#### Profile Selection

Consumers MUST select the verification procedure named by `profile`, and
MUST require that it is both supported and permitted by local policy. They
MUST NOT infer another profile from `signer`, JWS headers, or other metadata,
or fall back to another procedure if the selected profile is unsupported,
disallowed, or fails verification. Such a signature MUST NOT count as a
verified endorsement; other manifests are evaluated independently.

Profiles defined by this specification use reserved names. Independently
defined profiles MUST use absolute URI identifiers [[RFC3986]] under the
profile author's control. Authors are encouraged to use a versioned HTTPS
URL pointing to a human-readable definition of the profile's verification
requirements. Consumers need an implementation of those requirements;
retrieving the document does not supply verification behavior. Profile
identifiers MUST be compared exactly and case-sensitively, without URI
normalization.

A profile identifier names a defined set of verification requirements. It
MUST NOT be reused for a different set of requirements. Key rotation under
those requirements does not change the profile. A consumer MAY impose
stricter local acceptance requirements without defining another profile.

The selected profile MUST authenticate the exact `signer` value using its
specified key-authorization and verification rules. Consumers MUST also
apply the coverage and authority checks required for the intended endorsement.
The [`did:web` Publisher Profile](#the-did-web-publisher-profile), for example,
adds publisher authorization and release coverage to the `did:web` Signer
Profile.

#### Signed Payload and JWS Construction

The payload is the containing Trust Manifest or catalog object, with only
these two members omitted:

1. The immediate `jws` member of its immediate `signature` object.
2. Its immediate `additionalSignatures` member, if present.

All other members and values MUST be retained, including `signature.signer`,
`signature.profile`, `signature.issuedAt`, optional `signature.expiresAt`,
and unrecognized members. Ignoring an unrecognized field's meaning MUST NOT
remove it from the payload. The omissions are not recursive: members named
`jws` or `additionalSignatures` elsewhere remain included. For example, a
catalog signature includes complete nested Trust Manifests and their signatures.

For example, a signed release-only manifest has this payload:

```json
{
  "contributor": "did:web:acme.com",
  "subject": {
    "identifier": "urn:air:acme.com:agent:finance",
    "type": "application/a2a-agent-card+json",
    "digest": "sha256:56bbd2ff730d81a52951fc2f58809dfb086b4be7a82766dcc18cfe32ff6acbbd"
  },
  "signature": {
    "signer": "did:web:acme.com",
    "profile": "did-web-v1",
    "issuedAt": "2026-09-12T10:00:00Z"
  }
}
```

Canonicalize this payload with JCS [[RFC8785]]. Its UTF-8 bytes are the JWS
payload. Use ordinary base64url-encoded JWS signing input, then omit only the
payload segment from the stored compact serialization, as specified in
Appendix F of [[RFC7515]]. Verifiers reconstruct that segment to verify the
JWS. The payload MUST satisfy JCS's I-JSON constraints; parsers MUST reject
duplicate JSON member names rather than silently discard one. Large integers
that cannot round-trip as IEEE 754 doubles SHOULD be encoded as strings.

The protected header MUST contain `alg` and `typ`. The `typ` value MUST
exactly match the kind of containing object:

| Containing object | Protected `typ` value |
| --- | --- |
| Trust Manifest | `ai-catalog-trust-manifest+jws` |
| Catalog root | `ai-catalog+jws` |

Consumers MUST reject a missing or mismatched `typ`. This authenticated marker
prevents reusing a manifest signature as a catalog signature or vice versa.
The `alg` value `none` MUST NOT be accepted. The protected header MUST NOT
contain `b64`: the unencoded-payload option of [[RFC7797]] is not used. All
other header parameters, algorithm allowlists, and key-selection rules are
governed by the applicable signer profile and JWS requirements, including
rejection of unsupported critical parameters. A successful cryptographic
check alone establishes neither signer identity nor authority to make the claims.

#### Signature Acceptance and Time

Consumers MUST validate the Signature object's structure, profile selection,
payload, JWS, and selected signer profile before accepting an
endorsement. They MUST validate timestamp syntax and compare timestamps as
instants, not strings.
Consumers MUST NOT accept an endorsement before `issuedAt` or at or after
`expiresAt`, when present. Consumers MAY allow a small clock-skew tolerance
determined by implementation defaults or local policy. A new signature does
not cryptographically invalidate an old one. Endorsement expiry does not
replace freshness or validity checks defined by referenced evidence formats.

An invalid, unsupported, or expired signature MUST NOT count as a verified
endorsement. Other manifests are evaluated independently; consumers MAY
apply local requirements such as evidence from particular contributors.
Consumers MUST limit authentication claims based on a Trust Manifest to its
signed contents and successfully verified subject bindings.

### Entry Release Coverage

Before relying on a Trust Manifest's signature as an endorsement of an entry's
artifact or of claims about that artifact, consumers MUST require:

- A [verified](#signature-acceptance-and-time) Signature object whose `signer`
  exactly equals the manifest's `contributor`.
- A signed `subject` whose `identifier` and `type` exactly equal the
  corresponding entry fields.
- Either both `subject.version` and `entry.version` absent, or both present
  and exactly equal.
- Either both `subject.digest` and `entry.digest` absent, or both present
  and exactly equal. When present, the consumer MUST verify artifact bytes
  against that digest using [Verifying Artifact Integrity](#verifying-artifact-integrity).
- When `subject.url` is present, an absolute HTTPS URL exactly equal to
  `entry.url`.
- At least one of `subject.digest` or `subject.url` present. When both are
  present, both bindings MUST succeed; URL binding MUST NOT excuse a failed
  digest check.

These comparisons are between decoded JSON strings and MUST be case-sensitive,
without URI normalization. Adding, removing, or changing an entry's version
or digest without the corresponding subject change makes the manifest
unacceptable for that entry, even if its signature still verifies independently.
Consumers MUST NOT combine fields from different manifests to establish binding.

A digest binding authenticates exact artifact content. A URL-only binding
identifies the resource selected by the signer, whose representation can
change without a new manifest. Consumers MUST NOT treat URL-only binding as
proof that the signer examined or approved the resource's current bytes.
Consumers requiring that assurance MUST require a verified digest binding.
When fetching a signed URL, consumers MUST apply [Safe Fetching](#safe-fetching),
including the existing checks on redirects. The signature binds the starting
URL, not a fixed final destination after redirects.

Other entry fields, including entry extensions, are outside the manifest
signature's scope. Referenced evidence retains its own verification requirements.

### Catalog Snapshot Coverage

A catalog signature covers the entire catalog object, omitting only its own
`signature.jws` and its own reserved `additionalSignatures` as defined in
[Signed Payload and JWS Construction](#signed-payload-and-jws-construction).
This includes `specVersion`, every entry in order, Host Info, extensions, and
all other present members, including unknown fields.

Nested manifest signatures and nested `additionalSignatures` members remain
included. Adding, removing, or changing a contribution therefore changes the
catalog snapshot and requires a new catalog signature. Adding the catalog's
own reserved `additionalSignatures` does not change its signed payload.
Snapshot integrity does not replace checks on referenced artifacts or
establish the authority of entry publishers.

### The `did:web` Signer Profile

This profile is selected by the exact `profile` value `did-web-v1`. It
authenticates a signer using a root `did:web` DID and an ES256 assertion key.
It can authenticate a publisher, assessor, registry, or other contributor.
Authentication does not by itself grant publisher, host, or catalog authority.
The [`did:web` Publisher Profile](#the-did-web-publisher-profile) adds publisher
namespace authorization. The [`did:web` Catalog Profile](#the-did-web-catalog-profile)
establishes attribution to the declared catalog operator.

The Signature object's `signer` MUST be a root `did:web` DID. Its domain
MUST be lowercase ASCII, with no port, IP address, trailing root dot, or
Unicode U-label; IDNA A-labels are permitted [[DIDWEB]] [[RFC5890]]
[[RFC5891]].

Other identity mechanisms, delegated controllers, path-based `did:web` DIDs,
and algorithms require separately defined profiles. Implementations MAY
support additional profiles by agreement; they MUST NOT silently apply these
rules to a different mechanism.

#### JWS Algorithm and Key Requirements

Producers conforming to the `did:web` Signer Profile MUST use ES256 as
defined by [[RFC7518]]. Consumers implementing the `did:web` Signer Profile
MUST support ES256 and MUST reject any other `alg` value when applying that
profile. A different algorithm can be introduced by a future signature
profile; an implementation-specific choice does not extend the `did:web`
Signer Profile.

The protected JWS header MUST contain `kid`, identifying the verification
method that authorizes the signature. It MUST NOT contain `jku`, `jwk`, `x5u`,
or `x5c`; a verifier applying the `did:web` Signer Profile selects key
material only through the issuer's DID document, never from a key source named
by the signature itself.

The protected `kid` MUST be an absolute DID URL consisting of the exact
`signer` value followed by a non-empty fragment, with no path or query.
A mismatch MUST fail verification under this profile. It identifies a
verification method in the signer's DID document.

For example, a signature with `signer` set to `did:web:assessor.example`
can use `kid` set to `did:web:assessor.example#assertion-key`.

#### DID Document Resolution and Key Selection

The verifier MUST resolve `signer` according to the `did:web` method
[[DIDWEB]] and process the result as a DID document according to DID Core
[[DIDCORE]]. The resolution MUST satisfy the safe-fetching requirements in
[Safe Fetching](#safe-fetching). Resolution fails under the `did:web` Signer
Profile if the DID document cannot be retrieved and validated or if its `id`
is not exactly equal to `signer`.

The verification method selected by `kid` MUST be authorized by the DID
document's `assertionMethod` verification relationship. An
`assertionMethod` entry can contain the verification method directly or can
reference a method in the top-level `verificationMethod` collection. After
resolving relative DID URLs as defined by DID Core, the verifier MUST select
exactly one verification method whose `id` exactly equals `kid`.

A key's presence in the top-level `verificationMethod` collection does not by
itself authorize the key to sign an AI Catalog endorsement. A key used only
for another relationship, such as `authentication` or `keyAgreement`, MUST NOT be accepted.
The selected verification method's `controller` MUST exactly equal
`signer`; the `did:web` Signer Profile does not support a verification method
controlled by another DID.

The selected verification method MUST contain `publicKeyJwk` [[RFC7517]]. The
JWK MUST describe a P-256 elliptic-curve public key: `kty` MUST be `EC`, `crv`
MUST be `P-256`, and `x` and `y` MUST contain valid curve coordinates. It MUST
NOT contain private key material. When present, `alg` MUST be `ES256`, `use`
MUST be `sig`, and `key_ops` MUST permit `verify`. A `kid` member inside the
JWK, if present, is not used for verification-method selection; the DID
verification method's `id` is authoritative.

#### Current-State Verification

This profile verifies against the DID document returned at verification time.
If the key identified by `kid` is no longer authorized by `assertionMethod`,
verification does not succeed. The Signature object's `issuedAt` value records a
claim by the issuer; it is not an independently trusted timestamp and cannot
prove that a removed key was authorized in the past.

Historical verification requires a trustworthy record of the DID document and
the relevant key authorization at the time of signing. This specification does
not define such a record. Applications that require durable historical
verification need an additional mechanism, such as a versioned DID method,
transparency log, or independently timestamped signature profile.

#### Verification Result

Signer authentication succeeds only when the Signature object and detached
JWS satisfy [Signature Object](#signature-object), the DID document resolves
and authorizes exactly one suitable ES256 key under `assertionMethod`, and
the signature verifies over the reconstructed payload. The authenticated
identity is the Signature object's `signer`.

Failure MUST NOT be treated as a verified endorsement. Consumers MAY retain
or display unverified content, retry temporarily unavailable resolution, or
reject it according to local policy. A successful signature is acceptable
as current only after [Signature Acceptance and Time](#signature-acceptance-and-time).

### The `did:web` Publisher Profile

This profile applies the [`did:web` Signer Profile](#the-did-web-signer-profile)
with two additional requirements:

- **Publisher authorization:** The entry MUST use the standard `urn:air`
  syntax. Its `{publisher}` component is the text following `urn:air:` and
  preceding the next colon and MUST satisfy the root `did:web` domain
  restrictions above. The authenticated signer identity MUST exactly match
  `did:web:` followed by that component. Subdomain, suffix, and
  organizational-ownership heuristics MUST NOT be used.
- **Release binding:** The signature MUST satisfy
  [Entry Release Coverage](#entry-release-coverage), including the signed subject
  matching the entry and verification of every present digest or URL binding.

For `urn:air:example.com:agent:billing`, the publisher signer is therefore
`did:web:example.com`. A valid signature by an assessor can endorse claims
about that same release, but does not satisfy publisher authorization.
Matching the publisher domain proves namespace control, not reputation,
claim accuracy, or artifact safety. Consumers choose which publishers and
claims meet their trust policies. A publisher MAY issue a signed manifest
containing only its contributor identity, subject, and signature to endorse
the artifact release.

### Catalog Authorization

Consumers accepting a signature as a catalog endorsement MUST establish its
signer's authority for the catalog using a catalog-authorization profile or
configured policy. The following profile establishes attribution to the
operator identified in the signed Host Info.

#### The `did:web` Catalog Profile

This profile applies the [`did:web` Signer Profile](#the-did-web-signer-profile)
with two additional requirements:

- **Catalog coverage:** The root signature MUST satisfy
  [Catalog Snapshot Coverage](#catalog-snapshot-coverage), including the
  protected JWS `typ` value `ai-catalog+jws`.
- **Operator attribution:** The catalog MUST contain `host.identifier`, and
  its value MUST exactly equal the authenticated root `signature.signer`.
  Consumers MUST compare the decoded JSON strings case-sensitively, without
  URI normalization. The Signer Profile's root `did:web` restrictions apply.

The Catalog Profile uses the Signer Profile's `profile: "did-web-v1"` and
adds the checks above for accepting a catalog endorsement. A matching unsigned
`host.identifier` alone does not establish operator attribution.

For example, a catalog with `host.identifier` set to `did:web:registry.example`
and a valid root signature from that DID satisfies operator attribution.
This authenticates the snapshot as that declared operator's endorsement.
It does not establish the operator's reputation, legal identity, or that
this is the catalog expected by a particular application. Consumers determine
whether the authenticated operator meets their trust policy. The profile
neither binds the catalog to its retrieval URL nor establishes publisher
authority for its entries.

HTTPS authenticates the serving domain for transport. A DID document's
service endpoint may describe a location, but is not by itself proof that
the retrieved catalog was signed by that identity.

### Publisher and Policy Metadata

A Trust Manifest signature does not authenticate the entry's `publisher`
object or its entry extensions, including the
[Policy URLs extension](#policy-urls-extension). These fields are outside
its payload. Consumers MUST distinguish publisher-authenticated metadata
from metadata supplied or endorsed by another entity. A catalog signature
covers them as part of its signer's snapshot, subject to
[Catalog Authorization](#catalog-authorization); this does not by itself establish
publisher endorsement of those values. This specification does not define
a verification profile for a `publisher-identity` attestation.

An accepted publisher endorsement of the artifact does not authenticate its
policy links. Signing the catalog authenticates the URL strings in its
policy extension, not the contents of documents served at those URLs.

### Verifying Artifact Integrity

When an entry contains `digest`, verify its artifact representation as follows:

1. Retrieve bytes from `entry.url`, or use `entry.data`, observing
   [Safe Fetching](#safe-fetching).
2. Compute the digest of the retrieved bytes or the UTF-8 JCS-canonicalized
   `data` value using the algorithm named by `entry.digest`.
3. Compare with `entry.digest`. A mismatch MUST fail artifact verification.

A matching digest alone does not authenticate its source. Accepting an
endorsement additionally requires the signature, subject matching, and
applicable authority checks in [Entry Release Coverage](#entry-release-coverage).
The optional `provenance[].sourceDigest` identifies an upstream source and
MUST NOT be substituted for the digest of this entry's artifact.

### Verifying Attestations

For each attestation in the `attestations` array:

1. Fetch the attestation document from `uri`.
2. If `digest` is present, verify the fetched document matches the
   declared digest.
3. Validate the attestation per its `type` (e.g., verify a JWT
   signature, confirm a PDF certificate is current).

### Provenance Statements

A Provenance Link MAY reference a signed provenance statement via
`statementUri` and the key that signed it via `signatureRef`. The statement's
own format MUST define its signature algorithm, signer authorization,
key-selection rules, and verification procedure. The `did:web` Publisher
Profile for Entry Trust Manifests does not automatically apply to a provenance
statement, whose issuer may be a builder, transparency service, or other party.

To process such a statement:

1. Fetch the statement document from `statementUri`, observing
   [Safe Fetching](#safe-fetching).
2. Validate the statement and its signature according to the statement
   format's verification procedure and the consumer's trust policy.
   `signatureRef` can assist key discovery when that format defines how to use
   it, but the value is not a trust anchor by itself.
3. Confirm the statement's subject matches `entry.digest`, when present.
   Without an entry digest, content binding requires the evidence format's
   own verification procedure; a matching URL alone does not establish it.
   Treat an unverifiable statement as absent, not as a failure of the artifact
   itself.

# Organizing Catalogs

As catalogs grow, a flat list of entries becomes unwieldy. Because any
catalog entry can have a `type` of `application/ai-catalog+json`,
catalogs are naturally composable — an entry can reference or inline
another AI Catalog, creating a hierarchy of any depth.

## Nested Catalog Entries

A catalog entry whose `type` is `application/ai-catalog+json`
references (via `url`) or embeds (via `data`) another AI Catalog
document. This mechanism supports two complementary use cases:

**Organizational hierarchy.** An enterprise with thousands of artifacts
can partition its catalog into sub-catalogs by department, product line,
or region. Each sub-catalog is an independent AI Catalog document with
its own `host` and entries:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:catalog:finance",
      "displayName": "Finance Services",
      "type": "application/ai-catalog+json",
      "url": "https://acme.com/catalogs/finance.json"
    },
    {
      "identifier": "urn:air:acme.com:catalog:ml",
      "displayName": "ML Models",
      "type": "application/ai-catalog+json",
      "url": "https://acme.com/catalogs/ml.json"
    },
    {
      "identifier": "urn:air:acme.com:catalog:devops",
      "displayName": "DevOps Tools",
      "type": "application/ai-catalog+json",
      "url": "https://acme.com/catalogs/devops.json"
    }
  ]
}
```

**Multi-artifact packaging.** An entry with a `publisher` that contains
a nested catalog may be interpreted as a set of items that could be
acquired as a unit. For example, a finance plugin that ships an A2A
agent, an MCP server, and a dataset together:

```json
{
  "identifier": "urn:air:acme.com:plugin:finance-suite",
  "displayName": "Finance Plugin",
  "type": "application/ai-catalog+json",
  "url": "https://acme.com/plugins/finance-suite.json",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  }
}
```

The document at that URL would itself be an AI Catalog containing
the A2A agent, MCP server, and dataset entries.

A nested catalog entry is a regular catalog entry — it has an
`identifier`, may carry `trustManifests`, and may include a
`publisher`. An entry inside a nested catalog MAY reuse the same
`identifier` as an entry elsewhere; this indicates the same logical
artifact.

Clients processing nested catalogs SHOULD impose a maximum nesting
depth to prevent circular references. A depth limit of 4 is
RECOMMENDED. Implementations MAY support deeper nesting but SHOULD
document their limit.

# Extensions

The `extensions` property appears on the AI Catalog top-level object,
on Catalog Entry objects, and on Trust Manifest objects. It provides
a single, well-defined extension point for custom or vendor-specific
properties.

## Format and Key Naming

The `extensions` field is a JSON object (map). Each key in the object MUST
represent the extension type (namespace), and the corresponding value contains the extension data.

To avoid collisions between independent publishers, the keys MUST
be a valid URL or a reverse-DNS string:

- **Reverse-DNS prefix** for vendor-specific extensions:
  `com.example.confidenceScore`, `io.acme.deploymentRegion`.
- **URL prefix** for publicly accessible extension schemas:
  `https://cisco.com/extensions/security-scan`.

Consumers that do not recognize an extension key MUST ignore it without
throwing an error.

For example, a catalog entry with `extensions` representing metadata and a custom schema:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:treasury.gov:okf:fiscaldata",
      "type": "text/vnd.okf+markdown",
      "tags": ["finance", "treasury"],
      "extensions": {
        "https://ai-catalog.org/extensions/metadata": {
          "location": "US-West",
          "environment": "staging",
          "version-compatible": [">=1.0.0"]
        },
        "https://openknowledgeformat.org/ns#": {
          "@context": {
            "us-gaap": "https://xbrl.fasb.org/us-gaap/",
            "ifrs": "https://xbrl.ifrs.org/taxonomy/"
          },
          "type": "Financial Dataset",
          "taxonomy": "us-gaap",
          "conformsTo": ["us-gaap:Revenue", "ifrs:Revenue"]
        }
      }
    }
  ]
}
```

## Official Extensions

While publishers are free to create custom extensions, this specification
defines a set of "Official" known types for commonly requested schemas:

1. **Metadata** (`https://ai-catalog.org/extensions/metadata`)
   - Used to store generic, schemaless key-value pairs.
2. **Policy URLs** (`https://ai-catalog.org/extensions/policy-urls`)
   - Links to the policies governing an artifact, defined below.

As custom extensions become highly popular, the AI-Catalog TSC may promote
them to Official Known Types or core standard fields in future specification versions.

### Policy URLs Extension

The official extension key `https://ai-catalog.org/extensions/policy-urls`
identifies links to policies governing the entry's artifact. It is used in
`entry.extensions`. Its value MUST be a JSON object. The following members
are OPTIONAL:

`privacyPolicyUrl`
: A string containing a URL to the privacy policy governing this artifact.

`termsOfServiceUrl`
: A string containing a URL to the terms of service governing this artifact.

A publisher or catalog operator MAY populate this extension. An operator's
own catalog policy is not a substitute for the artifact's governing policy.
The extension's presence does not establish who authenticated its values.

A Trust Manifest signature does not authenticate this extension. A catalog
signature covers its complete value as part of the catalog snapshot, subject
to [Catalog Authorization](#catalog-authorization). Signing authenticates
the URL strings, not the contents of policy documents that can change at
those URLs. Consumers fetching those documents MUST follow
[Safe Fetching](#safe-fetching).

For example, this entry excerpt supplies both links:

```json
{
  "extensions": {
    "https://ai-catalog.org/extensions/policy-urls": {
      "privacyPolicyUrl": "https://example.com/privacy",
      "termsOfServiceUrl": "https://example.com/terms"
    }
  }
}
```

# Version Handling

The `specVersion` field identifies which version of this specification
a catalog conforms to. This section defines how producers and consumers
handle version differences.

## Version Format

The `specVersion` value is a "Major.Minor" string (e.g., "1.0",
"1.1", "2.0"). Major and minor components are non-negative integers.

## Compatibility Rules

Minor version increments (e.g., 1.0 → 1.1)
: The specification adds new OPTIONAL fields or features. Documents
  conforming to a higher minor version are backward-compatible with
  consumers that understand the same major version. Consumers MUST
  ignore unrecognized fields.

Major version increments (e.g., 1.x → 2.0)
: The specification introduces breaking changes (removed fields,
  changed semantics, new required fields). Consumers that do not
  support the major version SHOULD reject the document with an
  informative error rather than silently misinterpreting it.

## Consumer Behavior

Consumers SHOULD:

- Parse the `specVersion` field before processing the document.
- Accept documents whose major version matches their supported major
  version, regardless of minor version differences.
- Ignore unrecognized fields (forward compatibility within a major
  version).
- Reject documents whose major version is higher than the highest
  major version they support, with an informative error message.

## Producer Behavior

Producers MUST set `specVersion` to the version of this specification
they implement. Producers SHOULD NOT set `specVersion` to a version
higher than they actually conform to.

# Discovery

## Location Independence

An AI Catalog document MAY be served from any URL. It is identified
by its media type (`application/ai-catalog+json`) and its `specVersion`
field, not by its URL path. Catalogs are equally valid when hosted at
an arbitrary path, embedded in a registry response, packaged in an
archive, or distributed as a local file.

When served over HTTP, the document SHOULD be served with the media
type `application/ai-catalog+json`.

## Well-Known URI

To support automated discovery, hosts MAY serve an AI Catalog at the
following well-known URI [[RFC8615]]:

    /.well-known/ai-catalog.json

Clients performing domain-level discovery SHOULD attempt to retrieve
this well-known URL. If a valid AI Catalog document is returned, the
client SHOULD use the entries' `url` values to retrieve individual
artifacts. Trust metadata, when present, is carried inline on the
entries as Trust Manifests.

Use of the well-known URI is OPTIONAL. Hosts that publish catalogs at
other locations (e.g., as part of an API response or a package
registry) are fully conformant.

## Dynamic Discovery

Implementing protocols MAY support dynamic catalog generation through
their own mechanisms, such as providing different catalog content based
on a caller's identity or query parameters. Defining dynamic discovery
behavior is out of scope for this specification.

## Link Relation Discovery

Websites MAY advertise their AI Catalog by including an `ai-catalog`
link relation in HTTP responses or HTML documents. This enables AI
agents, crawlers, and other automated clients to discover the catalog
associated with any website without prior knowledge of its location.

**HTTP Link header.** A server MAY include a `Link` header [[RFC8288]]
in HTTP responses:

    Link: <https://example.com/catalog/ai.json>; rel="ai-catalog"

**HTML `<link>` element.** An HTML page MAY include a link element in
the document head:

```html
<link rel="ai-catalog" href="/catalog/ai.json"
      type="application/ai-catalog+json">
```

**Agent-driven discovery.** AI agents that interact with websites
(for example, agents following user instructions to "find tools on
this site" or browsing on behalf of a user) SHOULD check for the
`ai-catalog` link relation on the target website. The discovery
procedure is:

1. Fetch the target URL and inspect the HTTP response headers for
   a `Link` header with `rel="ai-catalog"`.
2. If no `Link` header is present and the response is an HTML
   document, parse the document for a `<link>` element with
   `rel="ai-catalog"`.
3. If neither is found, optionally fall back to the well-known URI
   `/.well-known/ai-catalog.json` as described in
   [Well-Known URI](#well-known-uri).
4. Retrieve the discovered URL. If the response carries a JSON media
   type (`application/ai-catalog+json` is preferred, but a generic
   type such as `application/json` is acceptable, per
   [Location Independence](#location-independence)) and the document
   contains a valid `specVersion` field, treat it as the site's AI
   Catalog.

This mechanism allows any website to surface its AI tools, agents,
and services to visiting agents through a standard, machine-readable
pointer — without requiring changes to the site's visible content.

# Conformance Levels

This specification defines three conformance levels. Each level builds
on the previous one. Implementations MUST satisfy all requirements of
their declared level.

## Level 1: Minimal Catalog

A conformant Minimal Catalog is a JSON document with media type
`application/ai-catalog+json` that contains:

- `specVersion` — the specification version string
- `entries` — an array of Catalog Entry objects, each containing at
  minimum `identifier`, `type`, and exactly one of `url` or
  `data`

All other defined members are OPTIONAL. This level supports consumers that
only need a simple list of artifacts. Each manifest in `trustManifests`, when
present at any level, MUST satisfy [Manifest Validity](#manifest-validity).

## Level 2: Discoverable Catalog

In addition to Level 1 requirements, a Discoverable Catalog:

- Includes a `host` object identifying the catalog operator
- MAY be served at the well-known URI `/.well-known/ai-catalog.json`
  to enable automated domain-level discovery

## Level 3: Trusted Catalog

In addition to Level 2 requirements, a Trusted Catalog:

- Includes an acceptably signed, publisher-authorized Trust Manifest on each
  entry whose publisher authenticity is to be relied upon, using
  [The `did:web` Publisher Profile](#the-did-web-publisher-profile).
- Consumers MUST authenticate signers, verify signatures and endorsement
  times, and enforce [Entry Release Coverage](#entry-release-coverage), including
  artifact content verification when a digest is present, before relying on
  signed claims. URL-only binding does not establish exact-content endorsement.
- Additional contributors MAY provide their own Trust Manifests. Before
  relying on their claims, consumers MUST verify each contributor's signature
  and the subject binding to the same entry release.
- Consumers MUST distinguish the initial interoperable `did:web` profiles
  from other profiles supported by private agreement. Future profiles can
  define additional interoperable authentication and authorization mechanisms.
- SHOULD provide catalog-level integrity through a content-addressed channel
  or a signature satisfying [Catalog Snapshot Coverage](#catalog-snapshot-coverage)
  and [the `did:web` Catalog Profile](#the-did-web-catalog-profile) or another
  applicable operator-authorization profile or configured policy.
- MAY include signed attestations, provenance, and manifest extensions,
  according to consumer policy.

Conformance does not imply that every optional signature is acceptable or
that every claim is true. Unverified additional contributions do not by
themselves invalidate an independently verified publisher endorsement.

Implementations at any level are fully conformant with this
specification. Consumers MAY ignore fields defined at higher
conformance levels and SHOULD gracefully handle their absence.

# Security Considerations

## Trust Layers

This specification supports a progressive trust model. Each layer
builds on the previous one, adding confidence without requiring all
consumers to implement every layer. Consumers choose the level
appropriate to their threat model.

**Layer 0 — Transport Security**
: The catalog and artifacts are served over HTTPS (TLS 1.2 or later).
  The consumer trusts the TLS certificate chain and DNS resolution.
  This prevents passive eavesdropping and casual tampering but does
  not protect against compromised hosting or DNS hijack.

**Layer 1 — Artifact Digest**
: `entry.digest` allows consumers to compare fetched or embedded content
  with the declared digest. Without an authenticated endorsement, an attacker
  controlling the catalog can substitute both the content and the digest.
  A provenance source digest describes the source, not the entry's
  representation.

**Layer 2 — Trust Manifest Signatures**
: A manifest signature binds its complete claims to the artifact identifier,
  version when present, type, and a digest or HTTPS URL through its signed
  subject. The consumer authenticates its signer, checks every present artifact
  binding, and evaluates authority for the intended claim. A digest binds exact
  content; a URL-only endorsement permits the resource's representation to change.
  Independent contributor
  manifests can coexist. A valid signature over one contribution does not
  authenticate another or establish completeness of the catalog.

**Layer 3 — Content-Addressed Distribution (OCI)**
: The catalog is distributed through an OCI registry where all content
  — entries, artifacts, and Trust Manifests — is addressed by
  cryptographic digest. The registry enforces integrity: substitution
  is impossible because any change produces a different digest.
  Cosign or Notation signatures on OCI manifests provide an additional
  layer of publisher authentication.

Consumers that rely on trust metadata for security decisions SHOULD
implement at least Layer 2 (signature verification). Consumers that
only implement Layer 0 or Layer 1 SHOULD treat Trust Manifest content
as advisory, not authoritative.

## Nested Catalog Depth and Circular References

Clients processing nested catalogs SHOULD enforce a maximum recursion
depth to prevent denial-of-service attacks via deeply nested or
circular catalog references. A maximum depth of 4 is RECOMMENDED.

Depth limits alone do not prevent circular references at shallow
depths (e.g., Catalog A → Catalog B → Catalog A). Clients SHOULD
track the set of catalog URLs visited during recursive resolution and
reject any catalog URL that has already been fetched in the current
traversal path.

## Catalog Poisoning

An attacker who can modify a catalog document (e.g., through a
compromised hosting account or DNS hijack) can redirect consumers to
malicious artifacts by changing `url` values or injecting new entries.

The trust layers described above provide progressive defense against
this threat:

- **Layer 0** relies on HTTPS certificate management to prevent
  unauthorized modification.
- **Layer 1** enables post-fetch integrity checks but does not prevent
  whole-entry substitution.
- **Layer 2** binds the signed Trust Manifest to the logical artifact and
  its exact content or HTTPS resource through the signed `subject`. It prevents
  catalog intermediaries from substituting a different representation under
  a digest binding or a different URL under URL binding, and prevents release
  relabeling. URL-only binding does not prevent changes at the selected origin.
- **Layer 3** makes modification structurally impossible through
  content-addressing.

## Trust Manifest Substitution

Because a Trust Manifest is a peer element of the catalog entry rather
than part of the artifact, an attacker who can write the catalog
document can attempt to substitute the artifact, the Trust Manifest, or
both. This specification defends against substitution with three
compounding mechanisms:

- **Release binding.** Every accepted artifact endorsement jointly covers
  subject identifier, type, version when present, and a digest or HTTPS URL,
  plus the claims relied upon. Consumers check subject-to-entry equality and
  every present artifact binding. URL-only binding authenticates a resource
  location, not immutable content.
- **Signer and claim authority.** Contributor identities are not proof. Publisher
  authorization requires the authenticated signer to match the publisher
  namespace; contributor attribution requires authentication as that
  contributor. An attacker's signature under its own identity does not
  authenticate another publisher or contributor.
- **Catalog-level integrity.** Manifest signatures do not prevent adding,
  removing, or reordering complete entries. Hosts SHOULD provide a signature
  satisfying [Catalog Snapshot Coverage](#catalog-snapshot-coverage), with
  operator authorization, or an authenticated content-addressed channel.

Signatures do not prove that a newer manifest, omitted contributor, or revoked
evidence does not exist. Consumers requiring freshness beyond acceptable
endorsement times need an appropriate update source and evidence policy.

## Identifier Typosquatting

Catalog entries are identified by URIs/URNs. An attacker can register
identifiers similar to legitimate ones (e.g., `urn:air:acme.com:agent:financ`
vs. `urn:air:acme.com:agent:finance`) to trick consumers into using a
malicious artifact.

Registries and consumers SHOULD implement similarity checks on
identifiers. Publishers SHOULD use identifiers anchored to domains
they control (e.g., DIDs or domain-scoped URNs).

## Stale Attestations

Attestation documents referenced in Trust Manifests have no built-in
expiry mechanism in this specification. A SOC2 report from a previous
year may no longer reflect current practices.

Consumers SHOULD:

- Check acceptable contributor endorsement times; unsigned entry `updatedAt`
  is only an advisory listing timestamp.
- Independently verify attestation documents are current when making
  trust decisions.
- Treat attestations as evidence, not guarantees — the attestation
  indicates a claim was made, not that it remains valid indefinitely.

Future versions of this specification MAY add `validFrom` and
`expiresAt` fields to the Attestation object.

## Embedded Content Safety

When the `data` field contains embedded artifact content, consumers
MUST treat it as untrusted input. In particular:

- Content with HTML or script-capable media types MUST be sandboxed
  and MUST NOT be executed in the consumer's security context.
- Consumers SHOULD validate that the `data` content is well-formed
  JSON (or the expected format for the declared `type`) before
  processing.

## Privacy Considerations

Logo URLs SHOULD use Data URIs [[RFC2397]] to avoid leaking client
information through image fetch requests. Publishers SHOULD carefully
consider what information is included in `extensions` fields.

# Data Model Overview

The following diagram illustrates the relationships between the
core objects defined in this specification:

<pre class="mermaid nohighlight">
classDiagram
    class AICatalog {
        specVersion string
        entries CatalogEntry[]
        host HostInfo
        signature Signature
    }
    class HostInfo {
        displayName string
        identifier string
    }
    class CatalogEntry {
        identifier string
        displayName string
        type string
        url | data
        version string
        publisher Publisher
        trustManifests TrustManifest[]
        digest string
    }
    class Publisher {
        identifier string
        displayName string
    }
    class TrustManifest {
        contributor string
        subject Subject
        signature Signature
        trustSchema TrustSchema
        attestations Attestation[]
        provenance ProvenanceLink[]
        extensions object
    }
    class Subject {
        identifier string
        type string
        digest string
        url string
        version string
    }
    class TrustSchema {
        identifier string
        version string
        verificationMethods string[]
    }
    class Attestation {
        type string
        uri string
        digest string
    }
    class ProvenanceLink {
        relation string
        sourceId string
        sourceDigest string
    }
    class Signature {
        signer string
        profile string
        issuedAt string
        expiresAt string
        jws string
    }
    AICatalog --> "*" CatalogEntry : entries
    AICatalog --> "0..1" HostInfo : host
    CatalogEntry --> "0..1" Publisher : publisher
    CatalogEntry --> "*" TrustManifest : trustManifests
    TrustManifest --> "0..1" TrustSchema : trustSchema
    TrustManifest --> "*" Attestation : attestations
    TrustManifest --> "*" ProvenanceLink : provenance
    AICatalog --> "0..1" Signature : signature
    TrustManifest --> "0..1" Signature : signature
    TrustManifest --> "0..1" Subject : subject
    CatalogEntry --> "0..1" AICatalog : nested
</pre>

# IANA Considerations

## Media Type Registration: application/ai-catalog+json

This section registers the `application/ai-catalog+json` media type
[[RFC6838]] in the "Application" registry.

Type name:
: application

Subtype name:
: ai-catalog+json

Required parameters:
: N/A

Optional parameters:
: N/A

Encoding considerations:
: binary (UTF-8 encoded JSON [[RFC8259]])

Security considerations:
: See [Security Considerations](#security-considerations) of this document.

Interoperability considerations:
: This media type identifies a JSON document conforming to the AI
  Catalog schema defined in this specification. The document MUST
  contain `specVersion` and `entries` fields.

Published specification:
: This document

Applications that use this media type:
: AI artifact registries, agent discovery clients, package managers,
  and catalog aggregation services.

Fragment identifier considerations:
: N/A

Person & email address to contact for further information:
: Agent Card Working Group

Intended usage:
: COMMON

Restrictions on usage:
: N/A

## Link Relation Registration: ai-catalog

This section registers the `ai-catalog` link relation type in the
IANA "Link Relations" registry [[RFC8288]].

Relation Name:
: ai-catalog

Description:
: Refers to an AI Catalog document (`application/ai-catalog+json`)
  that describes AI artifacts, agents, and services associated with
  the context resource. See [Link Relation Discovery](#link-relation-discovery).

Reference:
: This document

## Well-Known URI Registration: ai-catalog.json

This section registers the `ai-catalog.json` well-known URI in the
IANA "Well-Known URIs" registry [[RFC8615]].

URI Suffix:
: ai-catalog.json

Change Controller:
: Agent Card Working Group

Specification Document:
: This document, [Well-Known URI](#well-known-uri)

Related Information:
: The well-known URI returns a JSON document with media type
  `application/ai-catalog+json` conforming to the AI Catalog schema
  defined in this specification.

# CDDL Schema

The following CDDL [[RFC8610]] defines the structural schema. The normative
prose additionally constrains contributor URIs, manifest substance, subject
binding, timestamp validity, and signature verification. The schema describes
recognized members. Under [Version Handling](#version-handling), consumers
MUST ignore unrecognized members when validating this structure, but MUST
retain them when constructing signed payloads.

## AI Catalog

```
AICatalog = {
  specVersion: text,
  ? host: HostInfo,
  entries: [* CatalogEntry],
  ? signature: Signature,
  ? additionalSignatures: any,
  ? extensions: { * text => any }
}

HostInfo = {
  displayName: text,
  ? identifier: text,
  ? documentationUrl: text,
  ? logoUrl: text
}

CatalogEntry = {
  identifier: text,
  ? displayName: text,
  type: text,
  (url: text // data: any),
  ? version: text,
  ? description: text,
  ? tags: [* text],
  ? publisher: Publisher,
  ? digest: text,
  ? trustManifests: [* TrustManifest],
  ? updatedAt: tdate,
  ? extensions: { * text => any }
}

Publisher = {
  identifier: text,
  displayName: text,
  ? identityType: text
}
```

## Trust Manifest

```
TrustManifest = {
  contributor: text,
  ? subject: Subject,
  ? signature: Signature,
  ? additionalSignatures: any,
  ? trustSchema: TrustSchema,
  ? attestations: [* Attestation],
  ? provenance: [* ProvenanceLink],
  ? extensions: { * text => any }
}

Subject = {
  identifier: text,
  type: text,
  (digest: text, ? url: text // url: text),
  ? version: text
}

Signature = {
  signer: text,
  profile: text,
  issuedAt: tdate,
  ? expiresAt: tdate,
  jws: text
}

TrustSchema = {
  identifier: text,
  version: text,
  ? governanceUri: text,
  ? verificationMethods: [* text]
}

Attestation = {
  type: text,
  uri: text,
  ? digest: text,
  ? size: uint,
  ? description: text
}

ProvenanceLink = {
  relation: text,
  sourceId: text,
  ? sourceDigest: text,
  ? registryUri: text,
  ? statementUri: text,
  ? signatureRef: text
}
```

## Official Extension Values

The value under the `https://ai-catalog.org/extensions/policy-urls` key in
`entry.extensions` has the following structure:

```
PolicyUrls = {
  ? privacyPolicyUrl: text,
  ? termsOfServiceUrl: text
}
```

# Example: Multi-Artifact Catalog with Nested Catalog

The following example shows an AI Catalog that contains a mix of
artifact types including a nested catalog packaging related artifacts.
Digest and JWS strings in illustrative examples are placeholders.

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Services Inc.",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://docs.acme-corp.com/ai"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:agent:finance-a2a",
      "version": "2.1.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance.json",
      "description": "A2A agent for financial workflows.",
      "tags": ["finance", "a2a"],
      "publisher": {
        "identifier": "did:web:acme.com",
        "displayName": "Acme Financial Corp"
      },
      "updatedAt": "2026-03-15T10:00:00Z",
      "extensions": {
        "https://ai-catalog.org/extensions/policy-urls": {
          "privacyPolicyUrl": "https://acme.com/legal/privacy",
          "termsOfServiceUrl": "https://acme.com/legal/terms"
        }
      },
      "trustManifests": [
        {
          "contributor": "did:web:acme.com",
          "attestations": [
            {
              "type": "SOC2-Type2",
              "uri": "https://trust.acme.com/reports/soc2.pdf",
              "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
            }
          ]
        }
      ]
    },
    {
      "identifier": "urn:air:acme.com:server:finance-mcp",
      "version": "1.4.0",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/mcp/server-card",
      "description": "MCP server with finance tools.",
      "tags": [
        "finance",
        "mcp"
      ],
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme.com:plugin:finance-suite",
      "displayName": "Acme Finance Suite",
      "type": "application/ai-catalog+json",
      "description": "A2A agent + MCP server + dataset for finance workflows.",
      "tags": [
        "finance",
        "suite"
      ],
      "data": {
        "specVersion": "1.0",
        "entries": [
          {
            "identifier": "urn:air:acme.com:agent:finance-a2a",
            "type": "application/a2a-agent-card+json",
            "url": "https://api.acme-corp.com/agents/finance.json"
          },
          {
            "identifier": "urn:air:acme.com:server:finance-mcp",
            "type": "application/mcp-server-card+json",
            "url": "https://api.acme-corp.com/mcp/server-card"
          },
          {
            "identifier": "urn:air:acme.com:data:market-2026q1",
            "displayName": "Market Dataset Q1 2026",
            "type": "application/parquet",
            "url": "https://data.acme-corp.com/market-2026q1.parquet",
            "trustManifests": [
              {
                "contributor": "did:web:acme.com",
                "provenance": [
                  {
                    "relation": "publishedFrom",
                    "sourceId": "oci://registry.acme.com/data/market:2026q1",
                    "sourceDigest": "sha256:99998888..."
                  }
                ]
              }
            ]
          }
        ]
      },
      "updatedAt": "2026-03-20T14:00:00Z",
      "digest": "sha256:22223333444455556666777788889999aaaabbbbccccddddeeeeffff00001111",
      "trustManifests": [
        {
          "contributor": "did:web:acme.com",
          "subject": {
            "identifier": "urn:air:acme.com:plugin:finance-suite",
            "type": "application/ai-catalog+json",
            "digest": "sha256:22223333444455556666777788889999aaaabbbbccccddddeeeeffff00001111"
          },
          "signature": {
            "signer": "did:web:acme.com",
            "profile": "did-web-v1",
            "issuedAt": "2026-03-20T14:00:00Z",
            "jws": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWI6YWNtZS5jb20jcmVsZWFzZS1zaWduaW5nLWtleSIsInR5cCI6ImFpLWNhdGFsb2ctdHJ1c3QtbWFuaWZlc3QrandzIn0..detached-jws-signature"
          }
        }
      ]
    }
  ]
}
```

# Example: Hierarchical Catalog

The following example shows how an enterprise uses nested catalog
entries to organize a large number of artifacts into browsable
categories. Each sub-catalog entry points to a separate AI Catalog
document:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:agent:assistant",
      "version": "3.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/assistant.json",
      "description": "General-purpose corporate assistant agent."
    },
    {
      "identifier": "urn:air:acme.com:catalog:finance",
      "displayName": "Finance Services",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/finance.json",
      "description": "Financial agents, MCP servers, and datasets.",
      "tags": ["finance", "trading", "compliance"]
    },
    {
      "identifier": "urn:air:acme.com:catalog:engineering",
      "displayName": "Engineering Tools",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/engineering.json",
      "description": "CI/CD agents, code review tools, and DevOps servers.",
      "tags": ["engineering", "devops", "ci-cd"]
    },
    {
      "identifier": "urn:air:acme.com:catalog:ml-models",
      "displayName": "ML Models",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/ml-models.json",
      "description": "Model cards and inference endpoints.",
      "tags": ["ml", "models", "inference"]
    }
  ]
}
```

A catalog MAY contain both direct artifact entries and nested catalog
entries. In this example, the corporate assistant agent is listed
directly while department-specific artifacts are organized into child
catalogs.

# Example: Dual-Protocol Agent (MCP + A2A)

A single agent that supports both MCP and A2A protocols can be
represented as one catalog entry whose content is a nested catalog
containing both protocol-specific entries:

```json
{
  "identifier": "urn:air:acme.com:agent:finance",
  "displayName": "Acme Finance Agent",
  "type": "application/ai-catalog+json",
  "description": "Finance agent accessible via both MCP and A2A protocols.",
  "tags": [
    "finance",
    "dual-protocol"
  ],
  "publisher": {
    "identifier": "did:web:acme.com",
    "displayName": "Acme Financial Corp"
  },
  "data": {
    "specVersion": "1.0",
    "entries": [
      {
        "identifier": "urn:air:acme.com:agent:finance:mcp",
        "type": "application/mcp-server-card+json",
        "url": "https://api.acme-corp.com/mcp/server-card"
      },
      {
        "identifier": "urn:air:acme.com:agent:finance:a2a",
        "type": "application/a2a-agent-card+json",
        "url": "https://api.acme-corp.com/agents/finance"
      }
    ]
  },
  "trustManifests": [
    {
      "contributor": "did:web:acme.com",
      "attestations": [
        {
          "type": "SOC2-Type2",
          "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
          "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
      ]
    }
  ]
}
```

The outer entry represents the logical agent as a single discoverable
artifact with its own trust metadata. The `data` field inlines a
catalog with protocol-specific entries, allowing clients to choose
MCP or A2A based on their capabilities.

# Acknowledgments

This specification was developed through collaboration among members of
the A2A and MCP protocol communities under the governance of the Linux
Foundation.
