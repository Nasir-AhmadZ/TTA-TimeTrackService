import os
import aio_pika
from fastapi import FastAPI, HTTPException
from datetime import datetime
from bson import ObjectId
import json
from dotenv import load_dotenv
load_dotenv()
from .schemas import EntryStart, Entry, ProjectCreate, Project, EntryUpdate
from .models import entry_helper, project_helper
from .configurations import db, entries_collection, projects_collection
app = FastAPI(title="Time Tracker API")
currentUser = "691c8bf8d691e46d00068bf3"


#******************************RabbitMQ stuff******************************************
RABBIT_URL = os.getenv("RABBIT_URL")
EXCHANGE_NAME = "notificiations_topic"
async def get_exchange():
    """
    Open a connection, create a channel and declare a topic exchange.
    Returns (connection, channel, exchange).
    """
    conn = await aio_pika.connect_robust(RABBIT_URL)
    ch = await conn.channel()
    ex = await ch.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC)
    return conn, ch, ex

#******************************entries endpoints****************************************
#Get entry by id
@app.get("/entry/{entry_id}", response_model=Entry, status_code=200)
def get_entry_by_id(entry_id: str):

    #validate ObjectId format
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry id")

    entry = entries_collection.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return entry_helper(entry)


#delete by id
@app.delete("/entry/{entry_id}",status_code=200)
def delete_entry_by_id(entry_id: str):
    entries_collection.delete_one({"_id": ObjectId(entry_id)})
    return {"message": "Entry deleted"}

#start a time entry using put
@app.put("/entries/", response_model=Entry,status_code=201)
async def start_entry(entry: EntryStart):
    now = datetime.now()
    entry_dict = {
        "name": entry.name,
        "project_group_id": ObjectId(entry.project_group_id),
        "starttime": now,
        "endtime": None,
        "duration": None
    }

    #check if the project exists
    project = projects_collection.find_one({"_id": entry_dict["project_group_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project does not exist")
    
    result = entries_collection.insert_one(entry_dict)
    created_entry = entries_collection.find_one({"_id": result.inserted_id})

    #send a message to nitifcation service via rabbitmq
    #send a rabbit mq message to notifications service
    await createNotification(
        event_type="entry.running",
        user_id=currentUser,
        routing_key="entry.running",
        data=entry_helper(created_entry)
    )

    return entry_helper(created_entry)

#complete a time entry
@app.patch("/entries/{entry_id}", response_model=Entry, status_code=200)
async def end_entry(entry_id: str):
    entry = entries_collection.find_one({"_id": ObjectId(entry_id)})
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if entry.get("endtime") is not None:
        raise HTTPException(status_code=400, detail="Entry already ended")
    
    now = datetime.now()
    starttime = entry["starttime"]
    duration_seconds = int((now - starttime).total_seconds())
    
    entries_collection.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": {"endtime": now, "duration": duration_seconds}}
    )

    updated_entry = entries_collection.find_one({"_id": ObjectId(entry_id)})

    #send a rabbit mq message to notifications service
    await createNotification(
        event_type="entry.completed",
        user_id=currentUser,
        routing_key="entry.completed",
        data=entry_helper(updated_entry)
    )

    return entry_helper(updated_entry)

#update a time entry. Name and project it belongs to
@app.patch("/entries/update/{entry_id}", response_model=dict, status_code=200)
async def update_entry(entry_id: str, updatedEntry: EntryUpdate):
    # Find existing entry
    entry = entries_collection.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # prepare update data, only include set fields
    update_data = {k: v for k, v in updatedEntry.dict(exclude_unset=True).items() if v is not None}

    # test if the project exists
    if "project_group_id" in update_data:
        project_id = ObjectId(update_data["project_group_id"])
        project = projects_collection.find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project does not exist")
        update_data["project_group_id"] = project_id  # convert to ObjectId for mongodb

    #update the entry
    if update_data:
        entries_collection.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
        
        updated_entry = entries_collection.find_one({"_id": ObjectId(entry_id)})
        
        #send a message to notifcation service via rabbitmq
        await createNotification(
            event_type="entry.updated",
            user_id=currentUser,
            routing_key="entry.updated",
            data=entry_helper(updated_entry)
        )
    else:
        updated_entry = entries_collection.find_one({"_id": ObjectId(entry_id)})

    return entry_helper(updated_entry)

# List all entries
@app.get("/entries/", response_model=list[Entry], status_code=200)
def list_entries():
    entries = entries_collection.find()
    return [entry_helper(e) for e in entries]

#list entries belongin to a project
@app.get("/entries/project/{project_id}", response_model=list[Entry],status_code=200)
def list_entries_from_project(project_id: str):

    #validate ObjectId format
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")

#check if the project exists
    if not projects_collection.find_one({"_id": ObjectId(project_id)}):
        raise HTTPException(status_code=404, detail="project does not exist")

    # check if project exists
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    #fetch entries belonging to project
    entries = entries_collection.find({"project_group_id": ObjectId(project_id)})

    return [entry_helper(e) for e in entries]



#********************project Managment*******************************
#create project
@app.put("/projects/", response_model=Project,status_code=201)
async def create_project(project: ProjectCreate):
    project_dict = {
        "name": project.name,
        "description": project.description,
        "owner_id": ObjectId(currentUser)
    }
    
    result = projects_collection.insert_one(project_dict)
    created_project = projects_collection.find_one({"_id": result.inserted_id})

    #send a message to nitifcation service via rabbitmq
    #send a rabbit mq message to notifications service

    await createNotification(
        event_type="project.created",
        user_id=currentUser,
        routing_key="project.created",
        data=project_helper(created_project)
    )

    return project_helper(created_project)

# list all projects
@app.get("/projects/", response_model=list[Project],status_code=200)
def list_projects():
    projects = projects_collection.find()
    return [project_helper(p) for p in projects]

#list projects belongin to the current user
@app.get("/projects/user", response_model=list[Project],status_code=200)
def list_users_projects():
    projects = projects_collection.find({"owner_id": ObjectId(currentUser)})
    return [project_helper(p) for p in projects]

#delete a project and all its entries
@app.delete("/project/{project_id}",status_code=200)
def delete_project_and_entries(project_id: str):
    if(delete_project_and_entries_helper(project_id)):
       return {"status": "success", "message": "Project and all its entries deleted"} 
    

@app.delete("/user/projects",status_code=200)
def delete_users_projects():

#list projects belongin to the current user
    projects = projects_collection.find({"owner_id": ObjectId(currentUser)})
    for p in projects:
        delete_project_and_entries_helper(str(p["_id"]))

    return {"status": "success", "message": "Users projects are deleted"}
    

##helper function to delete a project and all its entries
def delete_project_and_entries_helper(project_id: str):
        #validate ObjectId format
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")

    #check if the project exists
    if not projects_collection.find_one({"_id": ObjectId(project_id)}):
        raise HTTPException(status_code=404, detail="project does not exist")

    #delete all entries belonging to the project
    entries_collection.delete_many({"project_group_id": ObjectId(project_id)})

    #delete the project
    projects_collection.delete_one({"_id": ObjectId(project_id)})

    return 1


async def createNotification(event_type: str, user_id: str, routing_key: str, data: dict):
    conn, ch, ex = await get_exchange()
    msg_payload = {
        "event_type": event_type,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    msg = aio_pika.Message(body=json.dumps(msg_payload).encode())
    await ex.publish(msg, routing_key=routing_key)
    await conn.close()


# python -m uvicorn app.main:app --reload
