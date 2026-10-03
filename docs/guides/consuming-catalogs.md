# Consuming Catalogs

This guide covers how to discover, fetch, and process AI Catalog documents as a client developer.

## Discovery flow

When you have a domain and want to find its AI Catalog, follow this sequence:

1. **Fetch the target URL** and inspect HTTP response headers for a `Link` header with `rel="ai-catalog"`:
   ```
   Link: <https://example.com/catalog/ai.json>; rel="ai-catalog"
   ```

2. **If no `Link` header**, and the response is HTML, parse the document for a `<link>` element:
   ```html
   <link rel="ai-catalog" href="/catalog/ai.json">
   ```

3. **If neither**, fall back to the well-known URI:
   ```
   GET https://example.com/.well-known/ai-catalog.json
   ```

4. **Validate the response**: check that `Content-Type` contains `json`, parse the body, and confirm it has a `specVersion` field. If valid, this is the site's AI Catalog.

## Parsing the catalog

A valid catalog has at minimum:

```json
{
  "specVersion": "1.0",
  "entries": [...]
}
```

Always check `specVersion` first:

- If the **major version** matches what you support, proceed (ignore unrecognized fields)
- If the **major version** is higher than you support, reject with an informative error — don't silently misinterpret it
- Minor version differences (e.g., you support 1.0, the catalog says 1.1) are safe to ignore

```python
import json, urllib.request

def fetch_catalog(url):
    with urllib.request.urlopen(url) as resp:
        catalog = json.load(resp)

    major = int(catalog["specVersion"].split(".")[0])
    if major > 1:  # replace 1 with your supported major version
        raise ValueError(f"Unsupported catalog version: {catalog['specVersion']}")

    return catalog
```

## Filtering by type

The `type` field on each entry tells you what kind of artifact it is, without needing to fetch it:

```python
def find_mcp_servers(catalog):
    return [
        entry for entry in catalog["entries"]
        if entry["type"] == "application/mcp-server-card+json"
    ]

def find_a2a_agents(catalog):
    return [
        entry for entry in catalog["entries"]
        if entry["type"] == "application/a2a-agent-card+json"
    ]
```

Ignore entries with unknown `type` values — new types will be added over time.

## Resolving a display name

`displayName` is optional on entries. To get a human-readable name, resolve in this order:

1. `displayName` on the entry, if present — always takes precedence
2. The artifact's own canonical name, if you've already fetched it (e.g., `name` on an A2A Agent Card, `title` on an MCP Server Card)
3. The trailing segment of the `identifier` as a fallback (e.g., `urn:air:example.com:mcp:weather` → `weather`)

Avoid fetching an artifact at render time solely to obtain a name — resolve and cache the name at ingestion instead.

## Resolving artifacts

Each entry provides its artifact via either `url` or `data`:

```python
def resolve_artifact(entry):
    if "data" in entry:
        # Artifact is inline — use directly
        return entry["data"]

    if "url" in entry:
        # Fetch from the URL
        with urllib.request.urlopen(entry["url"]) as resp:
            return json.load(resp)

    raise ValueError("Entry has neither url nor data")
```

When fetching from `url`, the server should respond with the content type declared in the entry's `type` field.

## Handling nested catalogs

An entry with `type: "application/ai-catalog+json"` is itself a catalog. To get all artifacts, recurse into it:

```python
def collect_all_entries(catalog_url, max_depth=4, _visited=None, _depth=0):
    if _depth >= max_depth:
        return []

    if _visited is None:
        _visited = set()

    if catalog_url in _visited:
        return []  # cycle detected
    _visited.add(catalog_url)

    catalog = fetch_catalog(catalog_url)
    results = []

    for entry in catalog.get("entries", []):
        if entry["type"] == "application/ai-catalog+json":
            # Recurse into nested catalog
            nested_url = entry.get("url")
            if nested_url:
                results.extend(
                    collect_all_entries(
                        nested_url, max_depth, _visited, _depth + 1
                    )
                )
        else:
            results.append(entry)

    return results
```

!!! warning "Enforce depth limits"
    Always enforce a maximum nesting depth (4 is recommended) and track visited URLs to prevent circular references. A malicious or misconfigured catalog could otherwise cause infinite loops.

## Multi-version resolution

When multiple entries share the same `identifier`, they represent different versions of the same artifact. To get the latest:

```python
from packaging.version import Version

def latest_entries(entries):
    """Return only the latest version of each unique identifier."""
    by_id = {}

    for entry in entries:
        eid = entry["identifier"]
        if eid not in by_id:
            by_id[eid] = entry
            continue

        existing = by_id[eid]
        # Prefer by semver version, fall back to updatedAt
        try:
            if Version(entry.get("version", "0")) > Version(existing.get("version", "0")):
                by_id[eid] = entry
        except Exception:
            if entry.get("updatedAt", "") > existing.get("updatedAt", ""):
                by_id[eid] = entry

    return list(by_id.values())
```

## TypeScript example

```typescript
interface CatalogEntry {
  identifier: string;
  type: string;
  url?: string;
  data?: unknown;
  displayName?: string;
  version?: string;
  updatedAt?: string;
  tags?: string[];
  description?: string;
}

interface AICatalog {
  specVersion: string;
  entries: CatalogEntry[];
  host?: { displayName: string; identifier?: string };
}

async function discoverCatalog(domain: string): Promise<AICatalog | null> {
  const wellKnown = `https://${domain}/.well-known/ai-catalog.json`;
  try {
    const resp = await fetch(wellKnown);
    if (!resp.ok) return null;
    const catalog: AICatalog = await resp.json();
    if (!catalog.specVersion || !Array.isArray(catalog.entries)) return null;
    return catalog;
  } catch {
    return null;
  }
}

function filterByType(catalog: AICatalog, type: string): CatalogEntry[] {
  return catalog.entries.filter(e => e.type === type);
}
```

## Error handling

Be defensive when consuming catalogs from unknown sources:

- **Missing fields**: check for `specVersion` and `entries` before processing; skip entries missing `identifier` or `type`
- **Unknown `type` values**: ignore them — don't fail
- **Unreachable URLs**: log and skip; don't abort the whole catalog
- **Invalid JSON**: catch parse errors and treat the catalog as unavailable
- **Circular references**: track visited URLs and enforce depth limits (see above)
- **Untrusted `data` content**: treat inline `data` as untrusted input; don't execute content with script-capable media types

## Trust verification

If an entry has `trustManifests`, treat their identity keys as claimed contributors until verified. Check the entry's `signatures`, their field coverage and signer authority, and any referenced evidence before accepting those claims. See [Adding Trust](adding-trust.md) for details on the trust model and verification steps.
