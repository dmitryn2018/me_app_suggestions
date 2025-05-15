import pytest
import os
import httpx
from dotenv import load_dotenv
from app.services.generator import SuggestionGenerator
from app.services.memory import MemoryService
from app.models import ModelType, Suggestion

load_dotenv()

# Configure pytest-asyncio to use function scope for event loops
pytestmark = pytest.mark.asyncio(scope="function")

# Configure test environment
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "True"

@pytest.fixture
def test_conversation():
    return [
        {
            "role": "user",
            "content": "Hi there! I'm working on a graph project—could you write a Python function that optimizes a depth-first search with memoization for a weighted graph and explain its time and space complexity?"
        },
        {
            "role": "assistant",
            "content": "Absolutely. Here's a function using DFS with memoization to cache intermediate results and avoid redundant work..."
        },
        {
            "role": "user",
            "content": "Great, thanks! Next, I need to draft a blog post outline about remote work best practices. Could you suggest headings and bullet points?"
        },
        {
            "role": "assistant",
            "content": "**Blog Post Outline: \"Mastering Remote Work: Best Practices for Productivity and Well-Being\"**..."
        },
        {
            "role": "user",
            "content": "Perfect. Now, could you write a short fantasy story about a traveling musician who discovers magic through song?"
        },
        {
            "role": "assistant",
            "content": "Elara strummed her weathered lute beneath the shadow of the Moonspire cliffs..."
        }
    ]

