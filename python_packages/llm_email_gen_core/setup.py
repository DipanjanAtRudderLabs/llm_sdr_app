from setuptools import setup

setup(
    name='rudderstack_predictions_llm_email_gen_core',
    python_requires=">=3.10",
    version='0.0.1',
    author='Dipanjan Biswas',
    author_email='dipanjan@rudderstack.com',
    description='A py_native model package for constructing outreach emails for SDRs using LLM invocations',
    packages=['rudderstack_predictions_llm_email_gen_core'],
    install_requires=[
        'langchain',
        'pandas',
        'openai',
        'langchain-google-genai',
        'boto3',
        'awscli',
        'botocore'
    ],
)
