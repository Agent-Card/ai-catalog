# Example: Multi-Protocol Agent

An agent that supports both MCP and A2A protocols can be represented as a single logical entry whose content is a nested catalog containing both protocol-specific entries.

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Financial Corp",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:agent:finance",
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
            "identifier": "urn:air:acme-corp.com:mcp:finance",
            "type": "application/mcp-server-card+json",
            "url": "https://api.acme-corp.com/mcp/server-card"
          },
          {
            "identifier": "urn:air:acme-corp.com:a2a:finance",
            "type": "application/a2a-agent-card+json",
            "url": "https://api.acme-corp.com/agents/finance"
          }
        ]
      },
      "trustManifest": {
        "identity": "did:web:acme-corp.com",
        "attestations": [
          {
            "type": "SOC2-Type2",
            "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
            "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
          }
        ]
      }
    }
  ]
}
```

## How it works

**The outer entry** (`urn:air:acme-corp.com:agent:finance`) represents the logical agent. It has `type: "application/ai-catalog+json"`, meaning its content is itself a catalog. Clients that don't need to know about protocols can stop here — they see one agent with a name, description, tags, and trust metadata.

The outer entry sets `displayName` because a catalog document has no intrinsic name of its own — unlike an A2A Agent Card or MCP Server Card which embed their own names. The inner protocol-specific entries omit `displayName` since their native formats carry canonical names.

**The `data` field** inlines the inner catalog directly (instead of referencing it via `url`). This makes the entry self-contained — clients don't need a second network request to see the protocol-specific entries.

**The inner entries** provide protocol-specific access points. A client that speaks MCP fetches the MCP Server Card; one that speaks A2A fetches the A2A Agent Card. The outer entry's trust metadata applies to both.

## When to use this pattern

Use dual-protocol packaging when:

- A single logical service is accessible via more than one AI protocol
- You want to expose one identity and one set of trust claims for both protocol endpoints
- You're listing an agent in a catalog where some clients speak MCP and others speak A2A

## Variation: using `url` instead of `data`

If the inner catalog is large or updated independently, reference it via `url` instead of embedding it:

```json
{
  "identifier": "urn:air:acme-corp.com:agent:finance",
  "displayName": "Acme Finance Agent",
  "type": "application/ai-catalog+json",
  "url": "https://acme-corp.com/agents/finance-protocols.json"
}
```

The document at that URL is a full AI Catalog containing the MCP and A2A entries.

## Related guides

- [Organizing Catalogs](../guides/organizing-catalogs.md#dual-protocol-agents)
- [Adding Trust](../guides/adding-trust.md)
