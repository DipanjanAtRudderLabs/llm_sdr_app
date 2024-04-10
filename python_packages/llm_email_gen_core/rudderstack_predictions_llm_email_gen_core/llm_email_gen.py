from profiles_rudderstack.model import BaseModelType
from profiles_rudderstack.recipe import PyNativeRecipe
from profiles_rudderstack.material import WhtMaterial
from profiles_rudderstack.logger import Logger
from typing import List
import os
import time
import pandas as pd
import json 
import hashlib
from langchain.chains import ConversationChain
from langchain.llms import Bedrock
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import GoogleGenerativeAI




class LLMEmailGenModel(BaseModelType):
    TypeName = "llm_email_gen"
    BuildSpecSchema = {
        "type": "object",
        "properties": {
            "entity_key": {"type": "string"},
            "inputs": {"type": "array", "items": { "type": "string"}},
            "id_graph_table_name" : {"type": "string"},
            "feature_table_prospect_identifier_field": {"type": "string"},
            "prospect_info_table_name": {"type": "string"},
            "prospect_identifier_field": {"type": "string"},
            "prospect_email_field": {"type": "string"},
            "prospect_name_field": {"type": "string"},
            "prospect_title_field": {"type": "string"},
            "prospect_company_name_field": {"type": "string"},
            "prospect_company_category_field": {"type": "string"},
            "prospect_company_employee_num_field": {"type": "string"},
            "pages_table_name": {"type": "string"},
            "role_responsibility_prompt": {"type": "string"},
            "task_prompt": {"type": "string"},
            "output_field": {"type": "string"},
            "endpoint": {"type": "string"},
            "model": {"type": "string"}
        },
        "required": ["inputs","id_graph_table_name","feature_table_prospect_identifier_field","prospect_info_table_name","prospect_identifier_field",\
            "prospect_email_field","prospect_name_field","prospect_title_field","prospect_company_name_field","prospect_company_category_field",\
                "prospect_company_employee_num_field","pages_table_name","role_responsibility_prompt","task_prompt","output_field","endpoint","model"],
        "additionalProperties": False
    }

    def __init__(self, build_spec: dict, schema_version: int, pb_version: str) -> None:
        super().__init__(build_spec, schema_version, pb_version)

    def get_material_recipe(self)-> PyNativeRecipe:
        return LLMEmailGenRecipe(self.build_spec.get("inputs"),self.build_spec.get("id_graph_table_name"),self.build_spec.get("feature_table_prospect_identifier_field"),\
            self.build_spec.get("prospect_info_table_name"),self.build_spec.get("prospect_identifier_field"),self.build_spec.get("prospect_email_field"),\
                self.build_spec.get("prospect_name_field"),self.build_spec.get("prospect_title_field"),self.build_spec.get("prospect_company_name_field"),\
                    self.build_spec.get("prospect_company_category_field"),self.build_spec.get("prospect_company_employee_num_field"),\
                        self.build_spec.get("pages_table_name"),self.build_spec.get("role_responsibility_prompt"), self.build_spec.get("task_prompt"),\
                            self.build_spec.get("output_field"),self.build_spec.get("endpoint"),self.build_spec.get("model"))

    def validate(self):
        # Model Validate
        return super().validate()


