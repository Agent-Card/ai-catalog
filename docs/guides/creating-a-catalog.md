# Creating a Catalog

This guide covers everything you need to author a well-formed AI Catalog.

## Catalog structure

An AI Catalog is a JSON object with two required top-level fields:

```json
{
  "specVersion": "1.0",
  "entries": []
}
```

`specVersion`
:   The version of the AI Catalog specification this document conforms to, in `"Major.Minor"` format. Use `"1.0"` for the current version.

`entries`
:   An ordered array of Catalog Entry objects. May be empty.

Two optional top-level fields round out a complete catalog:

`host`
:   Identifies the organization operating this catalog. Required for [Level 2 (Discoverable)](../getting-started.md#what-youve-built) conformance.

`extensions`
:   A map of custom or vendor-specific extensions, keyed by a URL or reverse-DNS name. See [Extensions](#extensions).

## Adding a `host` object

The `host` object identifies who operates the catalog. Adding it upgrades you to Level 2 (Discoverable):

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Corp",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://docs.acme-corp.com/ai"
  },
  "entries": [...]
}
```

`displayName` is required on the host. All other host fields are optional:

| Field | Description |
|---|---|
| `identifier` | Verifiable identifier — a DID, domain name, or other URI |
| `documentationUrl` | URL to your AI platform documentation |
| `logoUrl` | URL to your logo. Use a Data URI to avoid leaking client info through image requests |

## Catalog entries

Each entry in the `entries` array describes one AI artifact.

### Required fields

Every entry must have these three things:

```json
{
  "identifier": "urn:air:acme-corp.com:mcp:weather",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme-corp.com/mcp/server-card"
}
```

`identifier`
:   A stable, globally unique string that identifies this artifact. The `urn:air:{domain}:{namespace}:{name}` format is highly recommended for open or federated systems. The identifier should remain stable across versions and catalog locations.

`type`
:   The media type of the artifact. This is how clients determine what kind of artifact this is without fetching it.

`url` **or** `data`
:   Exactly one of these must be present. Use `url` to reference an external document, or `data` to embed the artifact inline (see [url vs data](#url-vs-data)).

### Choosing a type {#choosing-a-type}

| Artifact | `type` value |
|---|---|
| AI Catalog (nested) | `application/ai-catalog+json` |
| Agent Card (generic) | `application/agent-card+json` |
| A2A Agent Card | `application/a2a-agent-card+json` |
| MCP Server Card | `application/mcp-server-card+json` |
| Agent Skill metadata (JSON) | `application/agent-skills+json` |
| Agent Skill (Markdown) | `application/agent-skills+md` |
| Agent Skill (ZIP bundle) | `application/agent-skills+zip` |
| Agent Skill (gzipped tarball) | `application/agent-skills+gzip` |
| Agent Plugin (ZIP bundle) | `application/agent-plugins+zip` |
| Agent Plugin (gzipped tarball) | `application/agent-plugins+gzip` |
| Dataset | `application/parquet`, `text/csv`, or appropriate type |

An **Agent Plugin** ([agent-plugins.org](https://agent-plugins.org)) is directory-based. For AI Catalog delivery, archive the complete plugin directory as ZIP or gzipped tar, point the entry's `url` to that archive, and copy `plugin.json`'s `name`, `description`, and `keywords` to `displayName`, `description`, and `tags`, respectively; clients extract the archive before loading the plugin.

This list is not exhaustive — AI Catalog accepts any string as a `type` value. The spec is intentionally artifact-agnostic.

### Optional fields

Enrich your entries with additional metadata:

| Field | Type | Description |
|---|---|---|
| `displayName` | string | Human-readable name override (see below) |
| `description` | string | Short description of what this artifact does |
| `tags` | string[] | Keywords for filtering and discovery |
| `version` | string | Artifact version. Semantic versioning recommended |
| `updatedAt` | string | ISO 8601 timestamp of last modification |
| `publisher` | object | Who publishes this artifact (see [Publisher object](#publisher-object)) |
| `trustManifest` | object | Trust and identity metadata (see [Adding Trust](adding-trust.md)) |
| `extensions` | object | Named extensions (see [Extensions](#extensions)) |

### When to set `displayName`

`displayName` is optional and its use depends on the artifact type:

- **Omit it** for artifacts that embed their own canonical name — such as A2A Agent Cards (which have a `name` field) and MCP Server Cards (which have a `title` field). Clients fall back to the artifact's own name when `displayName` is absent.
- **Set it** for artifacts that do not carry a human-readable name — such as datasets (`application/parquet`) or skill bundles (`application/agent-skills+zip`).
- **Set it** when you deliberately want to override the artifact's own name in this catalog context.

When `displayName` is present, it always takes precedence over the artifact's own name.

A fully populated entry for an artifact that benefits from `displayName`:

```json
{
  "identifier": "urn:air:acme-corp.com:data:market-2026q1",
  "displayName": "Market Dataset Q1 2026",
  "type": "application/parquet",
  "url": "https://data.acme-corp.com/market-2026q1.parquet",
  "description": "OHLCV equity data for Q1 2026.",
  "tags": ["finance", "dataset"],
  "version": "1.0.0",
  "updatedAt": "2026-04-01T09:00:00Z",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  }
}
```

## `url` vs `data`

Each entry must provide its artifact content via exactly one of these fields:

`url`
:   A URL where clients fetch the full artifact. The server at that URL should respond with the content type declared in `type`. This is the recommended approach for most cases.

`data`
:   The complete artifact document embedded directly as a JSON value. The structure is determined by the `type` field and is opaque to the AI Catalog spec.

**Use `url` when:**
- The artifact is large
- The artifact is updated independently of the catalog
- You want to keep the catalog file small

**Use `data` when:**
- You want a fully self-contained catalog
- You're packaging a multi-artifact bundle (see [Organizing Catalogs](organizing-catalogs.md#multi-artifact-packaging))
- The artifact is small and unlikely to change independently

## Identifier best practices

The spec highly recommends the `urn:air:{domain}:{namespace}:{name}` format for open and federated systems:

```
urn:air:acme-corp.com:mcp:weather        # MCP server
urn:air:acme-corp.com:a2a:finance        # A2A agent
urn:air:acme-corp.com:skill:code-review  # skill bundle
urn:air:acme-corp.com:catalog:finance    # nested catalog
finance-agent                            # Avoid: not globally unique
```

- `{domain}` — the domain name of the publishing organization
- `{namespace}` — logical category, can be colon-separated (`finance:agent`)
- `{name}` — stable, unique name within the publisher's namespace

Keep identifiers stable across catalog locations and versions. Anchoring to a domain you own prevents typosquatting.

## Multi-version entries

A catalog may contain multiple entries with the same `identifier` but different `version` values, representing a version history:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:a2a:finance",
      "version": "2.1.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.acme-corp.com/finance/v2.1.json",
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme-corp.com:a2a:finance",
      "version": "2.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.acme-corp.com/finance/v2.0.json",
      "updatedAt": "2026-01-20T08:00:00Z"
    }
  ]
}
```