@pytest.fixture
def full_conversation():
    return [
  {
    "role": "user",
    "content": "Hey! First, I’m tackling a network-optimization project in Python: could you design an efficient capacity-scaling max-flow algorithm, prove its time complexity, and outline edge-case pitfalls I should watch for, and write the code?"
  },
  {
    "role": "assistant",
    "content": "Certainly. Capacity scaling builds on the Ford–Fulkerson framework but groups augmenting paths by residual-capacity tiers… (detailed algorithm, proof, and edge cases follow)."
  },
  {
    "role": "user",
    "content": "Great. Switching gears—I need a well-structured product-requirements document for a mid-sized SaaS feature release. Could you draft an outline with bullet points for goals, success metrics, and stakeholder notes?"
  },
  {
    "role": "assistant",
    "content": "Here’s a concise PRD skeleton:\n\n1. **Objective & Background** …\n2. **Success Metrics** …\n3. **User Stories** …\n4. **Dependencies & Risks** …\n5. **Open Questions / Next Steps** …"
  },
  {
    "role": "user",
    "content": "Now for something creative—write a vivid 150-word fantasy advert that could headline our marketing campaign for an open-world RPG, making it irresistible to adventure fans."
  },
  {
    "role": "assistant",
    "content": "“When dusk falls over Eldoria, only the bold dare cross the Shattered Realms….” (engaging, persuasive copy continues)."
  },
  {
    "role": "user",
    "content": "Before launch, I need an analytical pros-and-cons breakdown: should our startup go fully remote or keep a hybrid office? Please include operational, cultural, and cost angles."
  },
  {
    "role": "assistant",
    "content": "Here’s a balanced matrix comparing remote vs. hybrid across productivity, recruitment reach, overhead, team cohesion, and compliance…"
  },
  {
    "role": "user",
    "content": "Quick fact-check: what’s the latest estimated population of Switzerland? I prefer to use grok 3 to answer this question."
  },
  {
    "role": "assistant",
    "content": "Switzerland’s population is roughly 8.9 million people according to 2024 estimates."
  },
  {
    "role": "user",
    "content": "And just a casual heads-up—what’s the weather supposed to be like in New York City tomorrow morning?"
  },
  {
    "role": "assistant",
    "content": "Tomorrow morning in NYC looks partly cloudy around 60 °F (16 °C) with light westerly breezes."
  },
  {
    "role": "user",
    "content": "For my thesis, outline a detailed literature review on AI alignment research since 2022, grouping papers by approach and highlighting open problems."
  },
  {
    "role": "assistant",
    "content": "Below is a structured survey segmented into value learning, interpretability, scalable oversight, and formal verification—with citations and gaps noted…"
  },
  {
    "role": "user",
    "content": "On a lighter note, I’m starving—got any quick vegetarian lunch ideas I can whip up in under ten minutes with pantry staples?"
  },
  {
    "role": "assistant",
    "content": "Sure! Try a chickpea-avocado smash wrap, five-minute tomato bruschetta on toast, or a microwave lentil soup using canned lentils and veggie broth…"
  },
  {
    "role": "user",
    "content": "What’s buzzing on social media right now about artificial-intelligence layoffs—any notable Twitter threads or memes making waves?"
  },
  {
    "role": "assistant",
    "content": "Trending hashtag **#AIXodus** is circulating; a viral thread by analyst @TechNomad breaks down recent cuts at three big firms, and a meme format featuring the ‘Distracted Boyfriend’ is being remixed to joke about engineers eyeing startups…"
  },
  {
    "role": "user",
    "content": "Could you summarize the three most recent *Nature* papers on fault-tolerant quantum computing, noting experimental setups and key findings?"
  },
  {
    "role": "assistant",
    "content": "Here’s a concise summary:\n\n1. **Superconducting Lattice with 127 Qubits** – IBM team demonstrates…\n2. **Topological Photonic Qubits** – University of Sydney reports…\n3. **Trapped-Ion Barium Array** – Innsbruck group achieves…"
  },
  {
    "role": "user",
    "content": "First visual request: could you generate a photorealistic cyberpunk street scene at twilight with rain-soaked neon signs?"
  },
  {
    "role": "assistant",
    "content": "Absolutely. I’ll leverage **Recraft V3**, which shines at photorealistic imagery with complex lighting and reflective surfaces—perfect for a rain-drenched cyberpunk boulevard. I’ll include vivid neon palettes, slick puddles, and atmospheric haze."
  },
  {
    "role": "user",
    "content": "Next up, I’d like a richly detailed illustration of a medieval dragon siege on a castle—dynamic composition, dramatic lighting."
  },
  {
    "role": "assistant",
    "content": "Great choice. I’ll use **OpenAI’s GPT-Image 1**, known for versatile, high-quality illustrations with fine detail, to capture the fury of a dragon assaulting stone ramparts under torch-lit skies."
  },
  {
    "role": "user",
    "content": "Then please design a clean vector icon set for a fitness app—dumbbells, heart-rate, yoga mat—using a pastel colorway."
  },
  {
    "role": "assistant",
    "content": "For crisp, scalable graphics I’ll tap **Recraft V3-SVG**. It excels at vector output, ensuring your icons stay sharp at any size while maintaining the soft pastel palette you want."
  },
  {
    "role": "user",
    "content": "I also need an ultra-high-resolution panoramic alpine landscape suitable for a six-foot gallery print."
  },
  {
    "role": "assistant",
    "content": "To achieve that gigantic clarity I’ll work with **Flux 1.1 Pro Ultra** from Black Forest Labs. Its ultra-high-resolution capability will render snow-capped peaks and valley mist without losing detail even at large formats."
  },
  {
    "role": "user",
    "content": "Finally, craft an interactive infographic that combines text and simple animations to explain the greenhouse effect to middle-school students."
  },
  {
    "role": "assistant",
    "content": "I’ll employ **Gemini 2.0 Flash-Exp**—ideal for multimodal projects mixing visuals and explanatory text. Expect layered graphics with animated arrows showing heat transfer, plus concise captions suitable for a classroom setting."
  }
]

@pytest.fixture
def suggestion_generator():
    # Ensure required environment variables are set
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY must be set"
    assert os.getenv("MEM0_API_KEY"), "MEM0_API_KEY must be set"
    
    # Get proxy URL from environment if set
    proxy_url = os.getenv("OPENAI_PROXY_URL")
    
    return SuggestionGenerator(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        mem0_api_key=os.getenv("MEM0_API_KEY"),
        proxy_url=proxy_url
    )

@pytest.fixture
def memory_service():
    return MemoryService()

# @pytest.mark.asyncio
# async def test_generate_suggestions_from_conversations(suggestion_generator, full_conversation):
#     """Test generating suggestions from a conversation."""
#     # Generate suggestions
#     test_user_id = "test_user_123"
#     suggestions = await suggestion_generator.generate_from_conversations(full_conversation, test_user_id, [])
    
#     # Verify suggestions were generated
#     assert len(suggestions) > 0, "Should generate at least one suggestion"
    
#     # Verify suggestion structure
#     for suggestion in suggestions:
#         assert suggestion.title, "Suggestion should have a title"
#         assert suggestion.description, "Suggestion should have a description"
#         assert suggestion.type in [ModelType.TEXT, ModelType.CODE, ModelType.IMAGE], "Should have valid type"

