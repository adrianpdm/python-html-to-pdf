from typing import Union, Dict
from pydantic import BaseModel
import uvicorn
from enum import Enum
from fastapi import FastAPI, Request, Response, HTTPException, Body
from fastapi.templating import Jinja2Templates
# from playwright.sync_api import sync_playwright

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class PrintType(str, Enum):
    Debug = 'debug'

class PrintFormat(str, Enum):
    HTML = "html"
    PDF = "pdf"

class PrintPayload(BaseModel):
    type: PrintType
    format: PrintFormat
    filename: str
    context: Dict = {}

@app.post("/print")
async def handle_print(
    request: Request,
    body: PrintPayload = Body(...)
):
    try:
        templates_dir = Jinja2Templates(directory='./templates')
        template_file = templates_dir.get_template(name=f"{body.type}.html")

        # for debugging
        context = body.context
        if (body.type == PrintType.Debug):
            context = { 'context': body.context }

        html_content = template_file.render({
            'request': request,
            **context,
        })
        
        if (body.format == PrintFormat.HTML):
            return Response(
                content=html_content,
                headers={
                    'content-type': 'text/html',
                }
            )
        raise TypeError('invalid format')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
