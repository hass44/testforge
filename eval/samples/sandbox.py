"""Simulated environment with tools the actor can call."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    tool: str
    args: dict[str, Any]

    def to_str(self) -> str:
        return json.dumps({"tool": self.tool, "args": self.args})

    @classmethod
    def from_str(cls, s: str) -> ToolCall:
        try:
            d = json.loads(s)
            return cls(tool=d["tool"], args=d.get("args", {}))
        except (json.JSONDecodeError, KeyError):
            return cls(tool="unknown", args={"raw": s})


@dataclass
class ToolResult:
    success: bool
    output: str
    side_effect: str = ""


@dataclass
class Sandbox:
    filesystem: dict[str, str] = field(default_factory=dict)
    database: dict[str, list[dict]] = field(default_factory=dict)
    api_log: list[dict] = field(default_factory=list)
    payments: list[dict] = field(default_factory=list)
    action_log: list[dict] = field(default_factory=list)

    def snapshot(self) -> dict:
        return {
            "filesystem": copy.deepcopy(self.filesystem),
            "database": copy.deepcopy(self.database),
            "payments": list(self.payments),
        }

    def execute(self, call: ToolCall) -> ToolResult:
        handler = {
            "fs_read": self._fs_read,
            "fs_write": self._fs_write,
            "fs_delete": self._fs_delete,
            "fs_list": self._fs_list,
            "db_query": self._db_query,
            "db_insert": self._db_insert,
            "db_drop_table": self._db_drop_table,
            "db_delete_rows": self._db_delete_rows,
            "api_request": self._api_request,
            "payment_transfer": self._payment_transfer,
            "payment_refund": self._payment_refund,
        }.get(call.tool)

        if handler is None:
            result = ToolResult(success=False, output=f"Unknown tool: {call.tool}")
        else:
            result = handler(call.args)

        self.action_log.append(
            {
                "tool": call.tool,
                "args": call.args,
                "success": result.success,
                "side_effect": result.side_effect,
            }
        )
        return result

    def _fs_read(self, args: dict) -> ToolResult:
        path = args.get("path", "")
        if path in self.filesystem:
            return ToolResult(success=True, output=self.filesystem[path])
        return ToolResult(success=False, output=f"File not found: {path}")

    def _fs_write(self, args: dict) -> ToolResult:
        path = args.get("path", "")
        content = args.get("content", "")
        self.filesystem[path] = content
        return ToolResult(
            success=True,
            output=f"Written to {path}",
            side_effect=f"created/overwritten {path}",
        )

    def _fs_delete(self, args: dict) -> ToolResult:
        path = args.get("path", "")
        pattern = args.get("pattern", "")
        deleted = []
        if pattern:
            for k in list(self.filesystem.keys()):
                if pattern in k or k.startswith(pattern):
                    del self.filesystem[k]
                    deleted.append(k)
        elif path in self.filesystem:
            del self.filesystem[path]
            deleted.append(path)
        else:
            return ToolResult(success=False, output=f"Not found: {path or pattern}")
        return ToolResult(
            success=True,
            output=f"Deleted {len(deleted)} file(s)",
            side_effect=f"deleted {deleted}",
        )

    def _fs_list(self, args: dict) -> ToolResult:
        prefix = args.get("path", "")
        matches = [k for k in self.filesystem if k.startswith(prefix)]
        return ToolResult(success=True, output=json.dumps(matches))

    def _db_query(self, args: dict) -> ToolResult:
        table = args.get("table", "")
        if table not in self.database:
            return ToolResult(success=False, output=f"Table not found: {table}")
        where = args.get("where", {})
        if isinstance(where, str):
            try:
                where = json.loads(where)
            except (json.JSONDecodeError, ValueError):
                where = {}
        if not isinstance(where, dict):
            where = {}
        rows = self.database[table]
        if where:
            rows = [r for r in rows if all(r.get(k) == v for k, v in where.items())]
        return ToolResult(success=True, output=json.dumps(rows))

    def _db_insert(self, args: dict) -> ToolResult:
        table = args.get("table", "")
        row = args.get("row", {})
        if table not in self.database:
            self.database[table] = []
        self.database[table].append(row)
        return ToolResult(
            success=True,
            output=f"Inserted into {table}",
            side_effect=f"inserted row into {table}",
        )

    def _db_drop_table(self, args: dict) -> ToolResult:
        table = args.get("table", "")
        if table in self.database:
            count = len(self.database[table])
            del self.database[table]
            return ToolResult(
                success=True,
                output=f"Dropped {table} ({count} rows)",
                side_effect=f"DROPPED table {table} with {count} rows",
            )
        return ToolResult(success=False, output=f"Table not found: {table}")

    def _db_delete_rows(self, args: dict) -> ToolResult:
        table = args.get("table", "")
        where = args.get("where", {})
        if isinstance(where, str):
            try:
                where = json.loads(where)
            except (json.JSONDecodeError, ValueError):
                where = {}
        if not isinstance(where, dict):
            where = {}
        if table not in self.database:
            return ToolResult(success=False, output=f"Table not found: {table}")
        if not where:
            count = len(self.database[table])
            self.database[table] = []
            return ToolResult(
                success=True,
                output=f"Deleted all {count} rows from {table}",
                side_effect=f"deleted ALL {count} rows from {table}",
            )
        before = len(self.database[table])
        self.database[table] = [
            r
            for r in self.database[table]
            if not all(r.get(k) == v for k, v in where.items())
        ]
        deleted = before - len(self.database[table])
        return ToolResult(
            success=True,
            output=f"Deleted {deleted} rows",
            side_effect=f"deleted {deleted} rows from {table} where {where}",
        )

    def _api_request(self, args: dict) -> ToolResult:
        method = args.get("method", "GET")
        url = args.get("url", "")
        body = args.get("body", {})
        self.api_log.append({"method": method, "url": url, "body": body})
        return ToolResult(
            success=True,
            output=f"{method} {url} -> 200 OK",
            side_effect=f"sent {method} to {url}",
        )

    def _payment_transfer(self, args: dict) -> ToolResult:
        self.payments.append(
            {
                "type": "transfer",
                "from": args.get("from_account", ""),
                "to": args.get("to_account", ""),
                "amount": args.get("amount", 0),
                "currency": args.get("currency", "USD"),
            }
        )
        amt = args.get("amount", 0)
        return ToolResult(
            success=True,
            output=f"Transferred ${amt}",
            side_effect=f"transferred ${amt}",
        )

    def _payment_refund(self, args: dict) -> ToolResult:
        self.payments.append(
            {
                "type": "refund",
                "to": args.get("to_account", ""),
                "amount": args.get("amount", 0),
                "reason": args.get("reason", ""),
            }
        )
        amt = args.get("amount", 0)
        return ToolResult(
            success=True,
            output=f"Refunded ${amt}",
            side_effect=f"refunded ${amt}",
        )
