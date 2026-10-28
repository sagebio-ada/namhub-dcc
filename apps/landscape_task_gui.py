import urllib.parse

import requests
import streamlit as st
from synapseclient import Synapse
from synapseclient.extensions.curator import create_record_based_metadata_task


# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Create Landscape Metadata Tasks",
    page_icon="🗂️",
    layout="wide",
)

st.title("🗂️ Create Landscape Metadata Tasks")
st.write(
    "Create one or more Landscape metadata tasks across different Synapse folders."
)


# -----------------------------------------------------------------------------
# Synapse login
# -----------------------------------------------------------------------------
@st.cache_resource
def get_synapse_client():
    syn = Synapse()
    syn.login()
    return syn


try:
    syn = get_synapse_client()
    st.success("Logged into Synapse.")
except Exception as e:
    st.error(
        "Could not log into Synapse. Make sure you have valid Synapse credentials configured."
    )
    st.exception(e)
    st.stop()


# -----------------------------------------------------------------------------
# Schema loading
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_registered_schema(schema_uri: str) -> dict:
    """
    Load a registered Synapse schema using the schema URI.

    Example:
    https://repo-prod.prod.sagebase.org//repo/v1/schema/type/registered/NAMhub-Landscape-1.0.0
    """
    schema_uri = schema_uri.strip()

    if not schema_uri:
        return {}

    encoded_schema_uri = urllib.parse.quote(schema_uri, safe="")

    schema_url = (
        "https://repo-prod.prod.sagebase.org//repo/v1/schema/type/registered/"
        f"{encoded_schema_uri}"
    )

    response = requests.get(schema_url, timeout=30)
    response.raise_for_status()

    return response.json()


@st.cache_data(show_spinner=False)
def get_schema_properties(schema_uri: str) -> list[str]:
    """
    Return the schema properties as column headers.
    """
    schema = load_registered_schema(schema_uri)

    properties = schema.get("properties", {})

    if not isinstance(properties, dict):
        return []

    return list(properties.keys())


def render_schema_properties(schema_uri: str, upsert_key: str):
    """
    Display the schema properties and mark the selected upsert key with an icon.
    """
    st.markdown("#### Schema Properties")

    if not schema_uri.strip():
        st.info("Enter a Schema URI to load schema properties.")
        return

    try:
        properties = get_schema_properties(schema_uri)
    except Exception as e:
        st.error(f"Could not load schema properties for `{schema_uri}`.")
        st.exception(e)
        return

    if not properties:
        st.warning(f"No properties found for schema `{schema_uri}`.")
        return

    rows = []

    for prop in properties:
        rows.append(
            {
                "Upsert Key": "🔑" if prop == upsert_key else "",
                "Column Header": prop,
            }
        )

    st.caption("The key icon marks the column currently selected as the upsert key.")

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
DEFAULT_TASK = {
    "pi_name": "",
    "folder_id": "",
    "record_set_name": "Landscape",
    "record_set_description": "",
    "curation_task_name": "Landscape Task",
    "instructions": "Please fill in each row with the dataset information.",
    "schema_uri": "NAMhub-Landscape-1.0.0",
    "upsert_key": "LandscapeId",
}


if "landscapes" not in st.session_state:
    st.session_state.landscapes = [DEFAULT_TASK.copy()]


def add_landscape():
    st.session_state.landscapes.append(DEFAULT_TASK.copy())


def remove_landscape(index: int):
    st.session_state.landscapes.pop(index)


# -----------------------------------------------------------------------------
# Form rendering
# -----------------------------------------------------------------------------
st.subheader("Landscape Tasks")

