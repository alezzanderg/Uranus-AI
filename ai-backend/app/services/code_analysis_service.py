"""
Code analysis service for static analysis and AI-powered insights.
"""
import ast
import re
import time
import uuid
from typing import Dict, List, Optional, Any
from loguru import logger
from openai import AsyncOpenAI

from ..config import settings
from ..models.code_models import (
    CodeAnalysisRequest, CodeAnalysisResponse, CodeLanguage,
    CodeIssue, FunctionInfo, ClassInfo, ImportInfo, CodeMetrics,
    SeverityLevel
)


class CodeAnalysisService:
    """Service for analyzing code and providing insights."""
    
    def __init__(self):
        """Initialize the code analysis service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.analyzers = {
            CodeLanguage.PYTHON: self._analyze_python_code,
            CodeLanguage.JAVASCRIPT: self._analyze_javascript_code,
            CodeLanguage.TYPESCRIPT: self._analyze_typescript_code,
        }
    
    async def analyze_code(self, request: CodeAnalysisRequest) -> CodeAnalysisResponse:
        """Analyze code and return comprehensive analysis."""
        try:
            start_time = time.time()
            
            response = CodeAnalysisResponse(
                id=str(uuid.uuid4()),
                language=request.language,
                file_path=request.file_path
            )
            
            # Perform static analysis
            if request.language in self.analyzers:
                static_analysis = self.analyzers[request.language](request.code)
                
                response.syntax_errors = static_analysis.get('syntax_errors', [])
                response.style_issues = static_analysis.get('style_issues', [])
                response.complexity_issues = static_analysis.get('complexity_issues', [])
                response.functions = static_analysis.get('functions', [])
                response.classes = static_analysis.get('classes', [])
                response.imports = static_analysis.get('imports', [])
                response.metrics = static_analysis.get('metrics')
            
            # Generate AI-powered insights
            if "suggestions" in request.analysis_types:
                ai_insights = await self._generate_ai_insights(request.code, request.language)
                response.suggestions = ai_insights.get('suggestions', [])
                response.summary = ai_insights.get('summary')
                response.recommendations = ai_insights.get('recommendations', [])
            
            processing_time = int((time.time() - start_time) * 1000)
            response.processing_time_ms = processing_time
            response.model_used = settings.openai_model
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            raise
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(code)
            
            analysis = {
                'functions': [],
                'classes': [],
                'imports': [],
                'syntax_errors': [],
                'style_issues': [],
                'complexity_issues': [],
                'metrics': None
            }
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_python_function(node, code)
                    analysis['functions'].append(func_info)
                    
                    # Check for complexity issues
                    if func_info.complexity and func_info.complexity > 10:
                        analysis['complexity_issues'].append(CodeIssue(
                            id=str(uuid.uuid4()),
                            line=node.lineno,
                            severity=SeverityLevel.WARNING,
                            message=f"Function '{func_info.name}' has high cyclomatic complexity ({func_info.complexity})",
                            category="complexity",
                            suggestion="Consider breaking this function into smaller functions"
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_python_class(node)
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._analyze_python_import(node)
                    analysis['imports'].append(import_info)
            
            # Calculate metrics
            lines = code.split('\n')
            analysis['metrics'] = CodeMetrics(
                lines_of_code=len([line for line in lines if line.strip()]),
                cyclomatic_complexity=self._calculate_total_complexity(analysis['functions'])
            )
            
            # Check for style issues
            analysis['style_issues'].extend(self._check_python_style(code, lines))
            
            return analysis
            
        except SyntaxError as e:
            return {
                'syntax_errors': [CodeIssue(
                    id=str(uuid.uuid4()),
                    line=e.lineno or 1,
                    column=e.offset,
                    severity=SeverityLevel.ERROR,
                    message=f"Syntax error: {e.msg}",
                    category="syntax"
                )],
                'functions': [],
                'classes': [],
                'imports': [],
                'style_issues': [],
                'complexity_issues': [],
                'metrics': None
            }
    
    def _analyze_python_function(self, node: ast.FunctionDef, code: str) -> FunctionInfo:
        """Analyze a Python function."""
        parameters = [arg.arg for arg in node.args.args]
        complexity = self._calculate_cyclomatic_complexity(node)
        docstring = ast.get_docstring(node)
        
        return FunctionInfo(
            name=node.name,
            line=node.lineno,
            parameters=parameters,
            complexity=complexity,
            docstring=docstring
        )
    
    def _analyze_python_class(self, node: ast.ClassDef) -> ClassInfo:
        """Analyze a Python class."""
        methods = []
        properties = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        properties.append(target.id)
        
        inheritance = [base.id for base in node.bases if isinstance(base, ast.Name)]
        docstring = ast.get_docstring(node)
        
        return ClassInfo(
            name=node.name,
            line=node.lineno,
            methods=methods,
            properties=properties,
            inheritance=inheritance,
            docstring=docstring
        )
    
    def _analyze_python_import(self, node) -> ImportInfo:
        """Analyze a Python import statement."""
        if isinstance(node, ast.Import):
            return ImportInfo(
                line=node.lineno,
                names=[alias.name for alias in node.names],
                is_from_import=False
            )
        elif isinstance(node, ast.ImportFrom):
            return ImportInfo(
                line=node.lineno,
                module=node.module,
                names=[alias.name for alias in node.names],
                is_from_import=True
            )
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_total_complexity(self, functions: List[FunctionInfo]) -> int:
        """Calculate total cyclomatic complexity."""
        return sum(func.complexity or 0 for func in functions)
    
    def _check_python_style(self, code: str, lines: List[str]) -> List[CodeIssue]:
        """Check Python code style issues."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:  # PEP 8 recommends 79, but 88 is more practical
                issues.append(CodeIssue(
                    id=str(uuid.uuid4()),
                    line=i,
                    severity=SeverityLevel.INFO,
                    message=f"Line too long ({len(line)} characters)",
                    category="style",
                    rule="line-length"
                ))
            
            # Check for trailing whitespace
            if line.rstrip() != line:
                issues.append(CodeIssue(
                    id=str(uuid.uuid4()),
                    line=i,
                    severity=SeverityLevel.INFO,
                    message="Trailing whitespace",
                    category="style",
                    rule="trailing-whitespace"
                ))
        
        return issues
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript code (basic implementation)."""
        # This is a simplified implementation
        # In a real scenario, you'd use a proper JavaScript parser
        lines = code.split('\n')
        
        functions = []
        function_pattern = r'function\s+(\w+)\s*\('
        
        for i, line in enumerate(lines, 1):
            match = re.search(function_pattern, line)
            if match:
                functions.append(FunctionInfo(
                    name=match.group(1),
                    line=i
                ))
        
        return {
            'functions': functions,
            'classes': [],
            'imports': [],
            'syntax_errors': [],
            'style_issues': [],
            'complexity_issues': [],
            'metrics': CodeMetrics(lines_of_code=len([line for line in lines if line.strip()]))
        }
    
    def _analyze_typescript_code(self, code: str) -> Dict[str, Any]:
        """Analyze TypeScript code (basic implementation)."""
        # Similar to JavaScript but with type annotations
        return self._analyze_javascript_code(code)
    
    async def _generate_ai_insights(self, code: str, language: CodeLanguage) -> Dict[str, Any]:
        """Generate AI-powered insights for code."""
        try:
            prompt = f"""
            Analyze this {language.value} code and provide specific improvement suggestions:
            
            ```{language.value}
            {code}
            ```
            
            Please provide:
            1. A brief summary of what the code does
            2. 3-5 specific improvement suggestions
            3. Any potential bugs or issues you notice
            
            Format your response as JSON with keys: summary, recommendations, issues
            """
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a code analysis expert. Provide constructive feedback on code quality, performance, and best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                import json
                parsed_response = json.loads(ai_response)
                
                suggestions = []
                if 'issues' in parsed_response:
                    for issue in parsed_response['issues']:
                        suggestions.append(CodeIssue(
                            id=str(uuid.uuid4()),
                            line=1,  # AI doesn't provide specific line numbers
                            severity=SeverityLevel.INFO,
                            message=issue,
                            category="ai-suggestion"
                        ))
                
                return {
                    'summary': parsed_response.get('summary', ''),
                    'recommendations': parsed_response.get('recommendations', []),
                    'suggestions': suggestions
                }
                
            except json.JSONDecodeError:
                # Fallback to plain text parsing
                return {
                    'summary': ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                    'recommendations': [ai_response],
                    'suggestions': []
                }
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return {
                'summary': '',
                'recommendations': [],
                'suggestions': []
            }


# Global code analysis service instance
code_analysis_service = CodeAnalysisService()


def get_code_analysis_service() -> CodeAnalysisService:
    """Get the code analysis service instance."""
    return code_analysis_service

