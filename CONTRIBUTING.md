# Contributing

Thank you for contributing to the AI Catalog project.

This repository is currently used to develop the AI Catalog specification in
public. The canonical specification source lives in
`specification/ai-catalog.md`, and changes are reviewed through GitHub
pull requests.

## Ways To Contribute

- open an issue to report a bug, gap, or editorial problem
- start a discussion for broader design questions or cross-project alignment
- send a pull request with a proposed change to the specification, examples, or
  build tooling

The v0.9 specification is a Release Candidate for v1.0, ready for implementation
feedback before the final v1.0 specification. When reporting implementation
experience, include the specification revision or commit, relevant sections,
and a reproducible example where possible. Requirements may change before
final publication.

For substantial specification changes, open an issue or discussion first so the
proposed direction can be reviewed before detailed text is drafted.

## Repository Layout

- `GOVERNANCE.md`: project governance and working rules
- `specification/ai-catalog.md`: canonical specification source
- `specification/respec-config.json`: publication metadata and references
- `specification/examples/`: example AI Catalog documents

Use the current repository contents as the source of truth when deciding where a
change belongs.

## Development Setup

To contribute to this repository, install:

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

If your change depends on new tooling or build steps, document that in the same
pull request.

## Working On Specification Changes

Most contribution work in this repository involves editing the specification
files and updating related examples.

### What To Update

When proposing a specification change, update the relevant supporting material
in the same pull request when applicable:

- the specification source in `specification/ai-catalog.md`
- examples under `specification/examples/`
- explanatory text in `README.md`
- governance or process documents when the change affects project workflow

## Pull Request Workflow

1. Create a feature branch for your change.
2. Make the smallest coherent set of edits needed for the proposal.
3. Review the changed specification text and examples carefully before opening
  the pull request.
4. Commit using a conventional commit message.
5. Open a pull request for review.
6. Address reviewer feedback in follow-up commits.

Current repository practice is to keep work off `main` and submit changes
through pull requests.

For security reasons, pull requests opened from forks do not generate PR
previews. If preview deployment is enabled for same-repository branches, it is
limited to branches in the main repository, which typically means
maintainer-managed branches.

## Commit Guidance

- use [Conventional Commits](https://www.conventionalcommits.org/)
- keep commit scope focused
- prefer signed and signed-off commits when contributing to the project

Examples:

- `docs: clarify well-known publication rules`
- `spec: add trust metadata requirements`
- `docs: add project security policy`

## Review Expectations

All substantive changes should go through pull request review. Maintainers are
trusted to merge PRs with one peer review. The TSC can revert or block changes
with 2 (of 4) votes. Each project's maintainers are listed in
[`MAINTAINERS.md`](MAINTAINERS.md).

When proposing a specification update, explain:

- what problem the change solves
- whether it changes interoperability expectations
- whether examples or generated output changed as a result

## Questions

If you are not sure where a change belongs, start with one of the existing
public collaboration channels listed in `README.md` and propose the change in
public first.