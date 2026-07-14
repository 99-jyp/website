import time
import threading
from contextvars import ContextVar


class AgentMemory:

    def __init__(self):

        self.last_employee = None
        self.last_department = None
        self.last_tool = None
        self.recent_employees = []

        self.conversation = []

        # 세션별로 언제 마지막에 사용됐는지 기록 (MemoryStore의 만료 정리용)
        self.last_accessed = time.time()

    def set_employee(self, name):

        self.last_employee = name

        if name is None:
            return

        # Keep unique recent employee history (newest first).
        self.recent_employees = [
            employee_name
            for employee_name in self.recent_employees
            if employee_name != name
        ]
        self.recent_employees.insert(0, name)
        self.recent_employees = self.recent_employees[:3]

    def get_employee(self):

        return self.last_employee

    def get_recent_employees(self):

        return self.recent_employees

    def set_department(self, department):

        self.last_department = department

    def get_department(self):

        return self.last_department

    def set_last_tool(self, tool_name):

        self.last_tool = tool_name

    def get_last_tool(self):

        return self.last_tool

    def resolve_employee_reference(self, message):

        if self.last_employee is None:
            return None

        if message is None:
            return None

        reference_keywords = [
            "그 사람",
            "그직원",
            "그 직원",
            "그분",
            "방금",
            "아까",
            "이 사람"
        ]

        # 지시어가 명시적으로 있을 때만 이전 직원을 추정한다.
        # (예: "삭제해줘" 처럼 이름도 지시어도 없는 애매한 명령에서
        #  엉뚱한 직원이 삭제되는 사고를 막기 위함)
        if any(keyword in message for keyword in reference_keywords):
            return self.last_employee

        return None

    def add_message(self, role, content):

        self.conversation.append({
            "role": role,
            "content": content
        })

        self.conversation = self.conversation[-10:] #최근 10개의 대화만 기억해라 라는 뜻

    def get_conversation(self):

        return self.conversation

    def get_recent_messages(self, limit=4):

        if limit <= 0:
            return []

        return self.conversation[-limit:]

class MemoryStore:
    """
    세션(사용자)별로 독립된 AgentMemory 인스턴스를 관리한다.

    기존에는 memory = AgentMemory() 가 모듈 전역 싱글톤이라
    모든 사용자가 last_employee / 대화 이력을 공유하는 문제가 있었다.
    (A 사용자가 조회한 직원 정보를 B 사용자의 "그 사람" 이 가리켜버리는 등)

    이 클래스는 session_id를 key로 하여 사용자마다 별도의 메모리를
    부여하고, 오래 쓰이지 않은 세션은 정리(cleanup)할 수 있게 한다.
    """

    def __init__(self, ttl_seconds=3600):
        self._store = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def get(self, session_id):
        """session_id에 해당하는 메모리를 가져오거나, 없으면 새로 만든다."""

        if not session_id:
            raise ValueError("session_id는 비어 있을 수 없습니다.")

        with self._lock:
            entry = self._store.get(session_id)

            if entry is None:
                entry = AgentMemory()
                self._store[session_id] = entry

            entry.last_accessed = time.time()
            return entry

    def drop(self, session_id):
        """특정 세션의 메모리를 명시적으로 삭제한다 (예: 로그아웃 시)."""

        with self._lock:
            self._store.pop(session_id, None)

    def cleanup_expired(self):
        """TTL이 지난 세션 메모리를 정리한다. 스케줄러나 요청 진입 시 주기적으로 호출."""

        cutoff = time.time() - self._ttl

        with self._lock:
            expired = [
                session_id
                for session_id, entry in self._store.items()
                if entry.last_accessed < cutoff
            ]
            for session_id in expired:
                del self._store[session_id]

    def active_session_count(self):
        with self._lock:
            return len(self._store)


# 앱 전역에서 공유하는 스토어. memory 인스턴스 자체가 아니라
# "세션별 memory를 꺼내는 창구"이기 때문에 전역으로 둬도 안전하다.
memory_store = MemoryStore()


# tools/* 가 기대하는 전역 memory 인터페이스를 유지하되,
# 실제 대상은 요청 단위(session_id)로 바인딩된 메모리를 사용한다.
_active_memory_var = ContextVar("active_agent_memory", default=None)
_fallback_memory = AgentMemory()


def set_active_memory(memory):
    """현재 실행 컨텍스트에서 사용할 AgentMemory를 바인딩한다."""

    return _active_memory_var.set(memory)


def reset_active_memory(token):
    """set_active_memory로 바인딩한 메모리를 원복한다."""

    _active_memory_var.reset(token)


def _current_memory():
    memory = _active_memory_var.get()
    if memory is None:
        return _fallback_memory
    return memory


class MemoryProxy:

    def set_employee(self, name):
        return _current_memory().set_employee(name)

    def get_employee(self):
        return _current_memory().get_employee()

    def get_recent_employees(self):
        return _current_memory().get_recent_employees()

    def set_department(self, department):
        return _current_memory().set_department(department)

    def get_department(self):
        return _current_memory().get_department()

    def set_last_tool(self, tool_name):
        return _current_memory().set_last_tool(tool_name)

    def get_last_tool(self):
        return _current_memory().get_last_tool()

    def resolve_employee_reference(self, message):
        return _current_memory().resolve_employee_reference(message)

    def add_message(self, role, content):
        return _current_memory().add_message(role, content)

    def get_conversation(self):
        return _current_memory().get_conversation()

    def get_recent_messages(self, limit=4):
        return _current_memory().get_recent_messages(limit)


# 하위호환: 기존 코드의 `from ai.memory import memory`를 계속 지원한다.
memory = MemoryProxy()
