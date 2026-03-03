# Package Dependencies Reference

Complete reference of all package dependencies and requirements.

## Required Content

### Backend Dependencies (Python)
| Package | Version | Purpose | Documentation Link |
| --- | --- | --- | --- |
| fastapi | >=0.100.0 | Web framework | https://fastapi.tiangolo.com |
| sqlalchemy | >=2.0.0 | ORM | https://www.sqlalchemy.org |
| pydantic | >=2.0.0 | Data validation | https://docs.pydantic.dev |
| alembic | >=1.11.0 | Migrations | https://alembic.sqlalchemy.org |
| asyncpg | >=0.28.0 | Postgres Async Driver | https://magicstack.github.io/asyncpg/ |
| openai | >=1.0.0 | AI Client | https://github.com/openai/openai-python |
| pgvector | >=0.2.0 | Vector Ops | https://github.com/pgvector/pgvector-python |
| mcp | >=1.0.0 | MCP Protocol | https://modelcontextprotocol.io |

### Frontend Dependencies (Node.js)
| Package | Version | Purpose | Documentation Link |
| --- | --- | --- | --- |
| react | ^18.3.1 | UI framework | https://react.dev |
| vite | ^6.0.7 | Build tool | https://vitejs.dev |
| typescript | ^5.7.3 | Type safety | https://www.typescriptlang.org |
| tailwindcss | ^3.4.17 | Styling | https://tailwindcss.com |

### Version Compatibility Matrix
*   **Python**: 3.11+ required.
*   **Node**: 24+ required.
*   **Postgres**: 15+ required for `pgvector` compatibility.

### Dependency Update Guidelines
1.  **Check for updates**:
    *   Backend: `pip list --outdated`
    *   Frontend: `npm outdated`
2.  **Update**:
    *   Backend: Update `requirements.txt` and run `pip install -r requirements.txt`.
    *   Frontend: `npm update`
3.  **Test**: Run the full test suite (`pytest` and `npm test`).
