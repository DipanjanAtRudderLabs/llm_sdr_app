from profiles_rudderstack.project import WhtProject
from .llm_email_gen import LLMEmailGenModel

def register_extensions(project: WhtProject):
    project.register_model_type(LLMEmailGenModel)
