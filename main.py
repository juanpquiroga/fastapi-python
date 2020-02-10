from fastapi import FastAPI, Query, Path, Body, Header, HTTPException, Depends
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Set, Dict
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id:int, q: str = Query(..., min_length=3, max_length=50, regex="^fixedquery$"), short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/items2/")
async def read_items(q: List[str] = Query(None)):
    # Recibe multiples query q
    query_items = {"q": q}
    return query_items

@app.get("/items3/")
async def read_items(q: List[str] = Query(["foo", "bar"])):
    query_items = {"q": q}
    return query_items

@app.get("/items4/")
async def read_items(
    # Describir los query param
    q: str = Query(
        None,
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/items5/")
async def read_items(q: str = Query(None, alias="item-query")):
    # Alias de un parametro query
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/items6/")
async def read_items(
    # deprecated
    q: str = Query(
        None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        deprecated=True,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/model/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_user_me(file_path: str):
    return {"file_path": file_path}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        print("Hola")
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.get("/items2/{item_id}")
async def read_items(
    item_id: int = Path(..., title="The ID of the item to get"),
    q: str = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.get("/items3/{item_id}")
async def read_items(
    *, item_id: int = Path(..., title="The ID of the item to get"), q: str
):
    # Toma los siguientes parametros como kwargs 
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.get("/items4/{item_id}")
async def read_items(
    *, item_id: int = Path(..., title="The ID of the item to get", ge=1,le=100), q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.get("/items5/{item_id}")
async def read_items(
    *,
    item_id: int = Path(..., title="The ID of the item to get", ge=0, le=1000),
    q: str,
    size: float = Query(..., gt=0, lt=10.5)
):
    # Verificar floats
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.put("/item6/{item_id}")
async def update_item(
    *,
    item_id: int = Path(..., title="The ID of the item to get", ge=0, le=1000),
    q: str = None,
    item: Item = None,
):
    # Cuerpo opcional
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

class User(BaseModel):
    username: str
    full_name: str = None


@app.put("/items7/{item_id}")
async def update_item(*, item_id: int, item: Item, user: User):
    # Diferentes campos en el body
    results = {"item_id": item_id, "item": item, "user": user}
    return results

@app.put("/items8/{item_id}")
async def update_item(
    *, item_id: int, item: Item, user: User, importance: int = Body(...)
):
    # Diferentes campos en el body item, user y importance
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

@app.put("/items9/{item_id}")
async def update_item(*, item_id: int, item: Item = Body(..., embed=True)):
    # Requiere el campo item en el body
    results = {"item_id": item_id, "item": item}
    return results


class Item2(BaseModel):
    name: str
    description: str = Field(None, title="The description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float = None


@app.put("/items10/{item_id}")
async def update_item(*, item_id: int, item: Item2 = Body(..., embed=True)):
    # Definir propiedades de los items
    results = {"item_id": item_id, "item": item}
    return results

@app.put("/items11/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item = Body(
        ...,
        example={
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    )
):
    # Definir metatadata adicional
    results = {"item_id": item_id, "item": item}
    return results

class Item4(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    tags: List[str] = []
    tags2: Set[str] = set()


@app.put("/items12/{item_id}")
async def update_item(*, item_id: int, item: Item4):
    results = {"item_id": item_id, "item": item}
    return results

class Image(BaseModel):
    url: str
    name: str


class Item5(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    tags: Set[str] = []
    image: Image = None


@app.put("/items13/{item_id}")
async def update_item(*, item_id: int, item: Item5):
    # Submodel
    results = {"item_id": item_id, "item": item}
    return results


class Image6(BaseModel):
    url: HttpUrl
    name: str


class Item6(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    tags: Set[str] = []
    image: Image6 = None


@app.put("/items14/{item_id}")
async def update_item(*, item_id: int, item: Item6):
    # Tipos especificos
    results = {"item_id": item_id, "item": item}
    return results

class Image7(BaseModel):
    url: HttpUrl
    name: str


class Item7(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    tags: Set[str] = []
    images: List[Image7] = None


@app.put("/items15/{item_id}")
async def update_item(*, item_id: int, item: Item7):
    # Lista de subtipos
    results = {"item_id": item_id, "item": item}
    return results


class Image8(BaseModel):
    url: HttpUrl
    name: str


class Item8(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    tags: Set[str] = []
    images: List[Image8] = None


class Offer8(BaseModel):
    name: str
    description: str = None
    price: float
    items: List[Item8]

@app.post("/offers/")
async def create_offer(*, offer: Offer8):
    # Nested type
    return offer

class Image9(BaseModel):
    url: HttpUrl
    name: str


@app.post("/images/multiple/")
async def create_multiple_images(*, images: List[Image9]):
    # List of types
    return images

@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    # List of arbitrary dict
    return weights


@app.get("/itemsheader/")
async def read_items(*, user_agent: str = Header(None)):
    return {"User-Agent": user_agent}


@app.get("/itemsheader2/")
async def read_items(*, device: str = Header(...,alias="X-Liftit-Device")):
    return {"Device": device}

@app.get("/itemsheader3/")
async def read_items(x_token: List[str] = Header(None)):
    return {"X-Token values": x_token}

@app.post("/itemsresp/", response_model=Item)
async def create_item(item: Item):
    return item

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str = None


@app.post("/user/", response_model=UserOut)
async def create_user(*, user: UserIn):
    return user

class Item10(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = 10.5
    tags: List[str] = []
    image: Image


items10 = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": [], "image": { "url": "asd", "name": "asdad"}},
}


@app.get("/itemsresp/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items10[item_id]


@app.get(
    "/itemsresp/{item_id}/name",
    response_model=Item10,
    response_model_include={"name", "description","image..name"},
)
async def read_item_name(item_id: str):
    return items10[item_id]


@app.get("/itemserror/{item_id}")
async def read_item(item_id: str):
    if item_id not in items10:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items10[item_id]}

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {exc}")
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


@app.get("/itemserror2/{item_id}", tags=["error"])
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}

async def common_parameters(q: str = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/itemsdep/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.get("/usersdep/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons

from starlette.requests import Request
import time 
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

from starlette.middleware.cors import CORSMiddleware
origins = [
    "http://hola.com"
    #"http://localhost.tiangolo.com",
    #"https://localhost.tiangolo.com",
    #"http://localhost",
    #"http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import BackgroundTasks
def write_notification(email: str, message:str=""):
    print("Enviar")
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)
        print("Termino")


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    print("Enviar background")
    background_tasks.add_task(write_notification, email, message="some notification")
    print("Terminar metodo")
    return {"message": "Notification sent in the background"}

from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/wshtml")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

import graphene
from starlette.graphql import GraphQLApp

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name

app.add_route("/gql", GraphQLApp(schema=graphene.Schema(query=Query)))

app.add_route("/", GraphQLApp(schema=graphene.Schema(query=Query)))

from fastapi import APIRouter
from starlette.responses import JSONResponse

class Invoice(BaseModel):
    id: str
    title: str = None
    customer: str
    total: float


class InvoiceEvent(BaseModel):
    description: str
    paid: bool


class InvoiceEventReceived(BaseModel):
    ok: bool


invoices_callback_router = APIRouter(default_response_class=JSONResponse)


@invoices_callback_router.post(
    "{$callback_url}/invoices/{$request.body.id}", response_model=InvoiceEventReceived,
)
def invoice_notification(body: InvoiceEvent):
    pass


@app.post("/invoices/", callbacks=invoices_callback_router.routes)
def create_invoice(invoice: Invoice, callback_url: HttpUrl = None):
    """
    Create an invoice.

    This will (let's imagine) let the API user (some external developer) create an
    invoice.

    And this path operation will:

    * Send the invoice to the client.
    * Collect the money from the client.
    * Send a notification back to the API user (the external developer), as a callback.
        * At this point is that the API will somehow send a POST request to the
            external API with the notification of the invoice event
            (e.g. "payment successful").
    """
    # Send the invoice, collect the money, send the notification (the callback)
    return {"msg": "Invoice received"}

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from datetime import datetime

class Item11(BaseModel):
    title: str
    timestamp: datetime
    description: str = None


@app.put("/items16/{id}")
def update_item(id: str, item: Item11):
    json_compatible_item_data = jsonable_encoder(item)
    return JSONResponse(content=json_compatible_item_data)

from starlette.responses import HTMLResponse

@app.get("/items17/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """

from starlette.responses import Response
from starlette.status import HTTP_201_CREATED

tasks = {"foo": "Listen to the Bar Fighters"}


@app.put("/get-or-create-task/{task_id}", status_code=200)
def get_or_create_task(task_id: str, response: Response):
    if task_id not in tasks:
        tasks[task_id] = "This didn't exist before"
        response.status_code = HTTP_201_CREATED
    return tasks[task_id]

class FixedContentQueryChecker:
    def __init__(self, fixed_content: str):
        self.fixed_content = fixed_content

    def __call__(self, q: str = ""):
        if q:
            return self.fixed_content in q
        return False


checker = FixedContentQueryChecker("bar")


@app.get("/query-checker/")
async def read_query_check(fixed_content_included: bool = Depends(checker)):
    return {"fixed_content_in_query": fixed_content_included}
