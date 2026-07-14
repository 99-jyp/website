import json

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Min
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Employee, Notification


# ──────────────────────────────────────────────
# Navigation helpers
# ──────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


# ──────────────────────────────────────────────
# Dashboard  (v4.0 + v5.0 stats / anomalies)
# ──────────────────────────────────────────────

@login_required
def dashboard_page(request):
    employees = Employee.objects.all()
    total = employees.count()
    agg = employees.aggregate(avg=Avg("leave_days"))
    avg_leave = round(float(agg["avg"] or 0), 1)
    low_leave = employees.filter(leave_days__lt=5).count()

    # v5.0 – auto anomaly notifications
    for emp in employees.filter(leave_days__lt=5):
        msg = f"⚠️ {emp.name}({emp.department}) 연차 {emp.leave_days}일 부족"
        if not Notification.objects.filter(message=msg, is_read=False).exists():
            Notification.objects.create(message=msg, level=Notification.LEVEL_WARNING)

    unread_count = Notification.objects.filter(is_read=False).count()
    recent_notifications = Notification.objects.all()[:8]

    context = {
        "employees": employees.order_by("employee_no"),
        "total": total,
        "avg_leave": avg_leave,
        "low_leave": low_leave,
        "unread_count": unread_count,
        "recent_notifications": recent_notifications,
    }
    return render(request, "core/dashboard.html", context)


# ──────────────────────────────────────────────
# AI Chat  (v4.0)
# ──────────────────────────────────────────────

@login_required
def chat_page(request):
    history = request.session.get("chat_history", [])
    unread_count = Notification.objects.filter(is_read=False).count()
    return render(request, "core/chat.html", {
        "history": history,
        "unread_count": unread_count,
    })


def _get_ai_session_id(request):
    """
    AI agent(ai.memory)의 session_id는 request.session과는 별개 개념이다.
    사용자별로 last_employee / 대화 문맥을 분리하기 위한 키이며,
    로그인 사용자이므로 user.id를 기준으로 고정한다.
    (브라우저를 바꿔도 같은 계정이면 같은 문맥을 이어받는다)
    """
    return f"user:{request.user.id}"


@login_required
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

    message = (data.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "메시지가 비어 있습니다."}, status=400)

    session_id = _get_ai_session_id(request)

    try:
        from ai.agent import ask_ai
        answer = ask_ai(message, session_id)
    except Exception as exc:
        answer = f"AI 연결 오류: {str(exc)[:200]}"

    history = request.session.get("chat_history", [])
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})
    request.session["chat_history"] = history[-30:]
    request.session.modified = True

    _notify_from_response(answer)
    return JsonResponse({"answer": answer})


@login_required
@require_POST
def clear_chat(request):
    request.session["chat_history"] = []
    request.session.modified = True

    # 화면상의 대화창만 지우고 AI의 last_employee 등 문맥은 남아있으면
    # "지웠는데 왜 아직 그 사람 얘기를 기억하지?" 하는 혼란이 생길 수 있음.
    # 대화 초기화 시 AI 메모리도 함께 리셋한다.
    from ai.memory import memory_store
    memory_store.drop(_get_ai_session_id(request))

    return JsonResponse({"success": True})


# ──────────────────────────────────────────────
# v5.0 – Stats API  (Chart.js source)
# ──────────────────────────────────────────────

@login_required
@require_GET
def stats_api(request):
    departments = list(
        Employee.objects.values("department")
        .annotate(count=Count("id"), avg_leave=Avg("leave_days"))
        .order_by("-count")
    )

    agg = Employee.objects.aggregate(
        total=Count("id"),
        avg=Avg("leave_days"),
        min_leave=Min("leave_days"),
        max_leave=Max("leave_days"),
    )

    anomalies = list(
        Employee.objects.filter(leave_days__lt=5)
        .values("name", "department", "leave_days")
        .order_by("leave_days")
    )

    for d in departments:
        if d["avg_leave"] is not None:
            d["avg_leave"] = round(float(d["avg_leave"]), 1)

    return JsonResponse({
        "total": agg["total"] or 0,
        "avg_leave": round(float(agg["avg"] or 0), 1),
        "min_leave": agg["min_leave"] or 0,
        "max_leave": agg["max_leave"] or 0,
        "departments": departments,
        "anomalies": anomalies,
        "dept_count": len(departments),
    })


# ──────────────────────────────────────────────
# v5.0 – Notifications API
# ──────────────────────────────────────────────

@login_required
@require_GET
def notifications_api(request):
    items = list(
        Notification.objects.all()[:25]
        .values("id", "message", "level", "created_at", "is_read")
    )
    for item in items:
        if item["created_at"]:
            item["created_at"] = item["created_at"].strftime("%m/%d %H:%M")

    unread = Notification.objects.filter(is_read=False).count()
    return JsonResponse({"notifications": items, "unread": unread})


@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    return JsonResponse({"success": True})


# ──────────────────────────────────────────────
# v5.0 – Automated Report
# ──────────────────────────────────────────────

@login_required
@require_POST
def generate_report(request):
    try:
        from tools.automation import generate_leave_status_report
        result = generate_leave_status_report()
        if result.get("success"):
            Notification.objects.create(
                message=f"📊 휴가 현황 리포트 생성 완료 – {result['count']}명",
                level=Notification.LEVEL_SUCCESS,
            )
        return JsonResponse(result)
    except Exception as exc:
        return JsonResponse({"success": False, "message": str(exc)})


# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

_NOTIFICATION_PATTERNS = [
    ("등록했습니다", Notification.LEVEL_SUCCESS, "직원이 등록되었습니다."),
    ("삭제했습니다", Notification.LEVEL_WARNING, "직원이 삭제되었습니다."),
    ("부서를", Notification.LEVEL_INFO, "직원 부서가 변경되었습니다."),
    ("연차가 변경", Notification.LEVEL_INFO, "직원 연차가 변경되었습니다."),
    ("엑셀 파일을 생성", Notification.LEVEL_SUCCESS, "엑셀 파일이 생성되었습니다."),
    ("PDF를 생성", Notification.LEVEL_SUCCESS, "PDF가 생성되었습니다."),
    ("리포트를 생성", Notification.LEVEL_SUCCESS, "리포트가 생성되었습니다."),
    ("메일을 발송", Notification.LEVEL_INFO, "공지 메일이 발송되었습니다."),
    ("스케줄러를 시작", Notification.LEVEL_INFO, "자동 리포트 스케줄러가 시작되었습니다."),
]


def _notify_from_response(response_text):
    for keyword, level, message in _NOTIFICATION_PATTERNS:
        if keyword in response_text:
            Notification.objects.create(message=message, level=level)
            break
