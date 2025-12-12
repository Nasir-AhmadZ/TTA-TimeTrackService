
# helper function to serialize MongoDB documents
# def entry_helper(entry) -> dict:
#     return {
#         "id": str(entry["_id"]),
#         "project_group_id": str(entry["project_group_id"]),
#         "name": entry["name"],
#         "starttime": entry["starttime"],
#         "endtime": entry.get("endtime"),
#         "duration": entry.get("duration"),
#     }

def entry_helper(entry) -> dict:
    return {
        "id": str(entry["_id"]),
        "project_group_id": str(entry["project_group_id"]),
        "name": entry["name"],
        "starttime": entry["starttime"].isoformat() if entry["starttime"] else None,
        "endtime": entry["endtime"].isoformat() if entry.get("endtime") else None,
        "duration": entry.get("duration"),
    }


#*********************Project managment models*************************
def project_helper(project) -> dict:
    return {
        "id": str(project["_id"]),
        "owner_id": str(project["owner_id"]),
        "name": project["name"],
        "description": project["description"]
    }