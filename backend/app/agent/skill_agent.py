"""Portable SkillMap AI Agent implementation.

Preserves the Gemini + LangChain/LangGraph + Composio MCP research workflow
from mcp.ipynb, replacing Google Colab dependencies with server-side configuration,
bounded execution limits, and structured response normalization.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from app.config import get_settings
from app.tools.job_search import get_langchain_job_search_tool
from app.utils.errors import (
    ConfigurationError,
    ProviderAuthError,
    ProviderTimeoutError,
    AgentExecutionError,
)

logger = logging.getLogger("skillmap.agent")

SYSTEM_PROMPT = """You are a Skill-to-Career Mapping assistant that helps students and professionals understand skill demand, industry trends, and find matching job opportunities.

You have access to these tools:
- MCP search tools: Search the web for industry demand, salary insights, forward-looking trends, and career roadmaps.
- Tavily search: Web research tool for real-time technology demand, skill requirements, and market insights.
- search_jobs: Find actual active job listings requiring specific skills using the verified RapidAPI JSearch service.

When answering:
1. Research the requested skill or technology across industry demand and salary insights.
2. Search for relevant job openings using the search_jobs tool with appropriate location filters.
3. Structure your final output clearly with these exact sections:
   - INDUSTRY DEMAND OVERVIEW: Brief summary of market demand and growth.
   - SALARY INSIGHTS: Median, entry-level, and senior compensation figures if found.
   - KEY SKILLS: Top complementary skills and technical requirements.
   - ACTIVE JOB OPPORTUNITIES: Numbered list with Title, Company, Location, Salary (if disclosed), and Apply Link.
4. Always include application links for active job listings.
5. If salary or demand figures are estimates from web research, state so accurately.
"""


class SkillAgentRunner:
    """Manages agent lifecycle, tool discovery, and execution."""

    def __init__(self):
        self.settings = get_settings()

    async def _init_mcp_client(self) -> Optional[Any]:
        """Connects to Composio remote MCP server if configured."""
        if not self.settings.has_composio_key:
            logger.info("Composio API key not configured; skipping MCP tool discovery.")
            return None

        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient

            client = MultiServerMCPClient({
                "mcp_composio": {
                    "transport": "http",
                    "url": self.settings.COMPOSIO_MCP_URL,
                    "headers": {
                        "x-consumer-api-key": self.settings.COMPOSIO_API_KEY
                    }
                }
            })
            return client
        except ImportError:
            logger.warning("langchain-mcp-adapters not installed; skipping MCP tools.")
            return None
        except Exception as e:
            logger.warning("Failed to initialize MCP client: %s", str(e))
            return None

    def _init_model(self) -> Any:
        """Initializes Google Gemini model via LangChain."""
        if not self.settings.has_gemini_key:
            raise ConfigurationError("GEMINI_API_KEY is not configured on the server.")

        try:
            from langchain.chat_models import init_chat_model

            # Use configured model (default gemini-3.7-flash or user-specified)
            model_name = self.settings.GEMINI_MODEL
            # If model name has google_genai prefix, handle accordingly
            if not model_name.startswith("google_genai:"):
                model_identifier = f"google_genai:{model_name}"
            else:
                model_identifier = model_name

            model = init_chat_model(
                model_identifier,
                api_key=self.settings.GEMINI_API_KEY
            )
            return model
        except ImportError:
            raise AgentExecutionError("langchain-google-genai or langchain is not installed.")
        except Exception as e:
            raise ProviderAuthError("Gemini", details={"error": str(e)})

    async def execute(
        self,
        query: str,
        location: Optional[str] = None,
        country: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote_only: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """Executes the agent workflow and returns the response state."""
        tools: List[Any] = []
        tools_invoked: List[str] = []
        warnings: List[str] = []

        # 1. Discover MCP tools
        mcp_client = await self._init_mcp_client()
        if mcp_client:
            try:
                mcp_tools = await asyncio.wait_for(
                    mcp_client.get_tools(),
                    timeout=self.settings.REQUEST_TIMEOUT_SECONDS
                )
                logger.info("Loaded %d MCP tools from Composio.", len(mcp_tools))
                tools.extend(mcp_tools)
                tools_invoked.append("COMPOSIO_MCP")
            except asyncio.TimeoutError:
                warnings.append("Composio MCP server timed out during tool discovery; proceeding with local tools.")
                logger.warning("Composio MCP connection timed out.")
            except Exception as e:
                warnings.append(f"Composio MCP tools unavailable ({type(e).__name__}); proceeding with local tools.")
                logger.warning("Composio MCP error: %s", str(e))
        else:
            if not self.settings.has_composio_key:
                warnings.append("COMPOSIO_API_KEY not configured; web search tools omitted.")

        # 2. Add Tavily search tool if configured
        if self.settings.has_tavily_key:
            try:
                from langchain_tavily import TavilySearch

                tavily_tool = TavilySearch(
                    max_results=5,
                    search_depth="advanced",
                    tavily_api_key=self.settings.TAVILY_API_KEY,
                )
                tools.append(tavily_tool)
                tools_invoked.append("TAVILY_SEARCH")
                logger.info("Loaded Tavily Search tool.")
            except ImportError:
                warnings.append("langchain-tavily not installed; skipping Tavily tool.")
                logger.warning("langchain-tavily not installed.")
            except Exception as e:
                warnings.append(f"Tavily Search tool unavailable ({str(e)}).")
                logger.warning("Tavily initialization failed: %s", str(e))

        # 3. Add repaired RapidAPI job search tool
        search_jobs_tool = get_langchain_job_search_tool()
        tools.append(search_jobs_tool)
        tools_invoked.append("RAPIDAPI_JSEARCH")

        # 3. Initialize model
        model = self._init_model()

        # 4. Create agent graph
        try:
            from langchain.agents import create_agent

            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                debug=False,
            )
        except Exception as e:
            raise AgentExecutionError(f"Failed to compile LangGraph agent: {str(e)}")

        # 5. Build user query with explicit filter context if provided
        query_context = query
        filter_hints = []
        if location:
            filter_hints.append(f"Location preference: {location}")
        if country:
            filter_hints.append(f"Country code: {country}")
        if experience_level:
            filter_hints.append(f"Experience level: {experience_level}")
        if remote_only:
            filter_hints.append("Remote positions only")

        if filter_hints:
            query_context = f"{query}\n[User Context: {', '.join(filter_hints)}]"

        # 6. Invoke agent with bounded timeout and iterations
        try:
            timeout = self.settings.REQUEST_TIMEOUT_SECONDS * 3  # Allow multi-step reasoning
            response = await asyncio.wait_for(
                agent.ainvoke(
                    {"messages": [{"role": "user", "content": query_context}]},
                    config={"recursion_limit": self.settings.MAX_AGENT_ITERATIONS * 2}
                ),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise ProviderTimeoutError("Agent reasoning timeout", details={"timeout": timeout})
        except Exception as e:
            raise AgentExecutionError(f"Agent execution encountered an error: {str(e)}")

        # 7. Extract final content
        messages = response.get("messages", [])
        final_text = ""
        if messages:
            final_message = messages[-1]
            content = final_message.content
            if isinstance(content, str):
                final_text = content
            elif isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif hasattr(block, "text"):
                        text_parts.append(block.text)
                    elif isinstance(block, str):
                        text_parts.append(block)
                final_text = "\n".join(text_parts)

        return {
            "final_text": final_text,
            "messages": messages,
            "tools_invoked": tools_invoked,
            "warnings": warnings,
        }
