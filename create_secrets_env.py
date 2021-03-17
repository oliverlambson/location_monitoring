def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})

    # Return the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    return payload


if __name__ == "__main__":
    project_id = "itemit-box-tracking"
    version_id = "latest"
    secret_ids = [
        "ITEMIT_API_KEY",
        "ITEMIT_API_SECRET",
        "ITEMIT_TOKEN_VALUE",
        "ITEMIT_USER_ID",
        "ITEMIT_WORKSPACE_ID",
    ]
    with open(".env", "w", encoding="utf-8") as f:
        for secret_id in secret_ids:
            line = f"{secret_id}={access_secret_version(project_id, secret_id, version_id)}\n"
            f.write(line)
    #         print(line, end="")