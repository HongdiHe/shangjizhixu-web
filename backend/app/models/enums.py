"""Enums for the application."""
import enum


class UserRole(str, enum.Enum):
    """User roles in the system."""

    ADMIN = "admin"
    QUESTION_SUBMITTER = "question_submitter"  # 题目录入员
    OCR_EDITOR = "ocr_editor"
    OCR_REVIEWER = "ocr_reviewer"
    REWRITE_EDITOR = "rewrite_editor"
    REWRITE_REVIEWER = "rewrite_reviewer"


class QuestionStatus(str, enum.Enum):
    """Question processing status."""

    NEW = "NEW"
    OCR_EDITING = "OCR_编辑中"
    OCR_REVIEWING = "OCR_待审"
    OCR_APPROVED = "OCR_通过"
    REWRITE_GENERATING = "改写_生成中"
    REWRITE_EDITING = "改写_编辑中"
    REWRITE_REVIEWING = "改写_复审中"
    DONE = "DONE"
    ARCHIVED = "废弃"


class ReviewStatus(str, enum.Enum):
    """Review status for questions."""

    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"


class Subject(str, enum.Enum):
    """Academic subjects."""

    MATH = "数学"
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    BIOLOGY = "生物"
    CHINESE = "语文"
    ENGLISH = "英语"
    HISTORY = "历史"
    GEOGRAPHY = "地理"
    POLITICS = "政治"


class Grade(str, enum.Enum):
    """Grade levels."""

    ELEMENTARY = "小学"
    MIDDLE_SCHOOL = "初中"
    HIGH_SCHOOL = "高中"


class QuestionType(str, enum.Enum):
    """Question types."""

    MULTIPLE_CHOICE = "选择题"
    TRUE_FALSE = "判断题"
    FILL_BLANK = "填空题"
    SHORT_ANSWER = "简答题"
    ESSAY = "论述题"
    CALCULATION = "计算题"
    PROOF = "证明题"


class QuestionSource(str, enum.Enum):
    """Question sources."""

    HLE = "HLE"
    TEXTBOOK = "教材"
    EXAM = "考试"
    PRACTICE = "练习"
    CUSTOM = "自定义"
