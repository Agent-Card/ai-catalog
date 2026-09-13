# Mapping to Distribution Substrates

The AI Catalog specification defines a **logical format**: a JSON
document with `entries`, `displayName`, `type`, and `trustManifests`
fields that are immediately meaningful to anyone working with AI
artifacts. Authors write simple JSON. APIs serve simple JSON. Clients
consume simple JSON.

That logical format can be **physically distributed** over more than one
substrate — an OCI registry, an [[xRegistry]] registry, or a plain HTTP
server. Each substrate has its own data model and its own native
capabilities. To keep the logical format authoritative and to avoid
diverging, substrate-specific dialects, every binding defined by this
specification MUST satisfy the same contract: packing a logical document
into the substrate and unpacking it again MUST reproduce an equivalent
logical document.

```
Authoring                      Distribution                    Consumption
─────────                      ────────────                    ───────────
ai-catalog.json   ──pack──►   OCI / xRegistry / HTTP  ──unpack──►   ai-catalog.json
  entries[]                     substrate-native form                entries[]
  trustManifests                                                     trustManifests
```

This separation keeps authoring and consumption simple: publishers and
clients work with domain vocabulary (`entries`, `displayName`,
`type`, `trustManifests`), while infrastructure that wants
content-addressing, signing, replication, or registry APIs uses whichever
binding below matches its substrate.

## Binding Invariants

A conforming binding MUST preserve each of the following invariants. This
list — not any single substrate's vocabulary — is the conformance bar for
a pack/unpack round-trip.

| Logical concept | Invariant a binding MUST preserve |
|:---|:---|
| Entry identity (`identifier`) | A stable, addressable identity for each entry |
| Artifact content + `type` | The artifact bytes are retrievable together with their media type |
| Catalog structure / nesting | Nested catalogs remain navigable as a hierarchy |
| Trust Manifest association | An entry's Trust Manifests and their contributor identity keys are discoverable from that entry |
| Content integrity | The served bytes are verifiably bound to `entry.digest` |
| Signing | The Trust Manifests' authenticity is cryptographically verifiable |

## Delegate, Don't Duplicate

Substrates differ in what they can express natively. OCI is
content-addressed and has first-class signing (Cosign/Notation);
xRegistry is a hierarchical resource API with versioning and
cross-referencing but no native digest or signature primitive.

To avoid expressing the same guarantee twice, a binding **delegates** an
invariant to a native substrate primitive when one exists, and otherwise
**carries** it in the logical document. A binding MUST NOT restate,
in substrate vocabulary, a guarantee it has delegated, and MUST NOT drop
a guarantee the substrate cannot express.

| Invariant | OCI primitive (delegate) | xRegistry primitive (delegate) | Carried fallback |
|:---|:---|:---|:---|
| Identity | Repository path + digest | `resourceid` / `xid` | `entry.identifier` |
| Content + media type | `layers[0]` + `artifactType` | Resource document + `contenttype` | Entry artifact + `type` |
| Nesting | Nested Image Index | Nested Group / `xref` | Nested entry |
| Manifest association | Referrers API (`subject`) | `xref` / extension attribute | Inline `trustManifests` |
| Content integrity | Content-addressed digest | *(none — carried)* | `entry.digest` |
| Signing | Cosign / Notation referrer | *(none — carried)* | Entry `signatures` |

The [OCI Distribution](oci-distribution.md) and [xRegistry](xregistry.md)
mappings are concrete bindings of this contract. The OCI binding delegates
the most (identity, content integrity, signing); the xRegistry binding
delegates structure, identity, and discovery but carries content integrity
and signing because xRegistry has no native primitive for them.

