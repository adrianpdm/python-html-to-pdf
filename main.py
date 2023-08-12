from typing import Union, Dict
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Body
from fastapi.templating import Jinja2Templates
from playwright.sync_api import sync_playwright

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def parse_html(request: Request, file_name: str, context: Dict):
    return templates.TemplateResponse(name=file_name, context={ "request": request, **context })

class Context(BaseModel):
    context: Dict

@app.post('/pdf')
async def generate_pdf(
   request: Request,
   body: Dict = Body(...)
):
    try:
      parsed_html = parse_html(request=request, file_name='index.html', context=body)

      with sync_playwright() as playwright:
        webkit = playwright.webkit
        browser = webkit.launch()
        context = browser.new_context()
        page = context.new_page()
        page.set_content(parsed_html.body)

        pdf = page.pdf()
        browser.close()

        # Return API response with pdf type
        return Response(content=pdf, media_type="application/pdf")

    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
