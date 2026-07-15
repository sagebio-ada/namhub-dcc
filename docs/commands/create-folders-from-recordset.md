# `create-folders-from-recordset`

[← Back to docs index](../index.md)

Creates a Synapse Folder for each row of a Synapse RecordSet, using a column
value as the folder name, all under one parent container.

RecordSets are backed by a CSV file, so this command downloads that file and
reads it with pandas to get the rows. Folders that already exist under the
parent (matched by name) are skipped, so the command is safe to re-run.

## Usage

```bash
namhub-dcc create-folders-from-recordset \
    --record-set-id syn76265683 \
    --name-column DatasetName \
    --parent-id syn87654321
```

Add `--dry-run` to preview what would be created without creating anything.

## Options

| Option | Required | Description |
| --- | --- | --- |
| `--record-set-id` | Yes | Synapse ID of the RecordSet to read rows from (e.g. `syn76265683`). |
| `--name-column` | Yes | Name of the RecordSet column whose value becomes each folder's name. |
| `--parent-id` | Yes | Synapse ID of the container that new folders are created under. |
| `--auth-token` | No | Synapse personal access token. Falls back to `SYNAPSE_AUTH_TOKEN` or `~/.synapseConfig`. |
| `--download-dir` | No | Directory to download the RecordSet's underlying CSV to. Defaults to a temporary directory. |
| `--dry-run` | No | Print what would be created without creating anything. |

## Behavior notes

- Rows with a blank or `NaN` value in `--name-column` are skipped.
- A folder is only skipped as "already existing" if its name exactly matches
  an existing folder directly under `--parent-id`.
- If a folder fails to create (e.g. an invalid name), the error is logged and
  the command continues with the remaining rows; the final summary line
  reports counts for `created`, `skipped_existing`, `skipped_blank`, and
  `failed`.

## Source

[`src/namhub_dcc/commands/create_folders_from_recordset.py`](../../src/namhub_dcc/commands/create_folders_from_recordset.py)
