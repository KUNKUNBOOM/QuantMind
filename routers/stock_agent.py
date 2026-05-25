from fastapi import APIRouter
from pydantic import BaseModel, SecretStr
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
import settings
from core.mx_client import MXClient

mx = MXClient()
router = APIRouter(prefix="/stock")

class StockChatIn(BaseModel):
    message: str

class StockChatOut(BaseModel):
    reply: str

llm = ChatDeepSeek(model="deepseek-chat", api_key=SecretStr(settings.DEEPSEEK_API_KEY), temperature=0.7)

CLASSIFY_PROMPT = """判断用户意图，只回复一个词：data / news / screen / chat。
- data: 查行情、股价、财务数据、估值
- news: 搜新闻、公告、研报
- screen: 按条件选股
- chat: 闲聊或不明确"""

SUMMARY_PROMPT = """你是A股分析助手。根据以下数据回答用户问题，引用数据，声明仅供参考。
用户问题：{question}
查询结果：{result}"""

@router.post("/chat", response_model=StockChatOut)
async def stock_chat(data: StockChatIn):
    q = data.message
    classify = llm.invoke([SystemMessage(content=CLASSIFY_PROMPT), HumanMessage(content=q)])
    intent = str(classify.content).strip().lower()

    if intent == "data":
        result = mx.query_data(q)
    elif intent == "news":
        result = mx.search_news(q)
    elif intent == "screen":
        result = mx.screen_stocks(q)
    else:
        chat = llm.invoke([SystemMessage(content="你是A股投资助手，回答用户问题。投资建议声明仅供参考。"), HumanMessage(content=q)])
        return StockChatOut(reply=str(chat.content or "无法回复"))

    summary = llm.invoke([SystemMessage(content=SUMMARY_PROMPT.format(question=q, result=result))])
    return StockChatOut(reply=str(summary.content or result))