class LLMEmailGenRecipe(PyNativeRecipe):
    def __init__(self, inputs: List[str], id_graph_table_name: str, feature_table_prospect_identifier_field: str, prospect_info_table_name: str, \
        prospect_identifier_field: str, prospect_email_field: str, prospect_name_field: str, prospect_title_field: str, prospect_company_name_field: str, \
            prospect_company_category_field: str, prospect_company_employee_num_field: str, pages_table_name: str, role_responsibility_prompt: str, task_prompt: str,\
                output_field: str, endpoint: str, model: str) -> None:
        self.inputs = inputs
        self.id_graph_table_name = id_graph_table_name
        self.feature_table_prospect_identifier_field = feature_table_prospect_identifier_field
        self.prospect_info_table_name = prospect_info_table_name
        self.prospect_identifier_field = prospect_identifier_field
        self.prospect_email_field = prospect_email_field
        self.prospect_name_field = prospect_name_field
        self.prospect_title_field = prospect_title_field
        self.prospect_company_name_field = prospect_company_name_field
        self.prospect_company_category_field = prospect_company_category_field
        self.prospect_company_employee_num_field = prospect_company_employee_num_field
        self.output_field = output_field
        self.pages_table_name = pages_table_name
        self.role_responsibility_prompt = role_responsibility_prompt
        self.task_prompt = task_prompt
        self.endpoint = endpoint
        self.model = model
        self.logger = Logger("LLMEmailGenRecipe")

    def describe(self, this: WhtMaterial):
        material_name = this.name()
        return f"""Material - {material_name}\nInputs: {self.inputs}\nFeature Table Prospect Identifier Field: {self.feature_table_prospect_identifier_field}\n\
            Prospect Info Table Name: {self.prospect_info_table_name}\nProspect Identifier Field: {self.feature_table_prospect_identifier_field}\n\
                Prospect Email Field: {self.prospect_email_field}\nProspect Name Field: {self.prospect_name_field}\nProspect Title Field: {self.prospect_title_field}\n\
                        Prospect Company Name Field: {self.prospect_company_name_field}\nProspect Company Category Field: {self.prospect_company_category_field}\n\
                            Prospect Company Employee Number Field: {self.prospect_company_employee_num_field}\nOutput Field: {self.output_field}\n\
                                Pages Table Name: {self.pages_table_name}\nRole and Responsibility Prompt: {self.role_responsibility_prompt}\n\
                                    Task Prompt: {self.task_prompt}\nEndpoint: {self.endpoint}\nModel: {self.model}""", ".txt"

    
    def prepare(self, this: WhtMaterial):
        for in_model in self.inputs:
            this.de_ref(in_model)
        
        
    def execute(self, this: WhtMaterial):

        in_model = self.inputs[0]
        input_material = this.de_ref(in_model)

        # read data in batches, only supported in case of snowflake currently
        batch = input_material.get_df(["user_main_id",self.feature_table_prospect_identifier_field])

        batch = batch.dropna() #drop rows with null values, which can only be for null email

        api_call_count = 0
        id_response_list = []

        top_100_pages_query = "select title, url from " + self.pages_table_name + " where timestamp > dateadd(month,-3,current_date()) " + \
                    " group by title, url order by count(*) desc limit 100"

        top_100_pages_df = this.wht_ctx.client.query_sql_with_result(top_100_pages_query)


        for index, row in batch.iterrows():


            try:
                prospect_info_query = "select " + self.prospect_email_field + "," + self.prospect_name_field + "," + self.prospect_title_field + ","  + self.prospect_company_name_field + "," + \
                    self.prospect_company_category_field + "," + self.prospect_company_employee_num_field + " from " + self.prospect_info_table_name + \
                        " where " + self.prospect_identifier_field + " = '" + row[self.feature_table_prospect_identifier_field] + "'"
                prospect_info_df = this.wht_ctx.client.query_sql_with_result(prospect_info_query)

                prospect_email = str(prospect_info_df.iloc[0][self.prospect_email_field])
                prospect_name = str(prospect_info_df.iloc[0][self.prospect_name_field])
                prospect_company_name = str(prospect_info_df.iloc[0][self.prospect_company_name_field])
                prospect_company_num_employees = str(prospect_info_df.iloc[0][self.prospect_company_employee_num_field])
                prospect_company_industry = str(prospect_info_df.iloc[0][self.prospect_company_category_field])
                               
                prospect_page_view_query = "select title , timestamp from " + self.pages_table_name + " where anonymous_id in " + \
                    "(select other_id from " + self.id_graph_table_name + " where user_main_id = '" + row["USER_MAIN_ID"] + "' and " +\
                        " other_id_type = 'anonymous_id') order by timestamp desc limit 5"
                prospect_page_view_df = this.wht_ctx.client.query_sql_with_result(prospect_page_view_query)

                complete_prompt = "Following are the titles and links to top 100 pages on RudderStack website in JSON format : " + \
                    top_100_pages_df.to_json() + " . " + self.role_responsibility_prompt + " " + prospect_name + " of company " +  \
                        prospect_company_name + ". " + prospect_company_name + " is a " +  prospect_company_num_employees + " people, " + \
                            prospect_company_industry + " company. Following are the titles of pages on RudderStack website that the person has visited " + \
                                " most recently : " + prospect_page_view_df["TITLE"].to_json() + ". " + self.task_prompt


                llm = Bedrock(region_name="us-east-1", model_id="anthropic.claude-v2") # default LLM
                api_call_limit = 1533 # default for Bedrock-Claude

                # init LLM based on endpoint and model

                match self.endpoint.lower():
                    case "bedrock":
                        llm = Bedrock(region_name="us-east-1", model_id=self.model.lower()) # LLM init
                        api_call_limit = 1533

                    case "openai":
                        llm = ChatOpenAI(temperature=0,model_name=self.model.lower())
                        api_call_limit = 125

                    case "google":
                        llm = GoogleGenerativeAI(model=self.model.lower())
                        api_call_limit = 10000

                chain = ConversationChain(llm = llm) # chain init

                # Prompt construction

                template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. \
                    If the AI does not know the answer to a question, it truthfully says it does not know.

                Current conversation:
                {history}
                Human: {input}
                AI Assistant:"""

                PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

                # conversation construction
                conversation = ConversationChain(
                    prompt=PROMPT,
                    llm=llm,
                    verbose=False,
                    memory=ConversationBufferMemory(ai_prefix="AI Assistant"),
                )

                result = ""

                if api_call_count < api_call_limit:
                    #delay to avoid rate limit
                    time.sleep(5)
                    result = conversation.predict(input = complete_prompt)
                    api_call_count = api_call_count + 1
                    id_response = {}
                    id_response["user_main_id"] = row[0]
                    id_response["email_address"] = prospect_email
                    id_response["prompt"] = complete_prompt
                    id_response[self.output_field] = result
                    id_response_list.append(id_response)

                else:
                    self.logger.info("Internal rate limit reached for " + self.endpoint.lower() + ":" + self.model.lower())
                

            except Exception as e: # unable to retrieve data (table/row does not exist or other)                
                self.logger.info(str(e))
                


        if len(id_response_list) > 0:
            id_response_df = pd.DataFrame(id_response_list)

            this.write_output(id_response_df)
        else:
            self.logger.info("No data to materialize")



        