When `version` is present, the combination of `identifier` + `version` must be unique. Clients looking for the latest version should sort by `version` (semver) or `updatedAt` and take the most recent.

## Publisher object

The `publisher` field on an entry identifies who publishes that artifact:

```json
"publisher": {
  "identifier": "did:web:acme-corp.com",
  "displayName": "Acme Financial Corp",
  "identityType": "did"
}
```

`identifier` and `displayName` are required. `identityType` is optional and provides a hint for resolving the identifier (`"did"`, `"dns"`, etc.).

## Extensions

Both the top-level catalog object and individual entries support an `extensions` map for custom properties. Each key identifies an extension and must be a URL or a reverse-DNS name. Consumers that do not recognize an extension key must ignore it without error.

For generic key/value properties, use the official `https://ai-catalog.org/extensions/metadata` extension:

```json
"extensions": {
  "https://ai-catalog.org/extensions/metadata": {
    "region": "us-east-1",
    "sla": "99.9%",
    "license": "Apache-2.0"
  }
}
```

The value of this official extension is a schemaless object for generic key/value properties.

## Complete example

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://docs.acme-corp.com/ai"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:mcp:weather",
      "type": "application/mcp-server-card+json",
      "description": "Real-time weather data and forecasts.",
      "tags": ["weather", "data"],
      "version": "1.2.0",
      "url": "https://api.acme-corp.com/mcp/server-card",
      "updatedAt": "2026-04-01T09:00:00Z",
      "publisher": {
        "identifier": "did:web:acme-corp.com",
        "displayName": "Acme Corp"
      }
    },
    {
      "identifier": "urn:air:acme-corp.com:a2a:research",
      "type": "application/a2a-agent-card+json",
      "description": "Deep-research agent with citation support.",
      "tags": ["research", "analysis"],
      "url": "https://agents.acme-corp.com/research"
    },
    {
      "identifier": "urn:air:acme-corp.com:data:market-2026q1",
      "displayName": "Market Dataset Q1 2026",
      "type": "application/parquet",
      "description": "OHLCV equity data for Q1 2026.",
      "tags": ["finance", "dataset"],
      "url": "https://data.acme-corp.com/market-2026q1.parquet"
    }
  ]
}
```

## Next steps

- [Serving Your Catalog](serving-your-catalog.md) — deploy and configure hosting
- [Organizing Catalogs](organizing-catalogs.md) — nested catalogs for large inventories
- [Adding Trust](adding-trust.md) — identity, attestations, and provenance
