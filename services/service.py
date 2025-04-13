from typing import List
from google.auth.transport import requests
from google.cloud import firestore
import google.oauth2.id_token
from fastapi import Request
from fastapi import HTTPException

from pydantic_models.models import User, Workspace, WorkspaceSummary

firestore_db = firestore.Client()

firebase_request_adapter = requests.Request()

class Service:

    @staticmethod
    def check_login_and_return_user(request):
        token = request.cookies.get("token")
        if not token:
            return None

        try:
            user_token = google.oauth2.id_token.verify_firebase_token(token, firebase_request_adapter)
            if not user_token:
                return None

            email = user_token.get("email")
            if not email:
                return None
            print("verified")
            user = {
                "email": email,
                "name": email.split("@")[0]
            }
            print(user)
            return user
        except Exception:
            return None

    @staticmethod
    def create_user_into_firestore(request:Request):
        token = request.cookies.get("token")
        if not token:
            return None
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(token, firebase_request_adapter)
            if not user_token:
                return None

            email = user_token.get("email")
            if not email:
                return None

            name = email.split("@")[0]
            users_ref = firestore_db.collection("users")
            existing_users = users_ref.where("email", "==", email).limit(1).stream()

            if not any(existing_users):
                users_ref.add({"email": email, "name": name})

            return {"email": email, "name": name}
        except Exception:
            return None
        
    @staticmethod
    def get_workspaces_of_user(user:User)->List["WorkspaceSummary"]:
        try:
            summaries = []
            seen_ids = set()
            print(user)
            print(type(user))
            member_query = firestore_db.collection("workspaces").where("users", "array_contains", user['email']).stream()
            creator_query = firestore_db.collection("workspaces").where("created_by", "==", user['email']).stream()
            print(member_query)
            print(creator_query)

            for doc in list(member_query) + list(creator_query):
                if doc.id in seen_ids:
                    continue
                seen_ids.add(doc.id)

                workspace_id = doc.id
                data = doc.to_dict()
                users = data.get("users", [])
                created_by = data.get("created_by", "")
                title = data.get("title", "")

                tasks = firestore_db.collection("tasks").where("workspace_id", "==", workspace_id).stream()

                total_tasks = 0
                completed_tasks = 0
                last_activity = None

                for task_doc in tasks:
                    task = task_doc.to_dict()
                    total_tasks += 1
                    if task.get("status") == "completed":
                        completed_tasks += 1
                    updated_at = task.get("updated_at")
                    if updated_at and (not last_activity or updated_at > last_activity):
                        last_activity = updated_at

                summaries.append(WorkspaceSummary(
                    id=workspace_id,
                    title=title,
                    created_by=created_by,
                    users=users,
                    total_mem=len(users),
                    total_tasks=total_tasks,
                    completed_tasks=completed_tasks,
                    active_tasks=total_tasks - completed_tasks,
                    last_activity=last_activity
                ))

            return summaries
        except Exception as e:
            print(f"[WorkspaceSummary Error] {e}")
            return []
        
    
    @staticmethod
    def get_all_users() -> List[User]:
        print('in service users')
        users =  [doc.to_dict() for doc in firestore_db.collection("users").stream()]
        print('problem is here')
        print('users')
        return users
    
    @staticmethod
    def create_workspace(workspace:Workspace,user:User):
        try:
            if firestore_db.collection("workspaces").where("title", "==", workspace.title).limit(1).get():
                raise HTTPException(status_code=400, detail="Workspace name already exists. Please choose a different name.")
            existing_users_docs = firestore_db.collection("users").stream()
            existing_emails = {doc.to_dict().get("email") for doc in existing_users_docs}
            invalid_users = [u for u in workspace.users if u not in existing_emails]
            if invalid_users:
                raise HTTPException(
                    status_code=400,
                    detail=f"These users were not found in the system: {', '.join(invalid_users)}"
                )
            firestore_db.collection("workspaces").add(workspace.dict())
        except Exception as e:
            raise Exception(str(e))
            