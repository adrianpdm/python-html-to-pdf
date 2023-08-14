import uvicorn
import utils

from inspect import getmembers, isfunction
from typing import Dict
from pydantic import BaseModel
from enum import Enum
from fastapi import FastAPI, Request, Response, HTTPException, Body
from fastapi.templating import Jinja2Templates
from playwright import async_api

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class PrintType(str, Enum):
    Debug = 'debug'
    StayVoucher = 'stay-voucher'
    WisataBill = 'wisata-bill'
    PaymentTransactionsHistory = 'payment-transactions-history'
    StayInvoice = 'stay-invoice'
    HotelVoucherVisaInvoice = 'hotel-voucher-visa-invoice'

class PrintFormat(str, Enum):
    HTML = "html"
    PDF = "pdf"

class PrintPayload(BaseModel):
    type: PrintType
    format: PrintFormat
    filename: str
    data: Dict = {}
    header: Dict = {}
    footer: Dict = {}
    app_config: Dict = {}

@app.post("/print")
async def handle_print(
    request: Request,
    body: PrintPayload = Body(...)
):
    try:
        templates_dir = Jinja2Templates(directory='./templates')
        templates_dir.env.globals = {
            **templates_dir.env.globals,
            **(dict(getmembers(utils, isfunction)))
        }
        template_file = templates_dir.get_template(name=f"{body.type}.html")

        html_content = template_file.render({
            'request': request,
            'filename': body.filename,
            'data': body.data,
            'header': body.header,
            'footer': body.footer,
            'app_config': body.app_config,
        })
        
        if (body.format == PrintFormat.HTML):
            filename = body.filename if body.filename.endswith('.html') else f"{body.filename}.html"
            return Response(
                content=html_content,
                headers={
                    'content-type': 'text/html',
                    'content-disposition': 'Attachment',
                    'filename': filename
                }
            )
        if (body.format == PrintFormat.PDF):
            pdf_content = None
            filename = body.filename if body.filename.endswith('.pdf') else f"{body.filename}.pdf"
            async with async_api.async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True
                )
                page = await browser.new_page()
                await page.set_content(html_content)
                pdf_content = await page.pdf(
                    margin={
                        'top': '2cm',
                        'right': '1cm',
                        'bottom': '1cm',
                        'left': '1cm',
                    }
                )
                await browser.close()

            if (pdf_content != None):
                return Response(
                    content=pdf_content,
                    headers={
                        'content-type': 'application/pdf',
                        'content-disposition': 'Attachment',
                        'filename': filename
                    }
                )
        raise TypeError('invalid format')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
