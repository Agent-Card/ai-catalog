---
icon: material/rocket-launch
---

# Getting Started

This guide gets a working AI Catalog live in about 5 minutes.

## What you need

- A text editor
- A web server, static hosting service, or anywhere you can serve a JSON file over HTTPS

## Step 1: Create your catalog file

Create a file named `ai-catalog.json` with the following content:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:myorg.com:mcp:my-server",
      "type": "application/mcp-server-card+json",
      "url": "https://api.myorg.com/mcp/server-card"
    }
  ]
}
```

Replace the `identifier` and `url` with your actual artifact details. The `type` field tells clients what kind of artifact this is — use `application/mcp-server-card+json` for MCP servers, `application/a2a-agent-card+json` for A2A agents, or any other appropriate media type.

!!! tip "Not sure about the type?"
    See the [Creating a Catalog](guides/creating-a-catalog.md#choosing-a-type) guide for a list of common types.

## Step 2: Serve it at the well-known path

Place `ai-catalog.json` so it is accessible at:

```
https://yourdomain.com/.well-known/ai-catalog.json
```

This is a standard [well-known URI](https://www.rfc-editor.org/rfc/rfc8615) — a predictable path that AI clients check automatically when they want to discover what a domain offers. Serve the file as static JSON over HTTPS and you're done.

See [Serving Your Catalog](guides/serving-your-catalog.md) for more details on static hosting, OCI distribution, and link-relation discovery.

## Step 3: Verify

Once deployed, verify your catalog is accessible:

```bash
curl -I https://yourdomain.com/.well-known/ai-catalog.json
```

You should see `Content-Type: application/ai-catalog+json` (or `application/json`) in the response headers, and the JSON content when you fetch it:

```bash
curl https://yourdomain.com/.well-known/ai-catalog.json
```

## What you've built

Congratulations — you have a **Level 1 (Minimal) Catalog**. Any AI client that knows to look for `/.well-known/ai-catalog.json` can now discover your artifact automatically.

AI Catalog has three conformance levels:

| Level | What it adds |
|---|---|
| **1 — Minimal** | `specVersion` + `entries` with types and URLs |
| **2 — Discoverable** | Adds a `host` object + served at `/.well-known/` |
| **3 — Trusted** | Adds publisher-authenticated entry signatures and trust evidence |

Serving the catalog at `/.well-known/ai-catalog.json` enables automated discovery. To reach Level 2, add a `host` object identifying the catalog operator:

```json hl_lines="3 4 5 6"
{
  "specVersion": "1.0",
  "host": {
    "displayName": "My Organization",
    "identifier": "did:web:myorg.com"
  },
  "entries": [...]
}
```

## Next steps

- [**Creating a Catalog**](guides/creating-a-catalog.md) — add more entries, tags, versions, and publisher info
- [**Serving Your Catalog**](guides/serving-your-catalog.md) — hosting options and `Content-Type` configuration
- [**Adding Trust**](guides/adding-trust.md) — reach Level 3 with verifiable identity and attestations
- [**Organizing Catalogs**](guides/organizing-catalogs.md) — nest catalogs for large inventories
