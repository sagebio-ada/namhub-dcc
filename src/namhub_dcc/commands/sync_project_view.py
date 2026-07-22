"""Sync the NAMHub Projects view scope with the Studies table.

Reads all ``synapseProjectId`` values from the Studies table and ensures
each one is present in the ProjectView's ``scopeIds``.  Any project already
in scope is left untouched; only new entries are added.
"""

import logging

from namhub_dcc.auth import login

log = logging.getLogger(__name__)

COMMAND_NAME = "sync-project-view"

DEFAULT_STUDIES_TABLE_ID = "syn75404711"
DEFAULT_PROJECT_VIEW_ID = "syn74589195"


def add_parser(subparsers):
    parser = subparsers.add_parser(
        COMMAND_NAME,
        help="Sync the NAMHub Projects view scope with the Studies table.",
        description=__doc__,
    )
    parser.add_argument(
        "--studies-table-id",
        default=DEFAULT_STUDIES_TABLE_ID,
        help=f"Synapse ID of the Studies table. Default: {DEFAULT_STUDIES_TABLE_ID!r}.",
    )
    parser.add_argument(
        "--project-view-id",
        default=DEFAULT_PROJECT_VIEW_ID,
        help=f"Synapse ID of the NAMHub Projects view. Default: {DEFAULT_PROJECT_VIEW_ID!r}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without making any updates.",
    )
    parser.add_argument(
        "--auth-token",
        default=None,
        help="Synapse personal access token. If omitted, falls back to the "
        "SYNAPSE_AUTH_TOKEN environment variable or cached credentials.",
    )
    parser.set_defaults(func=run)
    return parser


def run(args):
    syn = login(args.auth_token)

    # Read synapseProjectId values from the Studies table (strip "syn" prefix
    # for comparison since scopeIds store the numeric part only).
    results = syn.tableQuery(
        f"SELECT synapseProjectId FROM {args.studies_table_id}"
    )
    df = results.asDataFrame()
    study_numeric_ids = set(
        str(int(v)) for v in df["synapseProjectId"].dropna()
    )
    log.info(
        "Found %d project(s) in Studies table %s",
        len(study_numeric_ids),
        args.studies_table_id,
    )

    # Load the ProjectView and compare scope.
    view = syn.get(args.project_view_id)
    current_scope = set(view.scopeIds or [])

    to_add = study_numeric_ids - current_scope
    if not to_add:
        log.info("ProjectView scope is already up to date — nothing to add.")
        return

    log.info(
        "%d new project(s) to add to ProjectView %s: %s",
        len(to_add),
        args.project_view_id,
        sorted(to_add),
    )

    if args.dry_run:
        log.info("Dry run — no changes made.")
        return

    view.scopeIds = sorted(current_scope | to_add)
    syn.store(view)
    log.info(
        "ProjectView %s scope updated. Total projects in scope: %d",
        args.project_view_id,
        len(view.scopeIds),
    )
