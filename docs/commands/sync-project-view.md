# sync-project-view

Syncs the NAMHub Projects view scope with the Studies table.

Reads all `synapseProjectId` values from the Studies table and ensures each
one is present in the ProjectView's `scopeIds`.  Projects already in scope are
left untouched; only new entries are added.

Run this command whenever a new row is added to the Studies table so that the
corresponding project appears in the MaterializedView (syn75904610) used by
the portal.

## Usage

```
namhub-dcc sync-project-view [OPTIONS]
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--studies-table-id` | `syn75404711` | Synapse ID of the Studies table |
| `--project-view-id` | `syn74589195` | Synapse ID of the NAMHub Projects view |
| `--dry-run` | — | Preview changes without applying them |
| `--auth-token` | — | Synapse PAT; falls back to `SYNAPSE_AUTH_TOKEN` env var |

## Example

```bash
# Preview what would be added
namhub-dcc sync-project-view --dry-run

# Apply changes
namhub-dcc sync-project-view
```
