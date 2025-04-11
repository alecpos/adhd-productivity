"""Service for interacting with Hugging Face's LLM models."""

import os
import requests.exceptions
import socket
from typing import Optional, Dict, List, Any
from huggingface_hub import (
    HfApi,
    HfFolder,
    Repository,
    create_repo,
    get_full_repo_name,
    login,
    model_info,
    InferenceClient,
)
from huggingface_hub.utils import (
    HfHubHTTPError,
    RepositoryNotFoundError,
    RevisionNotFoundError,
    LocalEntryNotFoundError,
    BadRequestError,
)
from app.core.config import settings
import logging
from time import sleep

logger = logging.getLogger(__name__)


class LLMService:
    """Service for language model operations."""

    def __init__(self, max_retries: int = 1, retry_delay: int = 5, offline_mode: bool = False):
        """Initialize LLM service with retry logic.

        Args:
            max_retries: Maximum number of retries when connecting to HuggingFace
            retry_delay: Delay between retries in seconds
            offline_mode: If True, skip trying to connect to HuggingFace
        """
        self.api = HfApi()
        self.text_generation_model = None
        self.offline_mode = offline_mode

        # Check if OFFLINE_MODE environment variable is set
        if os.environ.get("OFFLINE_MODE", "").lower() in ("true", "1", "yes"):
            self.offline_mode = True

        if self.offline_mode:
            logger.info("LLM Service initialized in offline mode")
        else:
            self._initialize_model(max_retries, retry_delay)

    def _initialize_model(self, max_retries: int, retry_delay: int) -> None:
        """Initialize the model with retry logic."""
        for attempt in range(max_retries):
            try:
                # First try to get model info to verify access
                model_info("deepseek-ai/DeepSeek-R1")

                # Then initialize the inference client
                self.text_generation_model = InferenceClient(
                    model="deepseek-ai/DeepSeek-R1",
                )
                logger.info("Successfully initialized DeepSeek-R1 model")
                return
            except (RepositoryNotFoundError, RevisionNotFoundError) as e:
                logger.error(f"Model repository error: {str(e)}")
                self.text_generation_model = None
                break
            except LocalEntryNotFoundError as e:
                logger.error(f"Local cache error: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                continue
            except (HfHubHTTPError, BadRequestError) as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                else:
                    logger.error("Failed to initialize DeepSeek-R1 model after all retries")
                    self.text_generation_model = None
            except (requests.exceptions.ConnectionError, socket.gaierror) as e:
                logger.warning(f"Network connection error: {str(e)}")
                logger.info("Switching to offline mode due to network connectivity issues")
                self.offline_mode = True
                self.text_generation_model = None
                break

    async def generate_text(self, prompt: str, max_length: int = 100) -> Optional[str]:
        """Generate text from prompt."""
        if self.offline_mode or not self.text_generation_model:
            logger.warning("Text generation model not available, using fallback")
            return self._fallback_generate_text(prompt, max_length)

        try:
            response = self.text_generation_model.text_generation(
                prompt,
                parameters={
                    "max_length": max_length,
                    "temperature": 0.7,
                    "num_return_sequences": 1,
                    "do_sample": True,
                },
            )

            if isinstance(response, list) and response:
                return response[0]["generated_text"]
            return None

        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return self._fallback_generate_text(prompt, max_length)

    def _fallback_generate_text(self, prompt: str, max_length: int = 100) -> str:
        """Fallback text generation when the model is not available."""
        logger.info("Using fallback text generation")
        return f"{prompt} [Offline fallback response]"

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a response using the text generation model."""
        if self.offline_mode or not self.text_generation_model:
            logger.warning("Text generation model not available, using fallback")
            return self._fallback_generate_response(prompt, context, system_prompt)

        try:
            # Construct the full prompt
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System: {system_prompt}\n\n"
            if context:
                full_prompt += f"Context: {context}\n\n"
            full_prompt += f"User: {prompt}\n\nAssistant:"

            # Set default parameters if none provided
            default_params = {
                "max_length": 1024,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
            }
            generation_params = {**default_params, **(params or {})}

            # Generate response
            response = self.text_generation_model(inputs=full_prompt, params=generation_params)

            return response[0]["generated_text"].strip()

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._fallback_generate_response(prompt, context, system_prompt)

    def _fallback_generate_response(
        self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None
    ) -> str:
        """Fallback response generation when the model is not available."""
        logger.info("Using fallback response generation")

        # Include a generic response that's contextually relevant
        if "analyze" in prompt.lower() or "task complexity" in prompt.lower():
            return "This is a medium complexity task requiring moderate focus."
        elif "focus strategies" in prompt.lower():
            return "Try using the Pomodoro technique with 25-minute focus sessions."
        else:
            return f"I've received your request about: {prompt}. Unable to process with AI in offline mode."

    async def analyze_task_complexity(self, task_description: str) -> Dict[str, Any]:
        """Analyze task complexity and provide ADHD-specific insights."""
        try:
            if self.offline_mode or not self.text_generation_model:
                logger.warning("Using fallback task complexity analysis")
                return self._fallback_task_complexity_analysis(task_description)

            # Create a structured prompt for task analysis
            analysis_prompt = f"""
            Analyze the following task for ADHD considerations:
            Task: {task_description}

            Provide analysis in the following areas:
            1. Task complexity
            2. Focus requirements
            3. Potential challenges
            4. Breakdown suggestions
            5. Energy level recommendation
            """

            # Get analysis from model
            response = await self.generate_response(
                prompt=analysis_prompt,
                params={"temperature": 0.3},  # Lower temperature for more focused analysis
            )

            # Parse and structure the response
            # Note: In production, you might want to use a more structured approach
            return {
                "complexity_level": 3,  # You would parse this from the response
                "time_estimate": 30,
                "focus_requirements": {"sustained": 0.8, "detail": 0.7},
                "potential_challenges": ["task switching", "time management"],
                "breakdown_suggestions": ["break into smaller steps", "set timers"],
                "energy_level_recommendation": "medium",
                "adhd_friendly_score": 0.7,
            }

        except Exception as e:
            logger.error(f"Error analyzing task complexity: {str(e)}")
            return self._fallback_task_complexity_analysis(task_description)

    def _fallback_task_complexity_analysis(self, task_description: str) -> Dict[str, Any]:
        """Provide fallback task complexity analysis when model is unavailable."""
        # Simplified heuristic approach based on task description length and keywords

        # Determine complexity based on description length
        description_length = len(task_description)
        if description_length < 50:
            complexity = 2
            time_estimate = 20
        elif description_length < 100:
            complexity = 3
            time_estimate = 30
        else:
            complexity = 4
            time_estimate = 45

        # Default values as fallback
        return {
            "complexity_level": complexity,
            "time_estimate": time_estimate,
            "focus_requirements": {"sustained": 0.7, "detail": 0.6},
            "potential_challenges": ["distraction", "time management"],
            "breakdown_suggestions": ["break into smaller steps", "set reminders"],
            "energy_level_recommendation": "medium",
            "adhd_friendly_score": 0.6,
        }

    async def generate_focus_strategies(
        self, user_profile: Dict[str, Any], task_type: str
    ) -> List[Dict[str, Any]]:
        """Generate personalized focus strategies based on user profile and task type."""
        try:
            if self.offline_mode or not self.text_generation_model:
                logger.warning("Using fallback focus strategies")
                return self._fallback_focus_strategies(user_profile, task_type)

            # Create a structured prompt for strategy generation
            strategy_prompt = f"""
            Generate ADHD-friendly focus strategies for:
            Task Type: {task_type}
            User Profile: {user_profile}

            Consider:
            1. User's performance history
            2. Preferred work styles
            3. Energy patterns
            4. Known challenges
            """

            # Get strategies from model
            response = await self.generate_response(
                prompt=strategy_prompt, params={"temperature": 0.7}
            )

            # Parse and structure the response
            # In production, you would parse the actual response
            return [
                {
                    "title": "Pomodoro with Breaks",
                    "description": "Use 25-minute focused work sessions with 5-minute breaks",
                    "duration": 25,
                    "break_intervals": [25, 50, 75],
                    "environment": ["quiet space", "minimal distractions"],
                    "tools": ["timer", "noise-canceling headphones"],
                },
                {
                    "title": "Task Chunking",
                    "description": "Break the task into 15-minute manageable chunks",
                    "duration": 15,
                    "break_intervals": [15, 30, 45],
                    "environment": ["organized workspace", "good lighting"],
                    "tools": ["checklist", "task timer"],
                },
            ]

        except Exception as e:
            logger.error(f"Error generating focus strategies: {str(e)}")
            return self._fallback_focus_strategies(user_profile, task_type)

    def _fallback_focus_strategies(
        self, user_profile: Dict[str, Any], task_type: str
    ) -> List[Dict[str, Any]]:
        """Provide fallback focus strategies when model is unavailable."""
        # Default strategies that work for most ADHD individuals
        common_strategies = [
            {
                "title": "Pomodoro Technique",
                "description": "Use 25-minute focused work sessions with 5-minute breaks",
                "duration": 25,
                "break_intervals": [25, 50, 75],
                "environment": ["quiet space", "minimal distractions"],
                "tools": ["timer", "noise-canceling headphones"],
            }
        ]

        # Add task-specific strategies
        if task_type.lower() in ["creative", "writing", "brainstorming"]:
            common_strategies.append(
                {
                    "title": "Mind Mapping",
                    "description": "Visually organize thoughts before starting task",
                    "duration": 30,
                    "break_intervals": [30, 60],
                    "environment": ["comfortable space", "inspiration materials"],
                    "tools": ["whiteboard", "colored pens", "mind mapping app"],
                }
            )
        elif task_type.lower() in ["focus", "study", "reading"]:
            common_strategies.append(
                {
                    "title": "Body Doubling",
                    "description": "Work alongside someone else to maintain accountability",
                    "duration": 45,
                    "break_intervals": [45, 90],
                    "environment": ["shared workspace", "accountability partner"],
                    "tools": ["video call app", "shared timer"],
                }
            )
        else:
            common_strategies.append(
                {
                    "title": "Task Chunking",
                    "description": "Break the task into 15-minute manageable chunks",
                    "duration": 15,
                    "break_intervals": [15, 30, 45],
                    "environment": ["organized workspace", "good lighting"],
                    "tools": ["checklist", "task timer"],
                }
            )

        return common_strategies

    def is_model_available(self) -> bool:
        """Check if the model is available."""
        return not self.offline_mode and self.text_generation_model is not None

    def get_model_info(self) -> Optional[dict]:
        """Get information about the current model."""
        if self.offline_mode:
            logger.warning("Operating in offline mode, model info not available")
            return {"name": "offline-fallback", "status": "offline"}

        try:
            return model_info("deepseek-ai/DeepSeek-R1")
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {"name": "unknown", "status": "error", "error": str(e)}

    async def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text input."""
        if self.offline_mode or not self.text_generation_model:
            logger.warning("Using fallback structured data extraction")
            return self._fallback_extract_structured_data(text)

        try:
            # Create a structured prompt for data extraction
            extraction_prompt = f"""
            Extract structured data from the following text:
            Text: {text}

            Extract the following elements if present:
            1. Task names
            2. Dates and times
            3. People mentioned
            4. Locations
            5. Priority indicators
            """

            # Get extraction from model
            response = await self.generate_response(
                prompt=extraction_prompt, params={"temperature": 0.3}
            )

            # Mock parsed data (in production, you would parse the actual response)
            return {
                "confidence": 0.85,
                "entities": [
                    {"type": "task", "value": "complete project", "confidence": 0.9},
                    {"type": "date", "value": "tomorrow", "confidence": 0.8},
                ],
                "intent": "task_creation",
            }

        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
            return self._fallback_extract_structured_data(text)

    def _fallback_extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Provide fallback structured data extraction when model is unavailable."""
        # Very basic extraction using simple string matching
        entities = []

        # Check for basic date keywords
        date_keywords = [
            "today",
            "tomorrow",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for keyword in date_keywords:
            if keyword.lower() in text.lower():
                entities.append({"type": "date", "value": keyword, "confidence": 0.7})

        # Check for time patterns (very simplistic)
        if "am" in text.lower() or "pm" in text.lower():
            entities.append({"type": "time", "value": "time_mentioned", "confidence": 0.6})

        # Assume task creation intent for simplicity
        return {"confidence": 0.6, "entities": entities, "intent": "task_creation"}

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for sentiment, complexity, key phrases, etc."""
        if self.offline_mode or not self.text_generation_model:
            logger.warning("Using fallback text analysis")
            return self._fallback_analyze_text(text)

        try:
            # In a real implementation, you would call the LLM here
            # For now, return mock data
            return {
                "sentiment": 0.6,
                "complexity": 0.4,
                "key_phrases": ["important task", "project deadline"],
                "topics": ["work", "planning"],
                "summary": "A note about completing a project by the deadline",
                "recommendations": ["Set a reminder", "Break down into subtasks"],
                "meta_data": {"word_count": len(text.split())},
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return self._fallback_analyze_text(text)

    def _fallback_analyze_text(self, text: str) -> Dict[str, Any]:
        """Provide fallback text analysis when model is unavailable."""
        # Very basic analysis
        words = text.split()
        word_count = len(words)

        # Simple sentiment based on positive/negative word counts
        positive_words = ["good", "great", "excellent", "happy", "excited", "love", "best"]
        negative_words = ["bad", "terrible", "awful", "sad", "angry", "hate", "worst"]

        positive_count = sum(1 for word in words if word.lower() in positive_words)
        negative_count = sum(1 for word in words if word.lower() in negative_words)

        # Calculate simple sentiment score
        if positive_count + negative_count > 0:
            sentiment = positive_count / (positive_count + negative_count)
        else:
            sentiment = 0.5  # Neutral

        return {
            "sentiment": sentiment,
            "complexity": min(1.0, word_count / 100),  # Simple complexity based on length
            "key_phrases": [],
            "topics": [],
            "summary": text[:100] + "..." if len(text) > 100 else text,
            "recommendations": ["Consider breaking into smaller tasks"],
            "meta_data": {"word_count": word_count},
        }
