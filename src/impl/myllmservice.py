# here is myllmservice.py


# to run python -m impl.myllmservice

import logging

# logger = logging.getLogger(__name__)
import asyncio
from llmservice import BaseLLMService, GenerationRequest, GenerationResult
from typing import Optional, Union
from . import prompts


class MyLLMService(BaseLLMService):
    def __init__(self, logger=None, max_concurrent_requests=200):
        super().__init__(
            logger=logging.getLogger(__name__),
            # default_model_name="gpt-4o-mini",
            default_model_name="gpt-4.1-nano",
            max_rpm=500,
            max_concurrent_requests=max_concurrent_requests,
        )
       
   


   
    
    def generate_ai_answer(self, chat_history: str, user_msg=None, model = None ) -> GenerationResult:
        
        user_prompt = prompts.GENERATE_AI_ANSWER_PROMPT.format(
            chat_history=chat_history,
            user_msg=user_msg
        )
       
        
        if model is None:
            model= "gpt-4o-mini"

        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="generate_ai_answer",
            # pipeline_config=pipeline_config,
            # request_id=request_id,
        )

        result = self.execute_generation(generation_request)
        return result
    
    def generate_affirmations_with_llm(self, 
                                       context: str,
                                       category: Optional[str] = None, 
                                       count: int = 5,
                                       style: Optional[str] = None,
                                       uslub: Optional[str] = None,
                                       model: Optional[str] = None) -> GenerationResult:
        
        """
        Generate positive affirmations based on user context using LLM.
        
        Args:
            context: The user's context/situation for generating relevant affirmations
            category: Optional category for the affirmations
            count: Number of affirmations to generate (default: 5)
            style: The style of affirmations (e.g., 'motivational', 'gentle', etc.)
            uslub: The tone/approach (e.g., 'powerful', 'nurturing', etc.)
            model: LLM model to use (default: gpt-4o-mini)
            
        Returns:
            GenerationResult containing the generated affirmations
        """
        # Handle empty context
        if context and context.strip():
            context_line = f' based on the following context:\n\nContext: {context}'
            context_requirement = 'Make them specific to the given context'
        else:
            context_line = ''
            context_requirement = 'Make them general and universally applicable'
            
        category_line = f'Category: {category}' if category else ''
        style_line = f'Style: {style}' if style else ''
        uslub_line = f'Tone: {uslub}' if uslub else ''
        
        user_prompt = prompts.GENERATE_AFFIRMATIONS_PROMPT.format(
            count=count,
            context_line=context_line,
            context_requirement=context_requirement,
            category_line=category_line,
            style_line=style_line,
            uslub_line=uslub_line
        )

        if model is None:
            model = "gpt-4o-mini"
        
        pipeline_config = [
            {
                "type": "ConvertToDict",
                "params": {},
            }, 
            {
                'type': 'ExtractValue',
                'params': {'key': 'content'} 
            }
        ]
        
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            output_type="json",
            operation_name="generate_affirmations",
            pipeline_config=pipeline_config
        )
        
        result = self.execute_generation(generation_request)
        return result
    
    def analyze_journal_entry(self, 
                            content: str,
                            mood: str,
                            model: Optional[str] = None) -> GenerationResult:
        """
        Analyze a journal entry to extract insights, tags, and suggestions.
        
        Args:
            content: The journal entry content
            mood: The mood emoji/indicator
            model: LLM model to use (default: gpt-4o-mini)
            
        Returns:
            GenerationResult containing analysis with tags, themes, emotional state, and suggestions
        """
        
        user_prompt = prompts.ANALYZE_JOURNAL_ENTRY_PROMPT.format(
            content=content,
            mood=mood
        )
        
        if model is None:
            model = "gpt-4o-mini"
        
        pipeline_config = [
            {
                "type": "ConvertToDict",
                "params": {},
            }
        ]
        
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
            model=model,
            output_type="json",
            operation_name="analyze_journal_entry",
            pipeline_config=pipeline_config
        )
        
        result = self.execute_generation(generation_request)
        return result
    


   


def main():
    """
    Main function to test the categorize_simple method of MyLLMService.
    """
    # Initialize the service
    my_llm_service = MyLLMService()


    context= "i want to make million dolars"
    category= ""
    count = 5
    # model= None



    try:
      
        generation_result = my_llm_service.generate_affirmations_with_llm(
            context=context,
            category=category,
            count=count
        )

        # Print the result
        # print("Generation Result:", generation_result)
        if generation_result.success:
            print("Content:", generation_result.content)
            print("type Content:", type(generation_result.content))
        else:
            print("Error:", generation_result.error_message)
    except Exception as e:
        print(f"An exception occurred: {e}")


if __name__ == "__main__":
    main()
