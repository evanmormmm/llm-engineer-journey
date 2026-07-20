from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="我的第一个 API")


class ChatRequest(BaseModel):
    message: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(answer=f"你发送的内容是：{request.message}")
