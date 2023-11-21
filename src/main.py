import asyncio
from datetime import datetime

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from src.database.database import close_db, get_session, init_db
from src.kafka import consume_item, produce_item
from src.models import Text
from src.schemas.schemas import Result, TextData


def create_app():
    app = FastAPI(docs_url='/')

    @app.on_event("startup")
    async def startup_event():
        # инициализация БД
        await init_db()

        # Запуск consumer Kafka
        loop = asyncio.get_event_loop()
        loop.create_task(consume_item())

    @app.on_event("shutdown")
    async def shutdown_event():
        close_db()

    @app.post("/upload")
    async def upload_item(text_file: UploadFile = File(description="Text file")):
        title_file, type_file = text_file.filename.split('.')
        if type_file not in ("txt", "doc", "pdf", "csv"):
            raise HTTPException(status_code=404, detail="Upload only text file .txt, .doc, .pdf, .csv")
        text = text_file.file.read().decode("utf-8")
        item = TextData(
            datetime=datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3],
            title=title_file,
            text=text
        )
        await produce_item(item)
        return JSONResponse(content={"message": "Item uploaded successfully"})

    @app.get("/results")
    async def get_results(db=Depends(get_session)):
        results = await db.execute(select(Text.datetime, Text.title, Text.x_avg_count_in_line))
        texts = []
        for result in results:
            if result is not None:
                response = Result(
                    datetime=result[0],
                    title=result[1],
                    x_avg_count_in_line=result[2]
                )
                texts.append(response)
        return texts

    return app


def main():
    uvicorn.run(
        f"{__name__}:create_app",
        host='0.0.0.0', port=8000,
        log_level='info'
    )


if __name__ == '__main__':
    main()
