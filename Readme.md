# namhub-dcc

Scripts to automate steps in NAMHub data coordination, packaged as an
installable command-line tool (`namhub-dcc`) so anyone with a Synapse
account can run them.

## Installation

Requires Python 3.10+ and a [Synapse](https://www.synapse.org) account.

```bash
pip install git+https://github.com/sagebio-ada/namhub-dcc.git
```

This installs the `namhub-dcc` command.

## Authentication

Every command needs Synapse credentials, resolved in this order:

1. An explicit `--auth-token` argument.
2. The `SYNAPSE_AUTH_TOKEN` environment variable.
3. Cached credentials in `~/.synapseConfig`.

You can generate a personal access token from your Synapse account settings
page ("Personal Access Tokens").

```bash
export SYNAPSE_AUTH_TOKEN=<your-personal-access-token>
```

## Commands

Run `namhub-dcc --help` to list all commands, or `namhub-dcc <command> --help`
for a command's options.

### `create-folders-from-recordset`

Creates a Synapse Folder for each row of a Synapse RecordSet, using a column
value as the folder name, all under one parent container. RecordSets are
backed by a CSV file, so the command downloads that file and reads it with
pandas to get the rows.

```bash
namhub-dcc create-folders-from-recordset \
    --record-set-id syn76265683 \
    --name-column DatasetName \
    --parent-id syn87654321
```

Add `--dry-run` to preview without creating anything.

### `create-landscape-task`

Creates a NAMHub "Landscape Task" in a Synapse project folder: a RecordSet
bound to the `NAMhub-Landscape` JSON schema, paired with a CurationTask and
a Grid view, via `synapseclient.extensions.curator.create_record_based_metadata_task`.

```bash
namhub-dcc create-landscape-task \
    --project-id syn12345678 \
    --folder-id syn74568176 \
    --pi-name "Jane Doe"
```

The RecordSet/CurationTask names, instructions, schema URI, and upsert key
all have NAMHub defaults and can be overridden; see
`namhub-dcc create-landscape-task --help`. The same logic is available as a
plain Python function, `namhub_dcc.landscape.create_landscape_task`, for
scripting (e.g. creating tasks across many folders in a loop).

## Development

Clone the repo and install it in editable mode with dev dependencies:

```bash
git clone https://github.com/sagebio-ada/namhub-dcc.git
cd namhub-dcc
pip install -e .
```

New scripts should be added as a new module under `src/namhub_dcc/commands/`
and registered in `src/namhub_dcc/commands/__init__.py`.
