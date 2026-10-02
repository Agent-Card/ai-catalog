---
icon: material/code-braces
---

# Implementations

This page lists implementations and tooling for the AI Catalog specification.

## Official

These implementations are maintained by the Agent Card Working Group or its member organisations.

- [spec-works/ai-catalog](https://github.com/spec-works/ai-catalog) (C#, Python)
- [ai-catalog-go-sdk](https://github.com/agntcy/ai-catalog-go-sdk/) (Go)
- [ai-catalog-rust](https://github.com/agntcy/ai-catalog-rust) (Rust)
- [tomevault-io/ai-catalog-reference](https://github.com/tomevault-io/ai-catalog-reference) (Python, Trust Manifest signer/verifier)
- [AI Catalog](https://ai-catalog.outshift.io/) (testbed service)

## Community Projects

Community-built tools, libraries, and integrations. Listed here to help discovery — not formally endorsed by the working group.

- [Apicurio Registry](https://github.com/Apicurio/apicurio-registry) (Java/Quarkus API and schema registry with experimental AI Catalog publishing for registered agent and tool metadata)
- [AgentAvow](https://github.com/AgentAvow/AgentAvow) (Python; publishes a signed `/.well-known/ai-catalog.json` for its MCP server, ES256 under `did:web:agentavow.com` per the did:web Publisher Profile, with a build, sign and strict-verify script at `scripts/ai_catalog_wellknown.py`; live at https://agentavow.com/.well-known/ai-catalog.json)

!!! tip "Add your project"
    Have an implementation to share? Open a pull request to add it here.
