import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

from yahoo_finance_tools import get_yahoo_finance_tools
from tiingo_tools import get_tiingo_tools
from brave_search_tools import get_brave_search_tools
from logging_utils import get_logger

logger = get_logger()


class PortfolioAdviceService:
    """Service to generate portfolio advice using an LLM and financial tools."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tiingo_api_key = os.getenv("TIINGO_API_KEY")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=self.openai_api_key,
        )

        self.tools = []
        self.tools.extend(get_yahoo_finance_tools())
        if self.tiingo_api_key:
            self.tools.extend(get_tiingo_tools())
        if self.brave_api_key:
            self.tools.extend(get_brave_search_tools())

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an experienced investment advisor. "
                "Use the available tools to fetch up to date stock prices and news before "
                "providing advice on a portfolio.",
            ),
            ("user", "{input}"),
            (
                "assistant",
                "I'll research the holdings and craft a short analysis.",
            ),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False)

    def generate_advice(self, portfolio_goal: str, cash_balance: float, positions: List[Dict]) -> str:
        """Generate textual advice for a portfolio."""
        position_lines = []
        for pos in positions:
            symbol = pos.get("symbol", "").upper()
            qty = pos.get("quantity", 0)
            price = pos.get("currentPrice") or pos.get("current_price") or 0
            gain = pos.get("gainLoss") or pos.get("gain_loss") or 0
            gain_pct = pos.get("gainLossPercent") or pos.get("gain_loss_percent") or 0
            position_lines.append(
                f"- {symbol}: {qty} shares at ${price} (gain {gain:+}, {gain_pct:+}%)"
            )
        positions_text = "\n".join(position_lines) if position_lines else "None"

        prompt = (
            f"Portfolio goal: {portfolio_goal}\n"
            f"Cash balance: ${cash_balance}\n"
            f"Positions:\n{positions_text}\n\n"
            "Discuss performance and how well this portfolio matches the goal. "
            "Mention relevant news or metrics for key holdings and end with a short recommendation."
        )

        result = self.agent_executor.invoke({"input": prompt})
        return result.get("output", "").strip()
