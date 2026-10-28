# Serving Your Catalog

AI Catalog is intentionally location-independent — a catalog is valid wherever it lives, identified by its media type and `specVersion`, not its URL. This guide covers the main distribution models.

## Static file at the well-known URI

The simplest and most common approach: serve a static JSON file at the well-known URI.

```
https://yourdomain.com/.well-known/ai-catalog.json
```

This path is a [well-known URI (RFC 8615)](https://www.rfc-editor.org/rfc/rfc8615) registered with IANA. AI clients performing domain-level discovery check this path automatically — no prior configuration needed.

Serve the file over HTTPS with the `Content-Type` header:

```
Content-Type: application/ai-catalog+json
```

This is the recommended starting point. It works with any static file host, CDN, or web server.

!!! important "HTTPS is required"
    Always serve your catalog over HTTPS (TLS 1.2+).

## Link relation discovery

Your catalog doesn't have to live at `/.well-known/` only. Any URL works — you just need to advertise it. Add an `ai-catalog` link relation to your HTTP responses or HTML pages so clients can find it:

**HTTP `Link` header:**

```
Link: <https://yourdomain.com/catalog/ai.json>; rel="ai-catalog"
```

**HTML `<link>` element:**

```html
<link rel="ai-catalog"
      href="/catalog/ai.json"
      type="application/ai-catalog+json">
```

When clients visit your site, they check for this relation first, then fall back to the well-known URI. This is useful if you want the catalog at a non-standard path, or if you need to serve different catalogs from different pages of a multi-tenant platform.

## OCI Distribution

For environments that need content-addressed storage, signing, and global replication, AI Catalog documents can be distributed through OCI registries using existing container infrastructure.

The mapping works as follows:

| AI Catalog (logical) | OCI (physical) |
|---|---|
| AI Catalog document | OCI Image Index with `artifactType: "application/ai-catalog+json"` |
| Catalog Entry | OCI Image Manifest with `artifactType` set to the entry's `type` |
| Entry artifact content | Manifest `layers[0]` blob |
| Entry metadata | Manifest `config` blob and/or `annotations` |
| Nested catalog entry | Nested OCI Image Index |
| Trust Manifest | OCI Referrer artifact attached to the entry manifest |

The logical AI Catalog format remains the authoring and consumption interface — tooling handles the OCI pack/unpack:

```
Authoring                    Distribution              Consumption
─────────                    ────────────              ───────────
ai-catalog.json  ─ pack ─►  OCI Registry  ─ unpack ─► ai-catalog.json
  entries[]                  Index/Manifests             entries[]
  trustManifests             Referrers                   trustManifests
```

Clients that fetch from `/.well-known/ai-catalog.json` or a registry API always receive the logical JSON format — they never parse OCI structures directly.

OCI distribution provides Layer 3 trust: all content is addressed by cryptographic digest, making substitution structurally impossible. See [Trust Layers](https://agent-card.github.io/ai-catalog/spec/#trust-layers) for how this fits into the progressive trust model.

For the full OCI mapping specification including the Image Index structure and Referrers API usage, refer to the [Full Specification](../specification.md).

## MCP servers

Remote (HTTP-connectable) MCP servers map to AI Catalog entries by referencing each server's [MCP Server Card](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127). Each MCP server becomes a catalog entry with `type: "application/mcp-server-card+json"` whose `url` points to the server's Server Card. A domain — or a registry — that hosts several MCP servers can publish them all as a single AI Catalog.

This enables cross-protocol discovery: a client that understands AI Catalog can discover MCP servers alongside A2A agents, datasets, and other artifact types from a single endpoint.

## Dynamic catalogs

Nothing requires a static file. A catalog can be generated dynamically by an API endpoint — for example, serving different entries based on the caller's identity or filtering by query parameters. The response just needs to be valid `application/ai-catalog+json` JSON with `specVersion` and `entries`.

## Verifying your catalog

After deploying, verify:

```bash
# Check headers and status
curl -I https://yourdomain.com/.well-known/ai-catalog.json

# Fetch and validate the JSON
curl -s https://yourdomain.com/.well-known/ai-catalog.json | python3 -m json.tool
```

A well-served catalog returns HTTP 200, a `Content-Type` containing `json`, and a body with `specVersion` and `entries` fields.
