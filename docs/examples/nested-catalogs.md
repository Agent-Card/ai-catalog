# Example: Nested Catalogs

This example shows how an enterprise organizes a large artifact inventory using nested catalogs. The root catalog provides an overview; each department maintains its own sub-catalog.

## Root catalog

The root catalog is served at `/.well-known/ai-catalog.json`:

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
      "identifier": "urn:air:acme-corp.com:assistant",
      "version": "3.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/assistant.json",
      "description": "General-purpose corporate assistant agent."
    },
    {
      "identifier": "urn:air:acme-corp.com:finance",
      "displayName": "Finance Services",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/finance.json",
      "description": "Financial agents, MCP servers, and datasets.",
      "tags": ["finance", "trading", "compliance"]
    },
    {
      "identifier": "urn:air:acme-corp.com:engineering",
      "displayName": "Engineering Tools",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/engineering.json",
      "description": "CI/CD agents, code review tools, and DevOps servers.",
      "tags": ["engineering", "devops", "ci-cd"]
    }
  ]
}
```

## Finance sub-catalog

The Finance team owns and hosts `finance.json`. It can be updated independently of the root:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Finance Team",
    "identifier": "did:web:finance.acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:finance-a2a",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance.json",
      "tags": ["finance", "trading"]
    },
    {
      "identifier": "urn:air:acme-corp.com:finance-mcp",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/mcp/server-card",
      "tags": ["finance", "mcp"]
    },
    {
      "identifier": "urn:air:acme-corp.com:market-2026q1",
      "displayName": "Market Dataset Q1 2026",
      "type": "application/parquet",
      "url": "https://data.acme-corp.com/market-2026q1.parquet",
      "tags": ["dataset", "finance"]
    }
  ]
}
```

## How it works

**Direct entries** (like `urn:air:acme-corp.com:assistant`) appear directly in the root catalog. Clients see them without any additional fetching. The `displayName` is omitted for A2A entries since the agent card itself carries a canonical name.

**Nested catalog entries** (like `urn:air:acme-corp.com:finance`) have `type: "application/ai-catalog+json"` and set `displayName` since catalogs don't embed their own name. Clients follow the `url` to fetch the sub-catalog and process it as another AI Catalog.

**Dataset entries** set `displayName` since Parquet files don't carry a human-readable name.

**Independent ownership**: each sub-catalog has its own `host` object. The Finance team updates their catalog without touching the root.

**Mix and match**: a catalog can contain both direct entries and nested catalog references in the same `entries` array.

## Client traversal

A client that wants all artifacts walks the tree:

1. Fetch root at `/.well-known/ai-catalog.json`
2. Find entries with `type: "application/ai-catalog+json"` → these are sub-catalogs
3. Fetch each sub-catalog URL
4. Repeat (up to depth limit of 4)
5. Collect all non-catalog entries

See [Consuming Catalogs — Handling nested catalogs](../guides/consuming-catalogs.md#handling-nested-catalogs) for implementation details including cycle detection.

## Related guides

- [Organizing Catalogs](../guides/organizing-catalogs.md)
- [Consuming Catalogs](../guides/consuming-catalogs.md)
