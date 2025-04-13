from fastapi import FastAPI, HTTPException, Request,Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.auth.transport import requests
from google.cloud import firestore
from pydantic_models.models import Task, Workspace
from services.service import Service
import google.oauth2.id_token
from fastapi.responses import RedirectResponse

app = FastAPI()



app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

def create_user_into_firestore(request:Request):
    try:
        return Service.create_user_into_firestore(request)
    except Exception as e:
        raise Exception(str(e))
    
def check_login_and_return_user(request:Request):
    try:
        user = Service.check_login_and_return_user(request)
        return user
    except Exception as e:
        raise Exception (str(e))
    

@app.get("/workspaces",response_class=RedirectResponse)
def get_workspaces_of_user(request:Request):
    try:
        user = check_login_and_return_user(request)
        if not user:
            return RedirectResponse(url="/")
        workspaces = Service.get_workspaces_of_user(user)
        return templates.TemplateResponse(
            "workspaces.html",
            {"request":request,"workspaces":workspaces,"user":user}
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/workspaces?error={str(e)}",
            status_code=303
        )

@app.get("/workspaces/create",response_class=HTMLResponse)
def create_workspaces(request:Request):
    try:
        print("hello")
        user = check_login_and_return_user(request)
        print(user)
        print("hello")
        if user :
            print('call here ')
            users = Service.get_all_users()
            print('inside')
            return templates.TemplateResponse(
            "create_workspace.html",
                {
                    "request": request,
                    "users": users,
                    "current_user": user,
                    "board": None
                }
            )
        else:
            print("not logged in")
            return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        print(e)
        return RedirectResponse(url="/")
    
@app.post("/workspaces/create",response_class=RedirectResponse)
def create_workspace(request:Request,workspace: Workspace = Depends(Workspace.from_form)):
    user = Service.check_login_and_return_user(request)
    try:
        if user:
            Service.create_workspace(workspace,user)
        else :
            return RedirectResponse(url="/",status_code=303)
        return RedirectResponse(
            url="/workspaces",
            status_code=303
        )
    except Exception as e:
        return templates.TemplateResponse(
           "add-task-board.html", 
            {"request": request,
             "users":Service.get_all_users(),
             "current_user":user,
             "board": None,
             "error":str(e)
            })