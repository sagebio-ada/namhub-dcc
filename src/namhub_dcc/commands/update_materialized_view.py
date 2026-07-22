"""Update the NAMHub portal MaterializedView SQL.

Applies the canonical SQL definition to the MaterializedView (syn75904610).
The view joins the Studies table (syn75404711) with the ProjectView
(syn74589195) so the portal always reflects the current Studies table content.
"""

import logging

from namhub_dcc.auth import login

log = logging.getLogger(__name__)

COMMAND_NAME = "update-materialized-view"

DEFAULT_MV_ID = "syn75904610"

DEFINING_SQL = """\
SELECT
    T.studyId AS synapseProjectId,
    P.name AS projectName,
    P.program AS program,
    T.studyName AS studyName,
    T.studyLeads AS studyLeads,
    T.fundingAgency AS fundingAgency,
    T.diseaseFocus AS diseaseFocus,
    T.institution AS institution,
    T.NAMsTechFocus AS NAMsTechFocus,
    T.grantId AS grantId,
    T.alternateName AS alternateName,
    P.studyStatus AS studyStatus,
    T.studyDoi AS studyDoi,
    T.summary AS summary
FROM syn75404711 T
LEFT JOIN syn74589195 P ON (T.synapseProjectId = P.id)\
"""


def add_parser(subparsers):
    parser = subparsers.add_parser(
        COMMAND_NAME,
        help="Apply the canonical SQL to the NAMHub portal MaterializedView.",
        description=__doc__,
    )
    parser.add_argument(
        "--mv-id",
        default=DEFAULT_MV_ID,
        help=f"Synapse ID of the MaterializedView. Default: {DEFAULT_MV_ID!r}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the SQL that would be applied without making any updates.",
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
    if args.dry_run:
        log.info("Dry run — SQL that would be applied to %s:\n%s", args.mv_id, DEFINING_SQL)
        return

    syn = login(args.auth_token)
    mv = syn.get(args.mv_id)

    if mv.definingSQL == DEFINING_SQL:
        log.info("MaterializedView %s is already up to date.", args.mv_id)
        return

    mv.definingSQL = DEFINING_SQL
    syn.store(mv)
    log.info("MaterializedView %s updated.", args.mv_id)
