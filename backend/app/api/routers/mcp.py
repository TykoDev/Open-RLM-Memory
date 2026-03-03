"""MCP router using streamable HTTP transport without auth."""

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from loguru import logger

from app.database.connection import AsyncSessionLocal
from app.services.memory_service import MemoryNotFoundError, MemoryService
from app.services.rlm_service import rlm_service
from app.services.user_service import get_or_create_user_by_namespace, normalize_namespace

router = APIRouter(prefix="/mcp", tags=["MCP"])
well_known_router = APIRouter(tags=["MCP Metadata"])


@well_known_router.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource_metadata(request: Request):
    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/mcp"
    return {
        "resource": resource_url,
        "issuer": base_url,
        "authorization_servers": [],
        "scopes_supported": ["mcp"],
        "token_types_supported": [],
        "auth_required": False,
    }


@well_known_router.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_metadata_mcp(request: Request):
    return await oauth_protected_resource_metadata(request)


_sessions: dict[str, dict[str, Any]] = {}


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid datetime format; use ISO-8601"
        ) from exc


def _extract_namespace(request: Request, arguments: dict[str, Any]) -> str:
    requested = arguments.get("namespace")
    header_namespace = request.headers.get("X-Memory-Namespace")
    try:
        return normalize_namespace(requested or header_namespace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def _search_memory(
    namespace: str,
    query: str,
    limit: int = 10,
    enable_rlm: bool = True,
    memory_type: str | None = None,
    session_id: str | None = None,
) -> str:
    async with AsyncSessionLocal() as db:
        try:
            user = await get_or_create_user_by_namespace(db, namespace)
            filters = {"type": memory_type} if memory_type else None

            service = MemoryService(db, rlm=rlm_service)
            results, rlm_metrics, processing_time = await service.search_memory(
                query=query,
                limit=limit,
                user_id=str(user.id),
                filters=filters,
                enable_rlm=enable_rlm,
                session_id=session_id,
            )

            formatted_results = [
                {
                    "id": str(memory.id),
                    "content": memory.content,
                    "type": memory.type,
                    "tags": memory.tags,
                    "score": float(score),
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                }
                for memory, score in results
            ]
            return json.dumps(
                {
                    "namespace": namespace,
                    "results": formatted_results,
                    "total": len(formatted_results),
                    "processing_time_ms": processing_time,
                    "rlm_metrics": rlm_metrics,
                },
                indent=2,
            )
        except Exception as exc:
            logger.error(f"search_memory failed: {exc}")
            return json.dumps({"namespace": namespace, "error": str(exc), "results": [], "total": 0}, indent=2)


async def _list_memory(
    namespace: str,
    limit: int = 100,
    offset: int = 0,
    tags: list[str] | None = None,
    memory_type: str | None = None,
    metadata: dict[str, Any] | None = None,
    created_before: str | None = None,
    created_after: str | None = None,
) -> str:
    async with AsyncSessionLocal() as db:
        try:
            user = await get_or_create_user_by_namespace(db, namespace)
            before_dt = _parse_iso_datetime(created_before)
            after_dt = _parse_iso_datetime(created_after)

            service = MemoryService(db, rlm=rlm_service)
            memories = await service.list_memories(
                user_id=str(user.id),
                limit=limit,
                offset=offset,
                tags=tags,
                memory_type=memory_type,
                metadata=metadata,
                created_before=before_dt,
                created_after=after_dt,
            )

            formatted = [
                {
                    "id": str(memory.id),
                    "content": memory.content,
                    "type": memory.type,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                    "updated_at": memory.updated_at.isoformat() if memory.updated_at else None,
                    "metadata": memory.metadata_,
                }
                for memory in memories
            ]
            return json.dumps({"namespace": namespace, "results": formatted, "total": len(formatted)}, indent=2)
        except Exception as exc:
            logger.error(f"list_memory failed: {exc}")
            return json.dumps({"namespace": namespace, "status": "error", "error": str(exc)}, indent=2)


async def _save_memory(
    namespace: str,
    content: str,
    memory_type: str = "knowledge",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    async with AsyncSessionLocal() as db:
        try:
            user = await get_or_create_user_by_namespace(db, namespace)
            service = MemoryService(db, rlm=rlm_service)
            result = await service.save_memory(
                content=content,
                memory_type=memory_type,
                tags=list(tags or []),
                metadata=dict(metadata or {}),
                user_id=str(user.id),
            )
            return json.dumps(
                {
                    "namespace": namespace,
                    "status": "saved",
                    "id": str(result.memory.id),
                    "type": result.memory.type,
                    "tags": result.memory.tags,
                    "content_preview": content[:100] + "..." if len(content) > 100 else content,
                    "created_at": result.memory.created_at.isoformat() if result.memory.created_at else None,
                    "embedding_generated": not result.embedding_is_fallback,
                    "classified_by_llm": result.classified_by_llm,
                },
                indent=2,
            )
        except Exception as exc:
            logger.error(f"save_memory failed: {exc}")
            return json.dumps({"namespace": namespace, "status": "error", "error": str(exc)}, indent=2)


async def _delete_memory(namespace: str, memory_id: str) -> str:
    async with AsyncSessionLocal() as db:
        try:
            user = await get_or_create_user_by_namespace(db, namespace)
            service = MemoryService(db, rlm=rlm_service)
            deleted_at = await service.delete_memory(memory_id, str(user.id))
            return json.dumps(
                {
                    "namespace": namespace,
                    "status": "deleted",
                    "id": memory_id,
                    "deleted_at": deleted_at.isoformat(),
                },
                indent=2,
            )
        except MemoryNotFoundError:
            return json.dumps(
                {"namespace": namespace, "status": "error", "error": f"Memory {memory_id} not found"}, indent=2
            )
        except Exception as exc:
            logger.error(f"delete_memory failed: {exc}")
            return json.dumps({"namespace": namespace, "status": "error", "error": str(exc)}, indent=2)


@router.post("")
async def mcp_post(request: Request):
    try:
        body = await request.json()
        method = body.get("method", "")
        request_id = body.get("id")
        params = body.get("params", {})

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "Open RLM Memory", "version": "1.0.0"},
                    "capabilities": {"tools": {"listChanged": True}},
                },
            }
            session_id = str(uuid.uuid4())
            _sessions[session_id] = {"initialized": True}
            return Response(
                content=json.dumps(response), media_type="application/json", headers={"mcp-session-id": session_id}
            )

        if method == "notifications/initialized":
            return Response(content="", status_code=204)

        if method == "tools/list":
            ns_desc = (
                "Namespace to scope this operation. Namespaces isolate memories so different "
                "projects or contexts don't mix. If omitted, falls back to the X-Memory-Namespace "
                "HTTP header, then to the server default ('local')."
            )
            tools = [
                {
                    "name": "search_memory",
                    "description": "Search memories for a namespace using semantic similarity.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": ns_desc},
                            "query": {"type": "string", "description": "Natural language search query."},
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "description": "Maximum number of results to return.",
                            },
                            "enable_rlm": {
                                "type": "boolean",
                                "default": True,
                                "description": "When true, enables RLM query decomposition and re-ranking for more relevant results. Disable for raw vector search.",
                            },
                            "memory_type": {
                                "type": "string",
                                "description": "Filter results to this memory type (e.g. 'knowledge', 'code_snippet').",
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Optional session identifier for cache keying.",
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "list_memory",
                    "description": "List memories for a namespace.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": ns_desc},
                            "limit": {
                                "type": "integer",
                                "default": 100,
                                "description": "Maximum number of memories to return.",
                            },
                            "offset": {
                                "type": "integer",
                                "default": 0,
                                "description": "Number of memories to skip (for pagination).",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter to memories that have all of these tags.",
                            },
                            "memory_type": {
                                "type": "string",
                                "description": "Filter to memories of this type.",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Filter by arbitrary metadata key-value pairs.",
                            },
                            "created_before": {
                                "type": "string",
                                "description": "ISO-8601 datetime upper bound for created_at.",
                            },
                            "created_after": {
                                "type": "string",
                                "description": "ISO-8601 datetime lower bound for created_at.",
                            },
                        },
                    },
                },
                {
                    "name": "save_memory",
                    "description": (
                        "Save a memory. The server automatically classifies the type and generates tags "
                        "using an LLM -- just provide the content. Only set memory_type or tags if you "
                        "need to override the auto-classification."
                    ),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": ns_desc},
                            "content": {
                                "type": "string",
                                "description": "The text content to save as a memory. Accepts any text: notes, code, conversations, facts, preferences, etc.",
                            },
                            "memory_type": {
                                "type": "string",
                                "description": "Override auto-classification. Only set this if you explicitly want a specific type.",
                                "enum": ["knowledge", "context", "summary", "event", "code_snippet", "preference"],
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Override auto-generated tags. Only set this if you explicitly want specific tags.",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Arbitrary key-value metadata to attach to the memory.",
                            },
                        },
                        "required": ["content"],
                    },
                },
                {
                    "name": "delete_memory",
                    "description": "Delete one memory by id for a namespace.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": ns_desc},
                            "memory_id": {
                                "type": "string",
                                "description": "UUID of the memory to delete.",
                            },
                        },
                        "required": ["memory_id"],
                    },
                },
            ]
            return Response(
                content=json.dumps({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}),
                media_type="application/json",
            )

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            namespace = _extract_namespace(request, arguments)

            if tool_name == "search_memory":
                result = await _search_memory(
                    namespace=namespace, **{k: v for k, v in arguments.items() if k != "namespace"}
                )
            elif tool_name == "list_memory":
                result = await _list_memory(
                    namespace=namespace, **{k: v for k, v in arguments.items() if k != "namespace"}
                )
            elif tool_name == "save_memory":
                result = await _save_memory(
                    namespace=namespace, **{k: v for k, v in arguments.items() if k != "namespace"}
                )
            elif tool_name == "delete_memory":
                result = await _delete_memory(
                    namespace=namespace, **{k: v for k, v in arguments.items() if k != "namespace"}
                )
            else:
                return Response(
                    content=json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                        }
                    ),
                    media_type="application/json",
                    status_code=400,
                )

            return Response(
                content=json.dumps(
                    {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": result}]}}
                ),
                media_type="application/json",
            )

        return Response(
            content=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
            ),
            media_type="application/json",
            status_code=400,
        )

    except json.JSONDecodeError:
        return Response(content=json.dumps({"error": "Invalid JSON"}), media_type="application/json", status_code=400)
    except HTTPException as exc:
        return Response(
            content=json.dumps({"error": exc.detail}), media_type="application/json", status_code=exc.status_code
        )
    except Exception as exc:
        logger.error(f"MCP error: {exc}")
        return Response(content=json.dumps({"error": str(exc)}), media_type="application/json", status_code=500)


@router.get("")
async def mcp_get(request: Request):
    _ = request.headers.get("mcp-session-id")

    async def event_stream():
        yield 'data: {"type": "ping"}\n\n'

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.delete("")
async def mcp_delete(request: Request):
    session_id = request.headers.get("mcp-session-id")
    if session_id and session_id in _sessions:
        del _sessions[session_id]
        return {"status": "closed", "session_id": session_id}
    return {"status": "no_session"}


@router.get("/info")
async def mcp_info():
    return {
        "endpoint": "/mcp",
        "transport": "streamable-http",
        "tools": ["search_memory", "list_memory", "save_memory", "delete_memory"],
        "protocol_version": "2024-11-05",
        "server_name": "Open RLM Memory",
        "auth_required": False,
    }
