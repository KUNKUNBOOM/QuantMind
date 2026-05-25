import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BASE = "https://mkapi2.dfcfs.com/finskillshub/api/claw"

class MXClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MX_APIKEY", "")
        self.headers = {"Content-Type": "application/json", "apikey": self.api_key}

    def _post(self, path: str, body: dict) -> dict:
        resp = requests.post(f"{BASE}{path}", headers=self.headers, json=body, timeout=30)
        if not resp.ok:
            return {"error": resp.status_code, "msg": resp.text[:300]}
        try:
            return resp.json()
        except:
            return {"error": -1, "msg": resp.text[:300]}

    def search_news(self, query: str) -> str:
        """搜索金融资讯/新闻/公告/研报"""
        data = self._post("/news-search", {"query": query})
        if "error" in data:
            return json.dumps(data, ensure_ascii=False)
        items = (data.get("data") or {}).get("items", [])
        if not items:
            return f"API返回: {json.dumps(data, ensure_ascii=False)[:500]}"
        lines = []
        for i, item in enumerate(items[:5]):
            title = item.get("title", "")
            summary = (item.get("summary") or item.get("content") or "")[:100]
            source = item.get("source", "")
            date = item.get("publishTime", "") or item.get("date", "")
            lines.append(f"{i+1}. {title}\n   来源: {source} | {date}\n   {summary}")
        return "\n\n".join(lines)

    def query_data(self, query: str) -> str:
        data = self._post("/query", {"toolQuery": query})
        if "error" in data:
            return json.dumps(data, ensure_ascii=False)
        try:
            items = data["data"]["data"]["searchDataResultDTO"]["dataTableDTOList"]
        except (KeyError, TypeError):
            return f"API返回: {json.dumps(data, ensure_ascii=False)[:500]}"
        lines = []
        for item in items[:3]:
            name = item.get("entityName", item.get("code", "未知"))
            tbl = item.get("table", {})
            lines.append(f"【{name}】")
            for key, vals in tbl.items():
                if key == "headName":
                    continue
                val = vals[0] if isinstance(vals, list) and vals else vals
                head = tbl.get("headName", [])
                label = str(head[0]) if head else key
                lines.append(f"  {label}: {val}")
        return "\n".join(lines) if lines else f"数据: {json.dumps(str(data)[:500], ensure_ascii=False)}"

    def screen_stocks(self, query: str) -> str:
        """根据条件选股（如PE<20、净利润增长>30%等）"""
        data = self._post("/stock-screen", {"query": query})
        if "error" in data:
            return json.dumps(data, ensure_ascii=False)
        items = (data.get("data") or {}).get("items", [])
        if not items:
            return f"API返回: {json.dumps(data, ensure_ascii=False)[:500]}"
        lines = [f"共筛选到 {len(items)} 只股票，前10只："]
        for item in items[:10]:
            code = item.get("code", "")
            name = item.get("name", "")
            price = item.get("price", "")
            change = item.get("change", "")
            lines.append(f"  {code} {name} 价格:{price} 涨跌:{change}")
        return "\n".join(lines)
