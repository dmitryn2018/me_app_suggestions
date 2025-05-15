from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.memory import ConversationBufferMemory
from mem0 import AsyncMemoryClient
from pydantic import BaseModel, Field, ConfigDict
from app.models import Suggestion, ModelType
from app.services.memory import MemoryService

load_dotenv()

class ModelSelection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    model_type: str = Field(..., description="Either 'Image' or 'Text'")
    selected_model: str = Field(..., description="The ID of the selected model")

class SuggestionList(BaseModel):
    model_config = ConfigDict(extra='forbid')
    suggestions: List[Suggestion]

class SuggestionGenerator:
    def __init__(self, openai_api_key: str, mem0_api_key: str, proxy_url: str = None):
        
        # Initialize proxy client if URL is provided
        client = None
        if proxy_url:
            client = httpx.Client(proxy=proxy_url)
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key,
            client=client if client else None,
        )
        self.memory = ConversationBufferMemory()
        self.mem0_client = AsyncMemoryClient(api_key=mem0_api_key)
        self.suggestion_parser = PydanticOutputParser(pydantic_object=SuggestionList)
        self.model_parser = PydanticOutputParser(pydantic_object=ModelSelection)
        self.memory_service = MemoryService()
        
        self.suggestion_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a suggestion generator that creates personalized suggestions based on conversation history and memories, one for each memory by the very least.
            IMPORTANT: You must generate _exactly_ {num_memories} suggestions – no more, no fewer – one corresponding to each memory provided.  
            
            CRITICAL RULES FOR SUGGESTIONS:
            1. For ANY coding-related content (programming, algorithms, Python, etc):
               - You MUST set model_type="code" (lowercase)
               - You MUST use "anthropic/claude-3.7-sonnet" as the selected_model
               - Keywords that indicate coding: python, algorithm, code, function, programming, development, optimization
            
            2. For image-related content (visuals, designs, etc):
               - You MUST set model_type="image" (lowercase)
               - Select an appropriate image model
               - Keywords that indicate images: design, logo, visual, picture, photo, illustration
            
            3. For writing-related content (blog posts, documentation, stories, etc):
               - Set model_type="text" (lowercase)
               - Keywords that indicate writing: blog, post, article, story, document, write
            
            Each suggestion should be concise and actionable. Format as a JSON object with a 'suggestions' field containing a list of objects.
            Each suggestion object MUST have these EXACT fields:
            - 'title': A short, descriptive title
            - 'description': A clear, actionable description
            - 'model_type': Must be one of: 'text', 'code', or 'image' (all lowercase)
            - 'selected_model': Must be one of the available models for the chosen model_type
            
            Example coding suggestion:
            {{
              "title": "Optimize Graph Algorithm",
              "description": "Enhance the depth-first search implementation with additional optimizations",
              "model_type": "code",
              "selected_model": "anthropic/claude-3.7-sonnet"
            }}"""),
            ("user", """Based on these messages and memories, generate relevant suggestions:
            
            Messages:
            {messages}
            
            Memories:
            {memories}
            
            Format each suggestion as:
            {format_instructions}""")
        ])

        self.model_selection_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI model selection assistant. Your task is to analyze suggestions and determine the optimal AI model based on the user's request and available user model preferences.
            For each suggestion, determine:
            1. Determine Model Type: Decide whether the suggestion requires an Image or Text model. This is CRITICAL, especially when the user has pre-selected models, as we need to know whether to use their selected image model or text model.
            2. Select the Best Model: Choose the most suitable model from the provided options or use the user-selected model if indicated in the instructions.
            
            Your response MUST be formatted as a JSON object with:
            - model_type: Either 'Image' or 'Text'
            - selected_model: The ID of the selected model"""),
            ("user", """TASK: Analyze the suggestions and consider the model preferences to achieve the following:

            1. Clearly identify if the prompt requires an Image or Text model.
            2. Select the most appropriate model from the following options, considering both the prompt and [ai_model_preferences]:

            Title: {title}
            Description: {description}
            Type: {type}
             
            
            SUPER IMPORTANT RULE: For image generation requests or text-to-image prompts, ALWAYS set MODEL_TYPE as "Image" and select an appropriate image model.

            SUPER IMPORTANT RULE: If the user requests a specific model (e.g., "use Claude" or "use GPT 4.1"), select that model regardless of any other settings or considerations.

            SUPER IMPORTANT RULE: Always prioritize specific user model preferences if they exist in [ai_model_preferences]. Only fall back to general model recommendations when no specific preference is found for specific task

            ### AVAILABLE TEXT MODELS:
            1. "anthropic/claude-3.7-sonnet" - Best for: coding tasks, complex reasoning, technical discussions, detailed explanations, and math problems. Use for complex programming, algorithm design, or sophisticated problem-solving.
            2. "anthropic/claude-3.5-sonnet" - Best for: balanced capabilities, good for writing tasks and mid-level coding. Use for general-purpose responses that need good reasoning but aren't extremely technical.
            3. "gpt-4.1" - Best for: creative writing, storytelling, generating fiction, marketing copy, persuasive content, complex reasoning, and technical accuracy. Use when creativity, precision, or detailed explanations are needed.
            4. "o3-mini" - Best for: versatile tasks requiring strong reasoning and balanced capabilities. Good for analytical thinking and detailed explanations.
            5. "gpt-4o-mini" - Best for: efficient processing of straightforward tasks with a focus on speed and simplicity. Ideal for quick responses and really-really simple queries.
            6. "gpt-4o" - Best for: quick responses to simple questions, casual conversation, brief explanations. Good for straightforward queries.
            7. "meta-llama/llama-4-maverick" - Best for: complex reasoning tasks, research questions, and detailed knowledge queries. Strong on analytical thinking.
            8. "meta-llama/llama-4-scout" - Best for: lightweight everyday questions and general conversation. Fast and efficient for common queries.
            9. "x-ai/grok-3-beta" - Best for: queries about current events, internet trends, and web knowledge. Has a distinctive, sometimes witty style.
            10. "deepseek/deepseek-r1" - Best for: research-focused content, academic writing, and structured analysis.
            
            ### AVAILABLE IMAGE MODELS:
            11. "openai/gpt-image-1" - Best for: versatile high-quality image generation. Excellent for photorealistic images, creative art, and detailed illustrations.
            12. "recraft-ai/recraft-v3" - Best for: photorealistic images, detailed illustrations, and images with complex elements. Good for high-quality visuals and design-intensive tasks.
            13. "recraft-ai/recraft-v3-svg" - Best for: vector images, logos, icons, and scalable graphics. Ideal for brand assets and UI/UX designs.
            14. "black-forest-labs/flux-1.1-pro-ultra" - Best for: ultra-high-resolution images and rapid generation. Great for professional art, detailed prints, and high-fidelity visuals.
            15. "google/gemini-2.0-flash-exp-image-generation" - Best for: multimodal content combining text and images. Efficient for interactive storytelling, educational visuals, and responsive applications.
             
            ### ADDITIONAL GUIDANCE:
            - For tasks requiring deep reasoning (e.g., "think more," "complex problem"), prioritize models like "anthropic/claude-3.7-sonnet", "gpt-4.1", "meta-llama/llama-4-maverick", or "deepseek/deepseek-r1".
            - For creative tasks (e.g., storytelling, marketing), prioritize "gpt-4.1".
            - For quick, simple queries, prioritize "gpt-4o-mini" or "o3-mini".
            - For current events or trends, prioritize "x-ai/grok-3-beta".
            - For coding tasks: "anthropic/claude-3.7-sonnet".
             
            ### IMAGE VS. TEXT PROMPT IDENTIFICATION GUIDANCE:

            Use the following criteria to determine if a prompt requires an Image or Text model:

            #### Indicators of Image Prompts:
            - Explicit requests for images, pictures, visuals, drawings, illustrations, etc.
            - Mentions of visual styles (photorealistic, cartoon, abstract, etc.)
            - References to visual elements (colors, composition, lighting, etc.)
            - Requests to generate or modify visual content (logos, icons, portraits, etc.)
            - Use of phrases like "show me", "draw", "create an image of", "picture of", "design a"

            #### Indicators of Text Prompts:
            - Requests for information, explanations, or analysis
            - Questions that seek factual answers or opinions
            - Requests to write text content (essays, stories, code, etc.)
            - Tasks involving reasoning, calculation, or problem-solving
            - Use of phrases like "explain", "write", "analyze", "how to", "why is", etc
             
            ### USER AI MODEL PREFERENCES:

            This section contains specific information about which AI models the user prefers for different types of tasks or scenarios. You MUST prioritize these specific preferences if they exist for the current task type.
            [user_ai_model_preferences]|| "No user AI model preferences available."
            """)
        ])

    def _format_messages_for_prompt(self, messages: List[dict]) -> str:
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n\n".join(formatted)

    async def _select_model_for_suggestion(self, suggestion: Suggestion) -> ModelSelection:
        """Select the appropriate model for a given suggestion."""
        try:
            chain = self.model_selection_prompt | self.llm | self.model_parser
            result = await chain.ainvoke({
                "title": suggestion.title,
                "description": suggestion.description,
                "type": suggestion.model_type,
                "format_instructions": self.model_parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"Error selecting model for suggestion: {str(e)}")
            # Default model selection based on type
            if suggestion.model_type.lower() == "code":
                return ModelSelection(
                    model_type="code",  # Preserve CODE type
                    selected_model="anthropic/claude-3.7-sonnet"
                )
            elif suggestion.model_type.lower() == "image":
                return ModelSelection(
                    model_type="Image",
                    selected_model="openai/gpt-image-1"
                )
            else:
                return ModelSelection(
                    model_type="Text",
                    selected_model="gpt-4.1"
                )

    async def generate_from_conversations(
        self,
        conversations: List[Dict[str, str]],
        user_id: str,
        memories: List[Dict[str, str]]
    ) -> List[Suggestion]:
        try:
            print(f"\nUsing provided memories for user {user_id}...")
            print(f"Total memories: {len(memories)}")
            
            for memory in memories:
                print(f"Memory: {memory.get('memory', '')}")

            formatted_messages = self._format_messages_for_prompt(conversations)
            print("\nFormatted messages:")
            for msg in formatted_messages.split("\n"):
                print(msg)

            formatted_memories = self._format_memories(memories)
            print("\nFormatted memories:")
            print(formatted_memories)

            print("\nGenerating suggestions...")
            try:
                # Generate initial suggestions
                num_memories = len(memories)

                chain = self.suggestion_prompt | self.llm | self.suggestion_parser
                result = await chain.ainvoke({
                    "messages": formatted_messages,
                    "memories": formatted_memories,
                    "num_memories": num_memories,
                    "format_instructions": self.suggestion_parser.get_format_instructions(),
                    "user_ai_model_preferences": "No user AI model preferences available."
                })
                suggestions = result.suggestions
                print(f"Generated {len(suggestions)} suggestions")

                # Select models for each suggestion
                print("\nSelecting models for suggestions...")
                for suggestion in suggestions:
                    model_selection = await self._select_model_for_suggestion(suggestion)
                    suggestion.selected_model = model_selection.selected_model
                    suggestion.model_type = model_selection.model_type
                    print(f"Selected {model_selection.selected_model} ({model_selection.model_type}) for: {suggestion.title}")
                
                return suggestions
            
            except Exception as e:
                print(f"Error generating suggestions: {str(e)}")
                # Provide fallback suggestions based on conversation context
                return self._generate_fallback_suggestions(conversations, memories)

        except Exception as e:
            print(f"Error in generate_from_conversations: {str(e)}")
            return self._generate_fallback_suggestions(conversations, [])

    def _format_messages(self, conversations: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [
            {
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            }
            for msg in conversations
        ]

    def _format_memories(self, memories: List[Dict[str, Any]]) -> str:
        return "\n".join(
            memory.get("memory", "") for memory in memories
        )

    def _generate_fallback_suggestions(
        self,
        conversations: List[Dict[str, str]],
        memories: List[Dict[str, Any]]
    ) -> List[Suggestion]:
        """Generate fallback suggestions based on conversation context when API calls fail."""
        fallback_suggestions = []
        
        # Extract topics from conversations and memories
        all_content = " ".join([
            msg.get("content", "").lower() 
            for msg in conversations
        ] + [
            memory.get("memory", "").lower() 
            for memory in memories
        ])

        # Add coding-related suggestion if relevant keywords are found
        if any(term in all_content for term in ["python", "code", "algorithm", "graph", "function", "programming", "development"]):
            fallback_suggestions.append(
                Suggestion(
                    title="Continue working on coding project",
                    description="Based on your recent work with algorithms and Python, you might want to explore optimization techniques or add more features.",
                    model_type=ModelType.CODE,
                    selected_model="anthropic/claude-3.7-sonnet"
                )
            )

        # Add image-related suggestion if relevant keywords are found
        if any(term in all_content for term in ["image", "visual", "design", "logo", "picture", "photo"]):
            fallback_suggestions.append(
                Suggestion(
                    title="Create visual content",
                    description="Based on your interest in visuals, consider creating some new designs or images.",
                    model_type=ModelType.IMAGE,
                    selected_model="openai/gpt-image-1"
                )
            )

        # Add writing-related suggestion if relevant keywords are found
        if any(term in all_content for term in ["write", "blog", "story", "post", "article"]):
            fallback_suggestions.append(
                Suggestion(
                    title="Expand your writing project",
                    description="Consider developing your recent writing ideas further, whether it's technical documentation or creative writing.",
                    model_type=ModelType.TEXT,
                    selected_model="gpt-4.1"
                )
            )

        # Always include a general suggestion if no other suggestions were added
        if not fallback_suggestions:
            fallback_suggestions.append(
                Suggestion(
                    title="Continue the conversation",
                    description="Feel free to ask more questions or explore other topics.",
                    model_type=ModelType.TEXT,
                    selected_model="gpt-4o-mini"
                )
            )

        return fallback_suggestions
