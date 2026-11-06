# Organizing Catalogs

AI Catalog supports nesting — a catalog entry can point to another catalog. This enables hierarchical organization, multi-artifact packaging, and federated publishing.

## When to nest

Use nested catalogs when:

- **Your catalog is large** — split into manageable, independently-updatable sub-catalogs
- **You have departmental structure** — each team owns and hosts their own catalog
- **You're packaging related artifacts** — group an A2A agent, MCP server, and dataset together as a single bundle
- **You want federation** — sub-catalogs maintained by different publishers

A flat catalog is simpler. Nest only when you have a clear organizational reason.

## Nested catalog entries

An entry whose `type` is `application/ai-catalog+json` is a nested catalog reference. Clients discover it, fetch the URL, and process the result as another catalog:

```json
{
  "identifier": "urn:air:acme-corp.com:finance",
  "displayName": "Finance Services",
  "type": "application/ai-catalog+json",
  "url": "https://acme-corp.com/catalogs/finance.json",
  "description": "Financial agents, MCP servers, and datasets.",
  "tags": ["finance", "trading", "compliance"]
}
```

The nested catalog at that URL is a full AI Catalog document with its own `specVersion`, `host`, and `entries`.

!!! note
    `displayName` is recommended on nested catalog entries since a catalog document doesn't have an intrinsic name the way an A2A Agent Card or MCP Server Card does.

## Hierarchical organization

An enterprise can organize a large artifact inventory into browsable categories:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com"
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
    },
    {
      "identifier": "urn:air:acme-corp.com:ml-models",
      "displayName": "ML Models",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/ml-models.json",
      "description": "Model cards and inference endpoints.",
      "tags": ["ml", "models", "inference"]
    }
  ]
}
```

A catalog can mix direct artifact entries and nested catalog entries. Here the corporate assistant is listed directly while department artifacts are organized into child catalogs.

## Multi-artifact packaging {#multi-artifact-packaging}

Bundle related artifacts together using the `data` field to embed the child catalog inline:

```json
{
  "identifier": "urn:air:acme-corp.com:finance-suite",
  "displayName": "Finance Suite",
  "type": "application/ai-catalog+json",
  "description": "Finance plugin — includes A2A agent, MCP server, and dataset.",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "data": {
    "specVersion": "1.0",
    "entries": [
      {
        "identifier": "urn:air:acme-corp.com:finance-a2a",
        "type": "application/a2a-agent-card+json",
        "url": "https://api.acme-corp.com/agents/finance.json"
      },
      {
        "identifier": "urn:air:acme-corp.com:finance-mcp",
        "type": "application/mcp-server-card+json",
        "url": "https://api.acme-corp.com/mcp/server-card"
      },
      {
        "identifier": "urn:air:acme-corp.com:market-2026q1",
        "displayName": "Market Dataset Q1 2026",
        "type": "application/parquet",
        "url": "https://data.acme-corp.com/market-2026q1.parquet"
      }
    ]
  }
}
```

The `data` field inlines the child catalog directly, making the package self-contained.

## Dual-protocol agents

An agent that supports both MCP and A2A can be represented as one logical entry containing protocol-specific sub-entries:

```json
{
  "identifier": "urn:air:acme-corp.com:finance-agent",
  "displayName": "Acme Finance Agent",
  "type": "application/ai-catalog+json",
  "description": "Finance agent accessible via both MCP and A2A protocols.",
  "tags": ["finance", "dual-protocol"],
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "data": {
    "specVersion": "1.0",
    "entries": [
      {
        "identifier": "urn:air:acme-corp.com:finance-mcp",
        "type": "application/mcp-server-card+json",
        "url": "https://api.acme-corp.com/mcp/server-card"
      },
      {
        "identifier": "urn:air:acme-corp.com:finance-a2a",
        "type": "application/a2a-agent-card+json",
        "url": "https://api.acme-corp.com/agents/finance.json"
      }
    ]
  }
}
```

The outer entry is the logical agent. Clients discover it and choose the protocol they support from the inner entries.

## Federation model

Each sub-catalog is an independent document:

- **Authored independently**: the finance team manages `finance.json`; the engineering team manages `engineering.json`
- **Hosted anywhere**: sub-catalogs don't need to live on the same server as the parent
- **Updated independently**: a change to a sub-catalog doesn't require updating the parent
- **Trusted independently**: each sub-catalog can carry its own `host` and Trust Manifests

The parent catalog entry just holds a stable `url` pointing to the sub-catalog. As long as that URL stays valid, the federation works.

## Depth limits

Clients processing nested catalogs should enforce a maximum nesting depth. **A depth of 4 is recommended.**

At depth 4 you can have: root → category → subcategory → bundle → individual artifacts. This covers virtually all real-world organizational structures.

Also track visited URLs to prevent circular references (e.g., catalog A → catalog B → catalog A). See [Consuming Catalogs](consuming-catalogs.md#handling-nested-catalogs) for implementation guidance.