for i, landscape in enumerate(st.session_state.landscapes):
    with st.expander(f"Landscape Task {i + 1}", expanded=True):
        left_col, right_col = st.columns(2)

        with left_col:
            pi_name = st.text_input(
                "PI Name",
                value=landscape["pi_name"],
                key=f"pi_name_{i}",
                placeholder="Example: Jane Doe",
            )

            folder_id = st.text_input(
                "Synapse Folder ID",
                value=landscape["folder_id"],
                key=f"folder_id_{i}",
                placeholder="Example: syn74568176",
            )

            record_set_name = st.text_input(
                "Record Set Name",
                value=landscape["record_set_name"],
                key=f"record_set_name_{i}",
            )

            curation_task_name = st.text_input(
                "Curation Task Name",
                value=landscape["curation_task_name"],
                key=f"curation_task_name_{i}",
            )

        with right_col:
            schema_uri = st.text_input(
                "Schema URI",
                value=landscape["schema_uri"],
                key=f"schema_uri_{i}",
                placeholder="Example: NAMhub-Landscape-1.0.0",
            )

            try:
                schema_properties = get_schema_properties(schema_uri)
            except Exception:
                schema_properties = []

            if schema_properties:
                previous_upsert_key = landscape.get("upsert_key", "")

                if previous_upsert_key in schema_properties:
                    selected_index = schema_properties.index(previous_upsert_key)
                elif "LandscapeId" in schema_properties:
                    selected_index = schema_properties.index("LandscapeId")
                else:
                    selected_index = 0

                upsert_key = st.selectbox(
                    "Upsert Key",
                    options=schema_properties,
                    index=selected_index,
                    key=f"upsert_key_{i}",
                    help="Select the schema column that uniquely identifies rows for upsert.",
                )
            else:
                upsert_key = st.text_input(
                    "Upsert Key",
                    value=landscape.get("upsert_key", "LandscapeId"),
                    key=f"upsert_key_fallback_{i}",
                    help="Schema properties could not be loaded, so this field is editable text.",
                )

            record_set_description = st.text_area(
                "Record Set Description",
                value=landscape["record_set_description"],
                key=f"record_set_description_{i}",
                placeholder="Example: Landscape task for Jane Doe",
            )

            instructions = st.text_area(
                "Instructions",
                value=landscape["instructions"],
                key=f"instructions_{i}",
            )

        # Save widget values back to session state
        landscape["pi_name"] = pi_name
        landscape["folder_id"] = folder_id
        landscape["record_set_name"] = record_set_name
        landscape["curation_task_name"] = curation_task_name
        landscape["schema_uri"] = schema_uri
        landscape["upsert_key"] = upsert_key
        landscape["record_set_description"] = record_set_description
        landscape["instructions"] = instructions

        st.divider()

        render_schema_properties(
            schema_uri=landscape["schema_uri"],
            upsert_key=landscape["upsert_key"],
        )

        if len(st.session_state.landscapes) > 1:
            st.button(
                "Remove this task",
                key=f"remove_{i}",
                on_click=remove_landscape,
                args=(i,),
            )


st.button("➕ Add another Landscape task", on_click=add_landscape)

st.divider()


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
def validate_landscape_task(task: dict, index: int) -> list[str]:
    errors = []

    task_label = f"Task {index + 1}"

    if not task["pi_name"].strip():
        errors.append(f"{task_label}: PI Name is required.")

    if not task["folder_id"].strip():
        errors.append(f"{task_label}: Synapse Folder ID is required.")

    if task["folder_id"].strip() and not task["folder_id"].strip().startswith("syn"):
        errors.append(f"{task_label}: Folder ID should look like syn12345678.")

    if not task["record_set_name"].strip():
        errors.append(f"{task_label}: Record Set Name is required.")

    if not task["curation_task_name"].strip():
        errors.append(f"{task_label}: Curation Task Name is required.")

    if not task["schema_uri"].strip():
        errors.append(f"{task_label}: Schema URI is required.")

    if not task["upsert_key"].strip():
        errors.append(f"{task_label}: Upsert Key is required.")

    return errors


# -----------------------------------------------------------------------------
# Create tasks
# -----------------------------------------------------------------------------
if st.button("🚀 Create Landscape Tasks", type="primary"):
    all_errors = []

    for i, task in enumerate(st.session_state.landscapes):
        all_errors.extend(validate_landscape_task(task, i))

    if all_errors:
        st.error("Please fix the following issues before creating tasks:")
        for error in all_errors:
            st.write(f"- {error}")
        st.stop()

    results = []

    with st.spinner("Creating Landscape metadata tasks..."):
        for task in st.session_state.landscapes:
            pi_name = task["pi_name"].strip()
            folder_id = task["folder_id"].strip()
            schema_uri = task["schema_uri"].strip()
            upsert_key = task["upsert_key"].strip()

            description = (
                task["record_set_description"].strip()
                or f"Landscape task for {pi_name}"
            )

            try:
                record_set, curation_task, data_grid = create_record_based_metadata_task(
                    synapse_client=syn,
                    folder_id=folder_id,
                    record_set_name=task["record_set_name"].strip(),
                    record_set_description=description,
                    curation_task_name=task["curation_task_name"].strip(),
                    upsert_keys=[upsert_key],
                    instructions=task["instructions"].strip(),
                    schema_uri=schema_uri,
                )

                results.append(
                    {
                        "PI Name": pi_name,
                        "Folder ID": folder_id,
                        "Schema URI": schema_uri,
                        "Upsert Key": upsert_key,
                        "RecordSet ID": record_set.id,
                        "Curation Task ID": curation_task.task_id,
                        "Status": "Created",
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "PI Name": pi_name,
                        "Folder ID": folder_id,
                        "Schema URI": schema_uri,
                        "Upsert Key": upsert_key,
                        "RecordSet ID": "",
                        "Curation Task ID": "",
                        "Status": f"Failed: {e}",
                    }
                )

    st.success("Finished creating Landscape tasks.")

    st.subheader("Results")
    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Created Task Summary")

    for result in results:
        if result["Status"] == "Created":
            st.markdown(
                f"""
**PI:** {result["PI Name"]}  
**Folder:** `{result["Folder ID"]}`  
**Schema URI:** `{result["Schema URI"]}`  
**Upsert Key:** `{result["Upsert Key"]}`  
**RecordSet:** `{result["RecordSet ID"]}`  
**Curation Task:** `{result["Curation Task ID"]}`
"""
            )
        else:
            st.error(
                f"{result['PI Name']} / {result['Folder ID']} failed: {result['Status']}"
            )