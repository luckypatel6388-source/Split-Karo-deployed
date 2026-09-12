from __future__ import annotations

from typing import Any

import requests


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class SplitKaroApi:
    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url.rstrip("/")
        self.session = session

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self.session.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                timeout=20,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Could not reach the backend: {exc}") from exc

        if response.ok:
            if not response.content:
                return None
            return response.json()

        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise ApiError(str(detail) or "The backend rejected this request.", response.status_code)

    def login(self, email: str, password: str) -> dict:
        return self.request("POST", "/auth/login", json={"email": email, "password": password})

    def register(self, name: str, email: str, password: str) -> dict:
        return self.request(
            "POST",
            "/auth/register",
            json={"name": name, "email": email, "password": password},
        )

    def me(self) -> dict:
        return self.request("GET", "/auth/me")

    def api_health(self) -> dict:
        return self.request("GET", "/health")

    def backend_health(self) -> dict:
        root_url = self.base_url.rsplit("/api/v1", 1)[0]
        try:
            response = self.session.get(f"{root_url}/health", timeout=20)
        except requests.RequestException as exc:
            raise ApiError(f"Could not reach the backend: {exc}") from exc
        if response.ok:
            return response.json()
        raise ApiError(response.text or "The backend rejected this request.", response.status_code)

    def logout(self) -> None:
        self.request("POST", "/auth/logout")

    def groups(self) -> list[dict]:
        return self.request("GET", "/users/me/groups")

    def create_group(self, name: str, description: str) -> dict:
        return self.request("POST", "/groups", json={"name": name, "description": description or None})

    def group(self, group_id: str) -> dict:
        return self.request("GET", f"/groups/{group_id}")

    def create_invite(self, group_id: str) -> dict:
        return self.request("POST", f"/groups/{group_id}/invite")

    def preview_invite(self, token: str) -> dict:
        return self.request("GET", f"/invites/{token}")

    def join_group(self, token: str) -> dict:
        return self.request("POST", f"/invites/{token}/join")

    def expenses(self, group_id: str) -> list[dict]:
        return self.request("GET", f"/groups/{group_id}/expenses")

    def balances(self, group_id: str) -> dict:
        return self.request("GET", f"/groups/{group_id}/balances")

    def settlements(self, group_id: str) -> dict:
        return self.request("GET", f"/groups/{group_id}/settlements")

    def create_optimized_settlements(self, group_id: str) -> list[dict]:
        return self.request("POST", f"/groups/{group_id}/settlements/optimized")

    def create_settlement(self, group_id: str, payload: dict) -> dict:
        return self.request("POST", f"/groups/{group_id}/settlements", json=payload)

    def get_settlement_record(self, group_id: str, settlement_id: str) -> dict:
        return self.request("GET", f"/groups/{group_id}/settlements/records/{settlement_id}")

    def mark_settlement_paid(self, group_id: str, settlement_id: str, payment_reference: str | None) -> dict:
        return self.request(
            "PATCH",
            f"/groups/{group_id}/settlements/{settlement_id}/paid",
            json={"payment_reference": payment_reference or None},
        )

    def initiate_payment(self, group_id: str, settlement_id: str, idempotency_key: str) -> dict:
        return self.request(
            "POST",
            f"/groups/{group_id}/payments/initiate",
            json={"settlement_id": settlement_id, "idempotency_key": idempotency_key},
        )

    def confirm_payment(self, payment_id: str, payment_reference: str) -> dict:
        return self.request(
            "POST",
            f"/payments/{payment_id}/confirm",
            json={"payment_reference": payment_reference},
        )

    def create_expense(self, group_id: str, payload: dict) -> dict:
        return self.request("POST", f"/groups/{group_id}/expenses", json=payload)

    def expense_detail(self, expense_id: str) -> dict:
        return self.request("GET", f"/expenses/{expense_id}")

    def update_expense(self, expense_id: str, payload: dict) -> dict:
        return self.request("PATCH", f"/expenses/{expense_id}", json=payload)

    def delete_expense(self, expense_id: str) -> dict | None:
        return self.request("DELETE", f"/expenses/{expense_id}")

    def create_expense_item(self, expense_id: str, payload: dict) -> dict:
        return self.request("POST", f"/expenses/{expense_id}/items", json=payload)

    def scan_bill(self, uploaded_file) -> dict:
        return self.request(
            "POST",
            "/bill-scan",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
        )

    def update_upi(self, upi_id: str) -> dict:
        return self.request("PATCH", "/users/me/upi", json={"upi_id": upi_id})