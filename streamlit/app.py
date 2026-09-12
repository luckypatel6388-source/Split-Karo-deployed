from __future__ import annotations

from decimal import Decimal, InvalidOperation

import pandas as pd
import requests
import streamlit as st
from secrets import token_urlsafe

from api_client import ApiError, SplitKaroApi


st.set_page_config(page_title="Split Karo", page_icon="S", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink:#18202b; --muted:#667085; --mint:#d8f8ed; --green:#0c8f72; --cream:#f6f8fb; --line:#dfe5ee; --coral:#ff6b5f; --yellow:#ffd166; --blue:#4c6fff; }
    html, body, [class*="css"] { font-family:'DM Sans', sans-serif; color:var(--ink); }
    [data-testid="stAppViewContainer"] *, [data-testid="stMain"] * { color:var(--ink); }
    [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] small { color:var(--ink); }
    [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3, [data-testid="stAppViewContainer"] h4 { color:var(--ink) !important; }
    [data-testid="stAppViewContainer"] { background-color:var(--cream); background-image:radial-gradient(#dfe5ee 1px, transparent 1px); background-size:18px 18px; }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:#18202b; border-right:4px solid var(--yellow); }
    [data-testid="stSidebar"] * { color:#f5f7fb !important; }
    [data-testid="stSidebar"] input { color:#18202b !important; background:#ffffff !important; }
    h1,h2,h3 { font-family:'Space Grotesk', sans-serif; letter-spacing:0; }
    h1 { font-size:2.65rem !important; line-height:1.04 !important; }
    .eyebrow { color:var(--blue); font-size:.75rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
    .hero { padding:1.5rem 0 .7rem; }
    .hero p { color:var(--muted); font-size:1.05rem; margin-top:.4rem; }
    .metric { background:white; border:1px solid var(--line); border-top:5px solid var(--yellow); border-radius:12px; padding:1.05rem 1.2rem; min-height:112px; box-shadow:0 8px 22px rgba(24,32,43,.06); }
    .metric-label { color:var(--muted); font-size:.82rem; font-weight:600; }
    .metric-value { color:var(--ink); font-family:'Space Grotesk'; font-size:1.9rem; font-weight:700; margin-top:.35rem; }
    .metric-note { color:var(--green); font-size:.78rem; margin-top:.15rem; font-weight:600; }
    .section { border-top:1px solid var(--line); margin-top:1.8rem; padding-top:1.2rem; }
    .stButton > button, .stFormSubmitButton > button { border-radius:10px; border:2px solid var(--ink); background:var(--green) !important; color:white !important; font-weight:700; min-height:2.7rem; box-shadow:3px 3px 0 var(--ink); transition:transform .15s ease, box-shadow .15s ease, background .15s ease; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { background:#08745d !important; color:white !important; transform:translate(-1px, -1px); box-shadow:5px 5px 0 var(--ink); }
    .stButton > button:focus, .stFormSubmitButton > button:focus { outline:3px solid var(--yellow); outline-offset:2px; }
    .stButton > button p, .stFormSubmitButton > button p { color:white !important; }
    .stButton > button[kind="secondary"], .stFormSubmitButton > button[kind="secondary"] { background:white !important; color:var(--ink) !important; }
    .stButton > button[kind="secondary"] p, .stFormSubmitButton > button[kind="secondary"] p { color:var(--ink) !important; }
    [data-baseweb="tab"] { font-weight:700; }
    [data-baseweb="tab"] p, [data-baseweb="tab"] span { color:var(--ink) !important; }
    [data-baseweb="tab-highlight"] { background:var(--coral); }
    [data-testid="stForm"] { background:rgba(255,255,255,.82); border:1px solid var(--line); border-radius:14px; padding:1.2rem; box-shadow:0 8px 22px rgba(24,32,43,.05); }
    [data-testid="stTextInput"] label, [data-testid="stNumberInput"] label, [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label, [data-testid="stFileUploader"] label, [data-testid="stRadio"] label { color:var(--ink) !important; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] { color:var(--ink) !important; background:#ffffff !important; }
    div[data-testid="stDataFrame"] { border:1px solid var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)


def api() -> SplitKaroApi:
    if "http" not in st.session_state:
        st.session_state.http = requests.Session()
    return SplitKaroApi(st.session_state.get("api_url", "http://127.0.0.1:8000/api/v1"), st.session_state.http)


def money(value) -> str:
    try:
        return f"₹{Decimal(str(value)):,.2f}"
    except (InvalidOperation, TypeError, ValueError):
        return "₹0.00"


def show_error(error: ApiError) -> None:
    if error.status_code == 401:
        st.session_state.authenticated = False
        st.warning("Your session has expired. Please sign in again.")
    else:
        st.error(str(error))


def auth_screen() -> None:
    st.markdown('<div class="eyebrow">Group expenses, without the spreadsheet</div>', unsafe_allow_html=True)
    st.title("Split the cost. Keep the friendship.")
    st.write("A calm command center for shared bills, balances, and clean settlements.")
    with st.container(border=True):
        login, register = st.tabs(["Sign in", "Create account"])
        with login:
            with st.form("login"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", width="stretch")
                if submitted:
                    try:
                        result = api().login(email.strip(), password)
                        st.session_state.user = result["user"]
                        st.session_state.authenticated = True
                        st.rerun()
                    except ApiError as error:
                        show_error(error)
        with register:
            with st.form("register"):
                name = st.text_input("Your name")
                email = st.text_input("Email", key="register_email")
                password = st.text_input("Password", type="password", key="register_password", help="Use at least 8 characters.")
                submitted = st.form_submit_button("Create account", width="stretch")
                if submitted:
                    try:
                        result = api().register(name.strip(), email.strip(), password)
                        st.session_state.user = result["user"]
                        st.session_state.authenticated = True
                        st.rerun()
                    except ApiError as error:
                        show_error(error)


def load_dashboard(group_id: str) -> None:
    if st.session_state.get("loaded_group") == group_id:
        return
    try:
        st.session_state.group_detail = api().group(group_id)
        st.session_state.expenses = api().expenses(group_id)
        st.session_state.balances = api().balances(group_id).get("balances", [])
        st.session_state.settlements = api().settlements(group_id).get("settlements", [])
        st.session_state.settlement_records = st.session_state.get("settlement_records", [])
        st.session_state.loaded_group = group_id
    except ApiError as error:
        show_error(error)


def sidebar(groups: list[dict]) -> str:
    with st.sidebar:
        st.markdown("# Split Karo")
        st.caption("Your shared money, made legible.")
        selected = st.selectbox("Workspace", groups, format_func=lambda group: group["name"], key="group_select")
        st.divider()
        st.markdown(f"**{st.session_state.user.get('name', 'Account')}**")
        st.caption(st.session_state.user.get("email", ""))
        with st.expander("Invites"):
            if st.button("Create invite", width="stretch"):
                try:
                    invite = api().create_invite(selected["id"])
                    st.code(invite.get("invite_url", invite.get("token", "")), language="text")
                except ApiError as error:
                    show_error(error)
            invite_token = st.text_input("Invite token", placeholder="Paste a token")
            if st.button("Preview invite", width="stretch") and invite_token.strip():
                try:
                    st.session_state.invite_preview = api().preview_invite(invite_token.strip())
                    st.session_state.invite_token = invite_token.strip()
                except ApiError as error:
                    show_error(error)
            preview = st.session_state.get("invite_preview")
            if preview:
                st.info(f"{preview.get('group_name', 'Group')}: {preview.get('group_description') or 'No description'}")
                if st.button("Join this group", key="join_invite", width="stretch"):
                    try:
                        result = api().join_group(st.session_state.invite_token)
                        st.session_state.pop("invite_preview", None)
                        st.session_state.pop("invite_token", None)
                        st.success(result.get("message", "Joined group."))
                        st.rerun()
                    except ApiError as error:
                        show_error(error)
        with st.expander("Account settings"):
            upi = st.text_input("UPI ID", value=st.session_state.user.get("upi_id") or "", placeholder="name@upi")
            if st.button("Save UPI", width="stretch"):
                try:
                    result = api().update_upi(upi.strip())
                    st.success(result.get("message", "UPI updated."))
                except ApiError as error:
                    show_error(error)
        if st.button("Sign out", width="stretch"):
            try:
                api().logout()
            except ApiError:
                pass
            st.session_state.clear()
            st.rerun()
    return selected["id"]


def dashboard(group: dict, group_id: str) -> None:
    load_dashboard(group_id)
    expenses = st.session_state.get("expenses", [])
    balances = st.session_state.get("balances", [])
    settlements = st.session_state.get("settlements", [])
    user_id = st.session_state.user["id"]
    owed_to_me = sum((Decimal(str(item["balance"])) for item in balances if Decimal(str(item["balance"])) > 0), Decimal("0"))
    i_owe = abs(sum((Decimal(str(item["balance"])) for item in balances if Decimal(str(item["balance"])) < 0), Decimal("0")))

    st.markdown('<div class="hero"><div class="eyebrow">Overview / selected group</div>', unsafe_allow_html=True)
    st.title(group["name"])
    st.write(group.get("description") or "A shared space for every dinner, trip, and tiny IOU.")
    st.markdown("</div>", unsafe_allow_html=True)
    columns = st.columns(4)
    metrics = [("Group spend", money(sum((Decimal(str(item["amount"])) for item in expenses), Decimal("0"))), f"{len(expenses)} expenses"), ("You are owed", money(owed_to_me), "net positive balances"), ("You owe", money(i_owe), "net negative balances"), ("To settle", str(len(settlements)), "optimized transfers")]
    for column, (label, value, note) in zip(columns, metrics):
        column.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

    overview, settle, add, scan = st.tabs(["Activity", "Settle up", "Add expense", "Scan a bill"])
    with overview:
        left, right = st.columns([1.35, 1])
        with left:
            st.markdown('<div class="section"><h3>Recent expenses</h3></div>', unsafe_allow_html=True)
            if expenses:
                rows = [{"Expense": item["title"], "Paid by": item.get("payer_name", ""), "Amount": money(item["amount"]), "Split": item["split_type"].title()} for item in expenses]
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                with st.expander("Expense actions"):
                    expense_options = {f"{item['title']} ({money(item['amount'])})": item["expense_id"] for item in expenses}
                    selected_expense = st.selectbox("Choose an expense", list(expense_options))
                    expense_id = expense_options[selected_expense]
                    if st.button("View details", width="stretch"):
                        try:
                            st.json(api().expense_detail(expense_id))
                        except ApiError as error:
                            show_error(error)
                    edit_title = st.text_input("Updated title", value=selected_expense.rsplit(" (", 1)[0])
                    edit_amount = st.number_input("Updated amount", min_value=0.01, step=1.0, format="%.2f")
                    if st.button("Update expense", width="stretch"):
                        try:
                            api().update_expense(expense_id, {"title": edit_title.strip(), "amount": f"{edit_amount:.2f}"})
                            st.session_state.loaded_group = None
                            st.success("Expense updated.")
                            st.rerun()
                        except ApiError as error:
                            show_error(error)
                    if st.button("Delete expense", width="stretch"):
                        try:
                            api().delete_expense(expense_id)
                            st.session_state.loaded_group = None
                            st.success("Expense deleted.")
                            st.rerun()
                        except ApiError as error:
                            show_error(error)
                    st.markdown("**Add a line item**")
                    item_name = st.text_input("Item name", key="item_name")
                    item_price = st.number_input("Item unit price", min_value=0.01, step=1.0, format="%.2f", key="item_price")
                    item_participants = st.multiselect("Item participants", [member["user_id"] for member in group.get("members", [])], format_func=lambda member_id: next((member["name"] for member in group.get("members", []) if member["user_id"] == member_id), member_id), key="item_participants")
                    if st.button("Add line item", width="stretch"):
                        if not item_name.strip() or not item_participants:
                            st.error("Add an item name and at least one participant.")
                            return
                        try:
                            api().create_expense_item(expense_id, {"name": item_name.strip(), "quantity": "1.00", "unit_price": f"{item_price:.2f}", "participants": [{"user_id": member_id, "share_amount": f"{item_price / max(len(item_participants), 1):.2f}"} for member_id in item_participants]})
                            st.success("Line item added.")
                        except ApiError as error:
                            show_error(error)
            else:
                st.info("No expenses here yet. Add the first shared bill.")
        with right:
            st.markdown('<div class="section"><h3>Balances</h3></div>', unsafe_allow_html=True)
            for balance in balances:
                amount = Decimal(str(balance["balance"]))
                tone = "#16794e" if amount >= 0 else "#c45c4a"
                st.markdown(f"**{balance['user_name']}** <span style='float:right;color:{tone};font-weight:700'>{money(amount)}</span>", unsafe_allow_html=True)
            st.markdown('<div class="section"><h3>Suggested settlements</h3></div>', unsafe_allow_html=True)
            if settlements:
                for settlement in settlements:
                    st.markdown(f"{settlement['from_user_name']} → **{settlement['to_user_name']}**  \\  {money(settlement['amount'])}")
            else:
                st.caption("Everyone is square for now.")
    with settle:
        settlement_center(group, group_id, settlements)
    with add:
        add_expense_form(group, group_id, user_id)
    with scan:
        bill_scanner()


def settlement_center(group: dict, group_id: str, previews: list[dict]) -> None:
    st.write("Turn the suggested transfers into records, then pay and confirm them from one place.")
    if previews and st.button("Create all suggested settlements", type="primary", width="stretch"):
        try:
            created = api().create_optimized_settlements(group_id)
            st.session_state.settlement_records = created
            st.session_state.loaded_group = None
            st.success(f"Created {len(created)} settlement record(s).")
            st.rerun()
        except ApiError as error:
            show_error(error)

    records = st.session_state.get("settlement_records", [])
    if not records:
        st.info("Create the suggested settlements above to unlock payment actions.")
        with st.expander("Create a manual settlement"):
            members = group.get("members", [])
            member_names = {member["user_id"]: member["name"] for member in members}
            member_ids = list(member_names)
            if len(member_ids) < 2:
                st.caption("You need at least two group members.")
                return
            with st.form("manual_settlement"):
                from_user = st.selectbox("From", member_ids, format_func=lambda value: member_names[value])
                to_user = st.selectbox("To", [value for value in member_ids if value != from_user], format_func=lambda value: member_names[value])
                amount = st.number_input("Amount", min_value=0.01, step=1.0, format="%.2f")
                payment_method = st.text_input("Payment method", value="UPI")
                if st.form_submit_button("Create manual settlement", width="stretch"):
                    try:
                        record = api().create_settlement(group_id, {"from_user_id": from_user, "to_user_id": to_user, "amount": f"{amount:.2f}", "payment_method": payment_method.strip() or None})
                        st.session_state.settlement_records = [record]
                        st.success("Settlement record created.")
                        st.rerun()
                    except ApiError as error:
                        show_error(error)
        return

    for record in records:
        settlement_record_card(group_id, record)


def settlement_record_card(group_id: str, record: dict) -> None:
    settlement_id = record.get("id")
    status = record.get("status", "pending")
    st.markdown(f"### {record.get('from_user_name', 'Payer')} → {record.get('to_user_name', 'Receiver')}")
    columns = st.columns(4)
    columns[0].metric("Amount", money(record.get("amount")))
    columns[1].metric("Status", status.replace("_", " ").title())
    columns[2].metric("Method", record.get("payment_method") or "Manual")
    columns[3].metric("Reference", record.get("payment_reference") or "Not added")

    if status.lower() in {"paid", "completed", "success"}:
        st.success("This settlement is complete.")
        return

    action_columns = st.columns(3)
    if action_columns[0].button("Pay with UPI", key=f"pay_{settlement_id}"):
        try:
            payment = api().initiate_payment(group_id, settlement_id, token_urlsafe(18)) #type:ignore
            st.session_state.payments = {**st.session_state.get("payments", {}), settlement_id: payment}
            st.success(payment.get("message", "Payment initiated."))
            if payment.get("upi_uri"):
                st.code(payment["upi_uri"], language="text")
        except ApiError as error:
            show_error(error)
    if action_columns[1].button("Refresh record", key=f"refresh_{settlement_id}"):
        try:
            refreshed = api().get_settlement_record(group_id, settlement_id) #type:ignore
            st.session_state.settlement_records = [refreshed if item.get("id") == settlement_id else item for item in st.session_state.settlement_records]
            st.rerun()
        except ApiError as error:
            show_error(error)
    with action_columns[2].expander("Mark as paid"):
        reference = st.text_input("Payment reference", key=f"reference_{settlement_id}", placeholder="UPI transaction ID")
        if st.button("Confirm paid", key=f"paid_{settlement_id}"):
            try:
                updated = api().mark_settlement_paid(group_id, settlement_id, reference.strip() or None) #type:ignore
                st.session_state.settlement_records = [updated if item.get("id") == settlement_id else item for item in st.session_state.settlement_records]
                st.success("Settlement marked as paid.")
                st.rerun()
            except ApiError as error:
                show_error(error)

    payment = st.session_state.get("payments", {}).get(settlement_id)
    if payment:
        st.info(f"Payment status: {payment.get('status', 'initiated')}. Receiver UPI: {payment.get('receiver_upi_id') or 'not available'}")
        with st.form(f"confirm_payment_{settlement_id}"):
            payment_reference = st.text_input("UPI transaction reference", key=f"payment_ref_{settlement_id}")
            if st.form_submit_button("Confirm UPI payment", width="stretch"):
                if not payment_reference.strip():
                    st.error("Add the transaction reference first.")
                else:
                    try:
                        result = api().confirm_payment(payment["payment_id"], payment_reference.strip())
                        refreshed = api().get_settlement_record(group_id, settlement_id) #type:ignore
                        st.session_state.settlement_records = [refreshed if item.get("id") == settlement_id else item for item in st.session_state.settlement_records]
                        st.success(result.get("message", "Payment confirmed."))
                        st.session_state.loaded_group = None
                        st.rerun()
                    except ApiError as error:
                        show_error(error)


def add_expense_form(group: dict, group_id: str, user_id: str) -> None:
    members = group.get("members", [])
    member_ids = [member["user_id"] for member in members]
    member_names = {member["user_id"]: member["name"] for member in members}
    with st.form("add_expense"):
        title = st.text_input("What was it for?", placeholder="Dinner at the lake house")
        amount = st.number_input("Total amount", min_value=0.01, step=1.0, format="%.2f")
        description = st.text_input("Note", placeholder="Optional context")
        payer = st.selectbox("Paid by", member_ids, format_func=lambda member: member_names[member], index=member_ids.index(user_id) if user_id in member_ids else 0)
        participants = st.multiselect("Split between", member_ids, default=member_ids, format_func=lambda member: member_names[member])
        split_type = st.radio("Split", ["equal", "custom"], horizontal=True, format_func=lambda value: "Equal split" if value == "equal" else "Custom shares")
        custom_shares = None
        if split_type == "custom":
            st.caption("Shares must add up to the total amount.")
            custom_shares = [{"user_id": member_id, "share_amount": st.number_input(member_names[member_id], min_value=0.0, step=1.0, format="%.2f", key=f"share_{member_id}")} for member_id in participants]
        if st.form_submit_button("Add expense", width="stretch"):
            if not title.strip() or not participants:
                st.error("Add a title and at least one participant.")
                return
            payload = {"title": title.strip(), "description": description.strip() or None, "amount": f"{amount:.2f}", "paid_by": payer, "split_type": split_type, "participant_user_ids": participants, "custom_shares": custom_shares}
            try:
                api().create_expense(group_id, payload)
                st.session_state.loaded_group = None
                st.success("Expense added.")
                st.rerun()
            except ApiError as error:
                show_error(error)


def bill_scanner() -> None:
    st.write("Upload a clear receipt and let the backend extract the bill details for review.")
    uploaded = st.file_uploader("Receipt image", type=["jpg", "jpeg", "png", "webp"])
    if uploaded and st.button("Scan receipt", type="primary"):
        with st.spinner("Reading the receipt..."):
            try:
                result = api().scan_bill(uploaded)
                st.session_state.scan_result = result.get("result", {})
            except ApiError as error:
                show_error(error)
    result = st.session_state.get("scan_result")
    if result:
        st.success("Receipt read. Verify the details before adding an expense.")
        cols = st.columns(4)
        values = [("Merchant", result.get("merchant_name") or "Unknown"), ("Date", result.get("bill_date") or "Unknown"), ("Total", money(result.get("total"))), ("Confidence", f"{float(result.get('confidence', 0)):.0%}")]
        for column, (label, value) in zip(cols, values):
            column.metric(label, value)
        for warning in result.get("warnings", []):
            st.warning(warning)
        if result.get("items"):
            st.dataframe(pd.DataFrame(result["items"]), width="stretch", hide_index=True)


def main() -> None:
    with st.sidebar:
        st.text_input("Backend URL", value="http://127.0.0.1:8000/api/v1", key="api_url")
        try:
            backend_status = api().backend_health()
            api_status = api().api_health()
            st.success(f"Backend online · {backend_status.get('version', 'ok')} · API {api_status.get('api_version', 'v1')}")
        except ApiError:
            st.error("Backend offline")
    if not st.session_state.get("authenticated"):
        auth_screen()
        return
    try:
        st.session_state.user = api().me()
        groups = api().groups()
    except ApiError as error:
        show_error(error)
        return
    if not groups:
        st.title("Start your first group")
        with st.form("new_group"):
            name = st.text_input("Group name", placeholder="Goa weekend")
            description = st.text_input("Description")
            if st.form_submit_button("Create group"):
                try:
                    api().create_group(name.strip(), description.strip())
                    st.rerun()
                except ApiError as error:
                    show_error(error)
        return
    group_id = sidebar(groups)
    group = next(group for group in groups if group["id"] == group_id)
    dashboard(group, group_id)


if __name__ == "__main__":
    main()