"""
Data models for code analysis functionality.
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class CodeLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    SHELL = "shell"
    YAML = "yaml"
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"


class SeverityLevel(str, Enum):
    """Severity levels for code issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CodeIssue(BaseModel):
    """Individual code issue or suggestion."""
    id: str
    line: int
    column: Optional[int] = None
    severity: SeverityLevel
    message: str
    rule: Optional[str] = None
    category: Optional[str] = None
    suggestion: Optional[str] = None
    fix: Optional[str] = None


class FunctionInfo(BaseModel):
    """Information about a function."""
    name: str
    line: int
    column: Optional[int] = None
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    complexity: Optional[int] = None
    docstring: Optional[str] = None


class ClassInfo(BaseModel):
    """Information about a class."""
    name: str
    line: int
    column: Optional[int] = None
    methods: List[str] = Field(default_factory=list)
    properties: List[str] = Field(default_factory=list)
    inheritance: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None


class ImportInfo(BaseModel):
    """Information about an import statement."""
    line: int
    module: Optional[str] = None
    names: List[str] = Field(default_factory=list)
    alias: Optional[str] = None
    is_from_import: bool = False


class CodeMetrics(BaseModel):
    """Code quality metrics."""
    lines_of_code: int
    cyclomatic_complexity: Optional[int] = None
    maintainability_index: Optional[float] = None
    technical_debt_ratio: Optional[float] = None
    test_coverage: Optional[float] = None
    duplication_percentage: Optional[float] = None


class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(..., min_length=1)
    language: CodeLanguage
    file_path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    analysis_types: List[str] = Field(default_factory=lambda: ["syntax", "style", "complexity", "suggestions"])


class CodeAnalysisResponse(BaseModel):
    """Response from code analysis."""
    id: str
    language: CodeLanguage
    file_path: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    
    # Analysis results
    syntax_errors: List[CodeIssue] = Field(default_factory=list)
    style_issues: List[CodeIssue] = Field(default_factory=list)
    complexity_issues: List[CodeIssue] = Field(default_factory=list)
    suggestions: List[CodeIssue] = Field(default_factory=list)
    
    # Code structure
    functions: List[FunctionInfo] = Field(default_factory=list)
    classes: List[ClassInfo] = Field(default_factory=list)
    imports: List[ImportInfo] = Field(default_factory=list)
    
    # Metrics
    metrics: Optional[CodeMetrics] = None
    
    # AI-generated insights
    summary: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    
    # Processing metadata
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None


class CodeCompletionRequest(BaseModel):
    """Request for code completion."""
    prefix: str
    suffix: str = ""
    language: CodeLanguage
    file_path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    max_completions: int = Field(default=5, ge=1, le=20)


class CodeCompletion(BaseModel):
    """Individual code completion suggestion."""
    id: str
    text: str
    display_text: Optional[str] = None
    description: Optional[str] = None
    kind: Optional[str] = None  # function, variable, class, etc.
    score: float = Field(ge=0.0, le=1.0)
    insert_text: Optional[str] = None
    documentation: Optional[str] = None


class CodeCompletionResponse(BaseModel):
    """Response from code completion."""
    id: str
    completions: List[CodeCompletion] = Field(default_factory=list)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None


class RefactorRequest(BaseModel):
    """Request for code refactoring."""
    code: str = Field(..., min_length=1)
    language: CodeLanguage
    refactor_type: str  # extract_method, rename, inline, etc.
    target_location: Optional[Dict[str, int]] = None  # line, column
    parameters: Optional[Dict[str, Any]] = None


class RefactorResponse(BaseModel):
    """Response from code refactoring."""
    id: str
    original_code: str
    refactored_code: str
    changes: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    processing_time_ms: Optional[int] = None

