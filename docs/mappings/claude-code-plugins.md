# Mapping to Claude Code Plugin Marketplaces

This guide describes how a
[Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
can be represented as an AI Catalog, enabling Claude Code plugins to be
discovered and indexed alongside other AI artifacts.

## Overview

A Claude Code plugin marketplace is defined by a `marketplace.json` file
that lists plugin definitions and tells Claude Code how to install them.
A plugin source is an installation locator; it is not necessarily a URL
that retrieves a single artifact document.

This guide illustrates a projection that catalogs a manifest-backed
plugin's `.claude-plugin/plugin.json` as its artifact document.

Claude Code's `strict` field controls where component definitions come
from. With `strict: true` (the default), `plugin.json` is authoritative
for component definitions, but the marketplace entry may supplement it.
With `strict: false`, the marketplace entry is the complete definition
and `plugin.json` is not required. This manifest-backed projection
applies only when `plugin.json` contains the complete component
definition. Otherwise, the operator must materialize the effective
definition or choose another artifact representation.

The guide assumes that the AI Catalog operator is also the marketplace
operator. When they are different, the catalog operator supplies its own
`host` information rather than deriving it from marketplace `owner`
metadata.

The projection is not entirely mechanical. The catalog operator assigns
globally unique entry identifiers, chooses the artifact representation
and media type, resolves installation sources to retrievable artifact
documents, and supplies any verifiable host or publisher identifiers.

## Conceptual Mapping

| Claude plugin marketplace | AI Catalog field | Mapping rule |
|:---|:---|:---|
| `marketplace.json` (whole file) | AI Catalog document | Project each plugin supported by this profile to an entry. |
| Marketplace `owner.name` | Candidate for catalog `host.displayName` | The catalog operator may use it when the same operator publishes both documents. Otherwise, the catalog operator supplies `host`. |
| Marketplace `owner.email` | No core equivalent | Contact information does not establish a verifiable `host.identifier`. |
| Marketplace `name`, `description`, `version`, and dependency policy | No direct core equivalent | These describe the Claude marketplace rather than the catalog host or an individual artifact. |
| `plugins[]` | Catalog `entries[]` | Each manifest-backed plugin becomes one entry. |
| Plugin `name` | Input to entry `identifier` | The name is scoped to its marketplace. The catalog operator assigns a globally unique identifier; it cannot derive the publisher authority from the name alone. |
| Plugin `displayName` and `description` | Entry `displayName` and `description`, conditionally | Omit them when the referenced artifact directly exposes the canonical values. Include them when clients would otherwise need to process an archive, when the artifact lacks them, or when they are intentional catalog-level values. |
| Plugin `version` | Entry `version`, conditionally | Omit it when a single referenced artifact directly exposes the canonical version. Include it when clients would otherwise need to process an archive or when catalog-level version selection requires it; when present, it must match the artifact. |
| Plugin `category`, `tags`, and `keywords` | Entry `tags[]` | Merge and deduplicate the discovery terms selected for the catalog. |
| Plugin `author.name` | Entry `publisher.displayName`, conditionally | The author may be used only when independently established as the publishing organization and paired with a verifiable identifier for that same entity. |
| Plugin `source` | Input to entry `url` or `data` | The operator resolves the installation locator, then publishes or references a complete artifact representation. A repository or directory URL is not itself an artifact document. |
| Plugin `homepage`, `repository`, and `license` | No direct core equivalent | They remain Claude metadata unless the artifact carries them or a separately defined extension preserves them. |
| Plugin component fields and `strict` | Plugin artifact content and projection policy | They determine the effective Claude component definition. Publishing a component in another artifact format requires a separately defined conversion. |
| *(not in marketplace metadata)* | Entry `type` | The catalog operator selects a type that describes the representation carried by `url` or `data`. |
| *(not established by marketplace metadata)* | Entry, host, or publisher `identifier` | The responsible catalog operator or artifact publisher supplies the identifier. |
| *(not in marketplace metadata)* | `trustManifests` | Add only independently established identity, attestation, or provenance information. Trust cannot be inferred from marketplace metadata. |

## Resolving Plugin Sources

Claude Code supports several plugin source forms. Refer to the
[Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces#plugin-sources)
for their current syntax.

Regardless of source form, an AI Catalog entry must contain a complete
artifact representation through `url` or `data`. A `url` retrieves the
artifact document represented by the entry, and that document should be
served with the media type declared by `type`. For this manifest-backed
profile, an operator resolves the installation source and publishes or
references `.claude-plugin/plugin.json` at a stable URL.

## Marketplace as AI Catalog

The following synthetic `marketplace.json` contains one plugin while
covering representative marketplace and plugin metadata:

```json
{
  "name": "example-tools",
  "description": "Claude Code plugins maintained by the Example Marketplace Team",
  "version": "2026.1",
  "owner": {
    "name": "Example Marketplace Team",
    "email": "marketplace@example.com"
  },
  "plugins": [
    {
      "name": "review-tools",
      "category": "development",
      "tags": ["code-review"],
      "source": {
        "source": "git-subdir",
        "url": "https://git.example/example/claude-plugins.git",
        "path": "plugins/review-tools",
        "ref": "v1.2.0"
      },
      "strict": true
    }
  ]
}
```

The referenced `.claude-plugin/plugin.json` provides the plugin's
canonical metadata:

```json
{
  "name": "review-tools",
  "displayName": "Review Tools",
  "description": "Adds code-review workflows to Claude Code",
  "version": "1.2.0",
  "author": {
    "name": "Example Plugin Team",
    "email": "plugins@example.com"
  },
  "homepage": "https://plugins.example/review-tools",
  "repository": "https://git.example/example/claude-plugins",
  "license": "Apache-2.0",
  "keywords": ["review", "quality"]
}
```

This projection makes the following assumptions:

- The catalog operator uses the marketplace owner's name for
  `host.displayName`.
- The operator publishes the manifest at the stable URL below and uses
  the illustrative operator-defined media type shown.
- The operator has independently verified that Example Plugin Team
  controls `plugins.example`.
- The publisher has authorized the corresponding `urn:air` identifier.

Under these assumptions, the operator can represent the marketplace as
follows:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Example Marketplace Team"
  },
  "entries": [
    {
      "identifier": "urn:air:plugins.example:claude-code:review-tools",
      "type": "application/vnd.example.claude-code-plugin+json",
      "url": "https://plugins.example/artifacts/review-tools/1.2.0/plugin.json",
      "tags": ["development", "code-review", "review", "quality"],
      "publisher": {
        "identifier": "plugins.example",
        "displayName": "Example Plugin Team"
      }
    }
  ]
}
```

The output omits the marketplace identifier and description because
they have no direct core equivalent. It leaves the plugin's canonical
display metadata, version, and descriptive links in the manifest while
merging the available discovery terms into entry `tags`. The entry
identifier, type, artifact URL, host display name, and publisher
identity are explicit operator inputs or policy decisions rather than
values mechanically derived from `marketplace.json`.

## What AI Catalog Adds to the Marketplace

The `marketplace.json` format is a lightweight directory focused on
listing and installing Claude Code plugins. Representing those plugins
in AI Catalog adds:

1. **Cross-ecosystem discovery**: Plugins become discoverable alongside
   MCP servers, A2A agents, and other artifacts through the standard
   `/.well-known/ai-catalog.json` convention, not only within Claude
   Code's `/plugin` system.

2. **Explicit artifact representation**: Each entry declares the type
   of document its `url` retrieves or its `data` contains, so consumers
   can filter and route artifacts without interpreting Claude
   installation locators.

3. **Independent identity and trust**: Publishers can add verifiable
   identifiers, attestations, and provenance when they possess that
   information. The projection does not infer those claims from owner,
   author, or source metadata.
