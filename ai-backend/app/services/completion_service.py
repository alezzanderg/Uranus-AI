"""
Code completion service for intelligent code suggestions.
"""
import time
import uuid
from typing import List, Optional, Dict, Any
from loguru import logger
from openai import AsyncOpenAI

from ..config import settings
from ..models.code_models import (
    CodeCompletionRequest, CodeCompletionResponse, CodeCompletion,
    CodeLanguage
)


class CompletionService:
    """Service for providing intelligent code completions."""
    
    def __init__(self):
        """Initialize the completion service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.language_contexts = {
            CodeLanguage.PYTHON: self._get_python_context,
            CodeLanguage.JAVASCRIPT: self._get_javascript_context,
            CodeLanguage.TYPESCRIPT: self._get_typescript_context,
        }
    
    async def get_completions(self, request: CodeCompletionRequest) -> CodeCompletionResponse:
        """Get code completions for the given context."""
        try:
            start_time = time.time()
            
            # Build context for the completion
            context = self._build_completion_context(request)
            
            # Generate completions using AI
            completions = await self._generate_ai_completions(request, context)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return CodeCompletionResponse(
                id=str(uuid.uuid4()),
                completions=completions,
                processing_time_ms=processing_time,
                model_used=settings.openai_model
            )
            
        except Exception as e:
            logger.error(f"Error generating completions: {str(e)}")
            raise
    
    def _build_completion_context(self, request: CodeCompletionRequest) -> str:
        """Build context string for completion."""
        context_parts = []
        
        # Add language-specific context
        if request.language in self.language_contexts:
            lang_context = self.language_contexts[request.language](request)
            if lang_context:
                context_parts.append(lang_context)
        
        # Add file context if available
        if request.file_path:
            context_parts.append(f"File: {request.file_path}")
        
        # Add project context if available
        if request.context:
            project_info = request.context.get('project_info', {})
            if project_info.get('type'):
                context_parts.append(f"Project type: {project_info['type']}")
            
            if project_info.get('dependencies'):
                deps = ', '.join(project_info['dependencies'][:5])  # Limit to first 5
                context_parts.append(f"Dependencies: {deps}")
        
        return '\n'.join(context_parts)
    
    async def _generate_ai_completions(
        self, 
        request: CodeCompletionRequest, 
        context: str
    ) -> List[CodeCompletion]:
        """Generate completions using AI."""
        try:
            # Prepare the code context
            code_before = request.prefix
            code_after = request.suffix
            
            prompt = f"""
            Complete the following {request.language.value} code. Provide {request.max_completions} different completion options.
            
            Context:
            {context}
            
            Code before cursor:
            ```{request.language.value}
            {code_before}
            ```
            
            Code after cursor:
            ```{request.language.value}
            {code_after}
            ```
            
            Provide completions that:
            1. Are syntactically correct
            2. Follow best practices for {request.language.value}
            3. Are contextually appropriate
            4. Vary in complexity and approach
            
            Format each completion as:
            COMPLETION_START
            [completion text]
            COMPLETION_END
            DESCRIPTION: [brief description]
            KIND: [function|variable|class|method|keyword|snippet]
            """
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are an expert {request.language.value} developer providing code completions."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_completions(ai_response)
            
        except Exception as e:
            logger.error(f"Error generating AI completions: {str(e)}")
            return []
    
    def _parse_completions(self, ai_response: str) -> List[CodeCompletion]:
        """Parse AI response into completion objects."""
        completions = []
        
        # Split response into completion blocks
        blocks = ai_response.split('COMPLETION_START')
        
        for i, block in enumerate(blocks[1:], 1):  # Skip first empty block
            try:
                # Extract completion text
                if 'COMPLETION_END' in block:
                    completion_text = block.split('COMPLETION_END')[0].strip()
                    metadata_part = block.split('COMPLETION_END')[1] if 'COMPLETION_END' in block else ""
                    
                    # Extract metadata
                    description = ""
                    kind = "snippet"
                    
                    if 'DESCRIPTION:' in metadata_part:
                        desc_line = [line for line in metadata_part.split('\n') if 'DESCRIPTION:' in line]
                        if desc_line:
                            description = desc_line[0].replace('DESCRIPTION:', '').strip()
                    
                    if 'KIND:' in metadata_part:
                        kind_line = [line for line in metadata_part.split('\n') if 'KIND:' in line]
                        if kind_line:
                            kind = kind_line[0].replace('KIND:', '').strip()
                    
                    # Calculate score based on position and length
                    score = max(0.1, 1.0 - (i - 1) * 0.15)
                    
                    completion = CodeCompletion(
                        id=str(uuid.uuid4()),
                        text=completion_text,
                        display_text=completion_text[:50] + "..." if len(completion_text) > 50 else completion_text,
                        description=description,
                        kind=kind,
                        score=score,
                        insert_text=completion_text
                    )
                    
                    completions.append(completion)
                    
            except Exception as e:
                logger.warning(f"Error parsing completion block: {str(e)}")
                continue
        
        # If no completions were parsed, create a simple fallback
        if not completions:
            completions.append(CodeCompletion(
                id=str(uuid.uuid4()),
                text="# AI completion unavailable",
                display_text="AI completion unavailable",
                description="Unable to generate completion",
                kind="comment",
                score=0.1,
                insert_text="# AI completion unavailable"
            ))
        
        return completions[:10]  # Limit to 10 completions
    
    def _get_python_context(self, request: CodeCompletionRequest) -> str:
        """Get Python-specific context for completion."""
        context_parts = []
        
        # Analyze the prefix for imports and class/function definitions
        lines = request.prefix.split('\n')
        
        imports = []
        current_class = None
        current_function = None
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
            elif stripped.startswith('class '):
                current_class = stripped.split('class ')[1].split('(')[0].split(':')[0].strip()
            elif stripped.startswith('def '):
                current_function = stripped.split('def ')[1].split('(')[0].strip()
        
        if imports:
            context_parts.append(f"Available imports: {', '.join(imports[:5])}")
        
        if current_class:
            context_parts.append(f"Current class: {current_class}")
        
        if current_function:
            context_parts.append(f"Current function: {current_function}")
        
        return '\n'.join(context_parts)
    
    def _get_javascript_context(self, request: CodeCompletionRequest) -> str:
        """Get JavaScript-specific context for completion."""
        context_parts = []
        
        # Look for common JavaScript patterns
        if 'function' in request.prefix:
            context_parts.append("JavaScript function context")
        
        if 'class' in request.prefix:
            context_parts.append("JavaScript class context")
        
        if 'import' in request.prefix or 'require' in request.prefix:
            context_parts.append("Module import context")
        
        return '\n'.join(context_parts)
    
    def _get_typescript_context(self, request: CodeCompletionRequest) -> str:
        """Get TypeScript-specific context for completion."""
        context_parts = []
        
        # TypeScript-specific patterns
        if 'interface' in request.prefix:
            context_parts.append("TypeScript interface context")
        
        if 'type' in request.prefix:
            context_parts.append("TypeScript type definition context")
        
        # Include JavaScript context as well
        js_context = self._get_javascript_context(request)
        if js_context:
            context_parts.append(js_context)
        
        return '\n'.join(context_parts)


# Global completion service instance
completion_service = CompletionService()


def get_completion_service() -> CompletionService:
    """Get the completion service instance."""
    return completion_service

