# Example: Minimal Catalog

The simplest valid AI Catalog — just a `specVersion` and a list of entries. This is Level 1 (Minimal) conformance.

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:example.com:code-review:skill",
      "displayName": "Code Review Assistant",
      "type": "application/agent-skills+zip",
      "url": "https://skills.example.com/code-review/skill.zip"
    },
    {
      "identifier": "urn:air:example.com:weather:mcp",
      "type": "application/mcp-server-card+json",
      "url": "https://api.example.com/mcp/server-card"
    },
    {
      "identifier": "urn:air:example.com:research:a2a",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.example.com/researchAssistant"
    }
  ]
}
```

## Breakdown

**`specVersion: "1.0"`**
Identifies the version of the AI Catalog specification this document conforms to. Always present. Clients check this before processing.

**`entries`**
The list of artifacts. Each entry requires `identifier`, `type`, and `url` (or `data`).

**`identifier`**
A stable, unique string for this artifact. The recommended format is `urn:air:{publisher}:{name}[:{kind}]`. The identifier should not change when the artifact moves or is versioned.

**`type`**
What kind of artifact this is. Clients use this to decide whether they can use the artifact — without fetching it.

**`displayName`**
Optional. Notice that the MCP server and A2A agent entries omit `displayName` — those artifact formats carry their own canonical names (`title` and `name` respectively). The skill bundle entry sets `displayName` because ZIP archives don't embed a self-describing name.

**`url`**
Where to fetch the full artifact document.

## Upgrading to Level 2

Add a `host` object to identify your organization and officially reach Level 2 (Discoverable):

```json hl_lines="3 4 5 6"
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Example Corp",
    "identifier": "did:web:example.com"
  },
  "entries": [...]
}
```

Then serve the catalog at `/.well-known/ai-catalog.json` to enable automated domain-level discovery.

## Related guides

- [Creating a Catalog](../guides/creating-a-catalog.md) — detailed field reference
- [Getting Started](../getting-started.md) — step-by-step quickstart
