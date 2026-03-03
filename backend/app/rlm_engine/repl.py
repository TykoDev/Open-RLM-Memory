import uuid
import abc
import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

try:
    import docker
    from docker.errors import ContainerError, ImageNotFound, APIError
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class REPLSession:
    """Isolated REPL session for code execution."""
    id: str
    variables: Dict[str, Any]
    execution_history: List[str]

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.variables = {}
        self.execution_history = []


class ExecutionBackend(abc.ABC):
    """Abstract backend for code execution."""

    @abc.abstractmethod
    async def execute(self, code: str, variables: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """Execute code with given variables."""
        pass

    @abc.abstractmethod
    async def evaluate(self, expression: str, variables: Dict[str, Any], timeout: float = 30.0) -> Any:
        """Evaluate expression with given variables."""
        pass


class LocalExecutionBackend(ExecutionBackend):
    """Local execution backend using exec/eval in a thread pool."""

    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4)

    def _get_safe_namespace(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "__builtins__": {
                "len": len,
                "list": list,
                "dict": dict,
                "str": str,
                "int": int,
                "float": float,
                "sorted": sorted,
                "filter": filter,
                "map": map,
                "sum": sum,
                "min": min,
                "max": max,
                "range": range,
                "bool": bool,
                "tuple": tuple,
                "enumerate": enumerate,
                "zip": zip,
                "abs": abs,
                "round": round,
                # Add more safe builtins as needed
            },
            **variables,
        }

    def _execute_sync(self, code: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        namespace = self._get_safe_namespace(variables)
        exec(code, namespace)

        # Return updated variables (excluding builtins)
        return {k: v for k, v in namespace.items() if k != "__builtins__"}

    def _evaluate_sync(self, expression: str, variables: Dict[str, Any]) -> Any:
        namespace = self._get_safe_namespace(variables)
        return eval(expression, namespace)

    async def execute(self, code: str, variables: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(self._executor, self._execute_sync, code, variables),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Execution timed out after {timeout}s")
            raise TimeoutError("Execution timed out")
        except Exception:
            raise

    async def evaluate(self, expression: str, variables: Dict[str, Any], timeout: float = 30.0) -> Any:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(self._executor, self._evaluate_sync, expression, variables),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Evaluation timed out after {timeout}s")
            raise TimeoutError("Evaluation timed out")
        except Exception:
            raise


class DockerExecutionBackend(ExecutionBackend):
    """Execution backend using ephemeral Docker containers."""

    def __init__(self, image: str = "python:3.11-slim", mem_limit: str = "128m", cpu_quota: int = 50000):
        if not DOCKER_AVAILABLE:
            raise ImportError("docker package is required for DockerExecutionBackend")
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")
            self.client = None

        self.image = image
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota

    def _ensure_client(self):
        if not self.client:
            try:
                self.client = docker.from_env()
            except Exception as e:
                raise RuntimeError(f"Docker client not available: {e}")

    async def execute(self, code: str, variables: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        self._ensure_client()

        # Prepare script wrapper
        # We handle simple JSON-serializable variables for now.
        runner_script = """
import json
import sys

try:
    variables = json.loads(sys.argv[1])
except Exception:
    variables = {}

code = sys.argv[2]

try:
    exec(code, variables)
    # Remove potentially unsafe or non-serializable items
    result = {k: v for k, v in variables.items() if not k.startswith('__') and not hasattr(v, '__call__')}
    print(json.dumps({"status": "success", "variables": result}))
except Exception as e:
    print(json.dumps({"status": "error", "error": str(e)}))
"""

        command = ["python", "-c", runner_script, json.dumps(variables), code]

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.client.containers.run(
                    self.image,
                    command=command,
                    mem_limit=self.mem_limit,
                    cpu_quota=self.cpu_quota,
                    remove=True,
                    network_disabled=True,  # No network for security
                )
            )

            output = json.loads(result.decode("utf-8").strip())
            if output.get("status") == "error":
                raise RuntimeError(f"Execution error: {output.get('error')}")

            return output.get("variables", {})

        except Exception as e:
            logger.error(f"Docker execution failed: {e}")
            raise

    async def evaluate(self, expression: str, variables: Dict[str, Any], timeout: float = 30.0) -> Any:
        self._ensure_client()

        runner_script = """
import json
import sys

try:
    variables = json.loads(sys.argv[1])
except Exception:
    variables = {}

expression = sys.argv[2]

try:
    result = eval(expression, variables)
    print(json.dumps({"status": "success", "result": result}))
except Exception as e:
    print(json.dumps({"status": "error", "error": str(e)}))
"""
        command = ["python", "-c", runner_script, json.dumps(variables), expression]

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.client.containers.run(
                    self.image,
                    command=command,
                    mem_limit=self.mem_limit,
                    cpu_quota=self.cpu_quota,
                    remove=True,
                    network_disabled=True,
                )
            )

            output = json.loads(result.decode("utf-8").strip())
            if output.get("status") == "error":
                raise RuntimeError(f"Evaluation error: {output.get('error')}")

            return output.get("result")

        except Exception as e:
            logger.error(f"Docker evaluation failed: {e}")
            raise


class REPLEnvironment:
    """Sandboxed Python REPL for memory operations."""

    def __init__(self, backend: Optional[ExecutionBackend] = None):
        self.sessions: Dict[str, REPLSession] = {}
        self.backend = backend or LocalExecutionBackend()

    def create_session(self) -> str:
        """Create new isolated session."""
        session = REPLSession()
        self.sessions[session.id] = session
        logger.debug(f"repl_session_created session_id={session.id}")
        return session.id

    async def execute(self, code: str, session_id: str, timeout: float = 30.0) -> Dict[str, Any]:
        """Execute code in session context."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        try:
            # Delegate to backend
            updated_vars = await self.backend.execute(code, session.variables, timeout)

            # Update session variables
            session.variables.update(updated_vars)
            session.execution_history.append(code)

            logger.debug(
                f"repl_execute_success session_id={session_id} lines={len(code.splitlines())}"
            )

            return {"status": "success", "variables": session.variables}

        except Exception as e:
            logger.error(
                f"repl_execute_failed session_id={session_id} error={str(e)}"
            )
            raise

    async def evaluate(self, expression: str, session_id: str, timeout: float = 30.0) -> Any:
        """Evaluate expression in session context."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        try:
            result = await self.backend.evaluate(expression, session.variables, timeout)
            logger.debug(
                f"repl_evaluate_success session_id={session_id} expr={expression}"
            )
            return result
        except Exception as e:
            logger.error(
                f"repl_evaluate_failed session_id={session_id} expr={expression} error={str(e)}"
            )
            raise
