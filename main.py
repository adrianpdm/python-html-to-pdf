from typing import Union, Dict, Optional
from pydantic import BaseModel
import uvicorn
from enum import Enum
from fastapi import FastAPI, Request, Response, HTTPException, Body
from fastapi.templating import Jinja2Templates
from playwright import async_api

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
    context: Dict = {}
    filename: str

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
            'filename': body.filename,
            **context,
        })
        
        if (body.format == PrintFormat.HTML):
            return Response(
                content=html_content,
                headers={
                    'content-type': 'text/html',
                }
            )
        if (body.format == PrintFormat.PDF):
            pdf_content = None
            pdf_filename = body.filename if body.filename.endswith('.pdf') else f"{body.filename}.pdf"
            async with async_api.async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True
                )
                page = await browser.new_page()
                await page.set_content(html_content)
                pdf_content = await page.pdf()
                await browser.close()

            if (pdf_content != None):
                return Response(
                    content=pdf_content,
                    headers={
                        'content-type': 'application/pdf',
                        'content-disposition': 'Attachment',
                        'filename': pdf_filename
                    }
                )
        raise TypeError('invalid format')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