@pytest.mark.asyncio
async def test_memory_integration_with_full_conversation(suggestion_generator, memory_service, full_conversation):
    """Test saving and retrieving the full conversation from memory."""
    test_user_id = "test_user_456"
    
    try:
        print("\n=== Starting memory integration test ===")
        # print("\nSaving full conversation in memory...")
        # add_response = await memory_service.add_memory(test_user_id, full_conversation)
        # assert add_response, "Should get response from add_memory"
        # print("Full conversation saved in memory")

        # Request memories from memory service
        print("\nRequesting memories from memory service...")
        memories = await memory_service.get_recent_conversations(test_user_id)
        print(f"Received {len(memories)} memories")
        
        # Generate suggestions using the saved conversation and memories
        print("\nGenerating suggestions from first exchange and memories...")
        suggestions = await suggestion_generator.generate_from_conversations(
            [],#full_conversation[:2],  # Use just the first exchange to test memory integration
            test_user_id,
            memories=memories  # Add memories from memory service to the call param
        )
        
        # Verify suggestions were generated
        print(f"\nVerifying suggestions (got {len(suggestions)})...")
        assert len(suggestions) > 0, "Should generate suggestions"
        for suggestion in suggestions:
            print(f"- {suggestion.title} ({suggestion.model_type}) - Model: {suggestion.selected_model}")
        
        has_coding_suggestion = any(s.model_type.lower() == ModelType.CODE.lower() for s in suggestions)
        has_writing_suggestion = any(s.model_type.lower() == ModelType.TEXT.lower() for s in suggestions)
        has_image_suggestion = any(s.model_type.lower() == ModelType.IMAGE.lower() for s in suggestions)
        
        print(f"- Has coding suggestion: {has_coding_suggestion}")
        print(f"- Has writing suggestion: {has_writing_suggestion}")
        print(f"- Has image suggestion: {has_image_suggestion}")
        
        assert has_coding_suggestion, "Should have coding-related suggestions based on memory"
        assert has_writing_suggestion, "Should have writing-related suggestions based on memory"
        assert has_image_suggestion, "Should have image-related suggestions based on memory"
        print("\n=== Memory integration test completed successfully ===")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        pytest.fail(f"Memory integration test failed: {str(e)}")

@pytest.mark.asyncio
async def test_model_selection(suggestion_generator):
    """Test that appropriate models are selected for different suggestion types."""
    # Create test suggestions
    test_suggestions = [
        Suggestion(
            title="Write a Python algorithm",
            description="Create an efficient sorting algorithm",
            model_type=ModelType.CODE,
            selected_model="anthropic/claude-3.7-sonnet"
        ),
        Suggestion(
            title="Generate a logo",
            description="Create a modern logo for a tech startup",
            model_type=ModelType.IMAGE,
            selected_model="openai/gpt-image-1"
        ),
        Suggestion(
            title="Write a story",
            description="Write a creative short story",
            model_type=ModelType.TEXT,
            selected_model="gpt-4.1"
        )
    ]
    
    # Test model selection for each suggestion
    for suggestion in test_suggestions:
        model_selection = await suggestion_generator._select_model_for_suggestion(suggestion)
        
        # Verify model type matches suggestion type
        if suggestion.model_type == ModelType.IMAGE:
            assert model_selection.model_type == "Image", "Image suggestions should use Image models"
            assert any(model in model_selection.selected_model for model in [
                "openai/gpt-image-1",
                "recraft-ai/recraft-v3",
                "recraft-ai/recraft-v3-svg",
                "black-forest-labs/flux-1.1-pro-ultra"
            ]), "Should select an appropriate image model"
        else:
            assert model_selection.model_type == "Text", "Non-image suggestions should use Text models"
            assert any(model in model_selection.selected_model for model in [
                "anthropic/claude-3.7-sonnet",
                "anthropic/claude-3.5-sonnet",
                "gpt-4.1",
                "o3-mini",
                "gpt-4o-mini"
            ]), "Should select an appropriate text model"
        
        # Verify specific model selection based on suggestion type
        if suggestion.model_type == ModelType.CODE:
            assert model_selection.selected_model == "anthropic/claude-3.7-sonnet", "Should use Claude 3.7 for coding tasks"
        elif suggestion.model_type == ModelType.TEXT and "story" in suggestion.title.lower():
            assert model_selection.selected_model == "gpt-4.1", "Should use GPT-4.1 for creative writing"
