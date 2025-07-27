"""
API routes for code analysis and completion functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from ..models.code_models import (
    CodeAnalysisRequest, CodeAnalysisResponse,
    CodeCompletionRequest, CodeCompletionResponse
)
from ..services.code_analysis_service import CodeAnalysisService, get_code_analysis_service
from ..services.completion_service import CompletionService, get_completion_service


router = APIRouter(prefix="/api/v1/code", tags=["code"])


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    analysis_service: CodeAnalysisService = Depends(get_code_analysis_service)
):
    """Analyze code and return comprehensive analysis."""
    try:
        response = await analysis_service.analyze_code(request)
        return response
    except Exception as e:
        logger.error(f"Error in analyze_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete", response_model=CodeCompletionResponse)
async def complete_code(
    request: CodeCompletionRequest,
    completion_service: CompletionService = Depends(get_completion_service)
):
    """Get code completions for the given context."""
    try:
        response = await completion_service.get_completions(request)
        return response
    except Exception as e:
        logger.error(f"Error in complete_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_code(
    code: str,
    language: str = "python"
):
    """Explain what a piece of code does."""
    try:
        # This would use the chat service to explain code
        from ..services.chat_service import get_chat_service
        from ..models.chat_models import ChatRequest, AiContext
        
        chat_service = get_chat_service()
        
        context = AiContext(
            selection={"text": code},
            editor={"language": language}
        )
        
        request = ChatRequest(
            message=f"Please explain what this {language} code does:\n\n```{language}\n{code}\n```",
            context=context
        )
        
        response = await chat_service.process_chat_message(request)
        return {"explanation": response.response}
        
    except Exception as e:
        logger.error(f"Error in explain_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refactor")
async def refactor_code(
    code: str,
    language: str = "python",
    refactor_type: str = "improve"
):
    """Suggest refactoring for a piece of code."""
    try:
        from ..services.chat_service import get_chat_service
        from ..models.chat_models import ChatRequest, AiContext
        
        chat_service = get_chat_service()
        
        context = AiContext(
            selection={"text": code},
            editor={"language": language}
        )
        
        refactor_prompts = {
            "improve": "Please suggest improvements for this code, focusing on readability, performance, and best practices:",
            "extract_method": "Please suggest how to extract methods from this code to improve modularity:",
            "simplify": "Please suggest ways to simplify this code while maintaining functionality:",
            "optimize": "Please suggest optimizations for this code to improve performance:"
        }
        
        prompt = refactor_prompts.get(refactor_type, refactor_prompts["improve"])
        
        request = ChatRequest(
            message=f"{prompt}\n\n```{language}\n{code}\n```",
            context=context
        )
        
        response = await chat_service.process_chat_message(request)
        return {"refactoring_suggestions": response.response}
        
    except Exception as e:
        logger.error(f"Error in refactor_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-bugs")
async def find_bugs(
    code: str,
    language: str = "python"
):
    """Find potential bugs in code."""
    try:
        from ..services.chat_service import get_chat_service
        from ..models.chat_models import ChatRequest, AiContext
        
        chat_service = get_chat_service()
        
        context = AiContext(
            selection={"text": code},
            editor={"language": language}
        )
        
        request = ChatRequest(
            message=f"Please analyze this {language} code for potential bugs, errors, or issues:\n\n```{language}\n{code}\n```",
            context=context
        )
        
        response = await chat_service.process_chat_message(request)
        return {"bug_analysis": response.response}
        
    except Exception as e:
        logger.error(f"Error in find_bugs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-tests")
async def generate_tests(
    code: str,
    language: str = "python",
    test_framework: str = "pytest"
):
    """Generate unit tests for code."""
    try:
        from ..services.chat_service import get_chat_service
        from ..models.chat_models import ChatRequest, AiContext
        
        chat_service = get_chat_service()
        
        context = AiContext(
            selection={"text": code},
            editor={"language": language}
        )
        
        request = ChatRequest(
            message=f"Please generate {test_framework} unit tests for this {language} code:\n\n```{language}\n{code}\n```",
            context=context
        )
        
        response = await chat_service.process_chat_message(request)
        return {"generated_tests": response.response}
        
    except Exception as e:
        logger.error(f"Error in generate_tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

