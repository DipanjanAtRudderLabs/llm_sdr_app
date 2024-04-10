# GenAI Based Email Content Generation : Sample Profiles Project 

This is a sample Profiles project that leverages Generative AI technology to generate content for emails that Sales Development Representatives can send to prospects, recommending popular reading material from the corporate website. The prospect's company profile and his/her browsing behaviour on the corporate website are utilised to make the resulting communication focused and personalised

# Pre-requisites
- You need to have the latest version of RudderStack Profiles installed. Refer to https://www.rudderstack.com/docs/profiles/get-started/profile-builder/ for more details
# Steps
- Clone this repository  
- Navigate to the root of the cloned repository and then issue the command  `pip install -e python_packages/llm_email_gen_core`  
-   The PyNative model involved in this project requires the following inputs
	- A table containing the `USER_MAIN_ID` and the corresponding identifier for the prospect from the Customer Relationship Management (CRM) system. For organisations using SalesForce along with RudderStack and including SalesForce data as part of their RudderStack Customer 360 profile - this identifier can be `SF_LEAD_ID`as provided in the `profiles.yaml` file of this project
	- `id_graph_table_name` - this is the table were RudderStack Profiles maintains mappings of all possible identifiers for a user corresponding to the unique Rudder Identifier (`user_main_id`) for that user. Such identifiers can include `anonymous_id`, `email` etc. This information is required as the model retrieves browsing information for the target user by using all possible identifiers for that user
	- `feature_table_prospect_identifier_field` - this would be the **column name** in the RudderStack Customer 360 table that contains the identifier that uniquely identifies the user in the CRM. Example - `SF_LEAD_ID`
	- `prospect_info_table_name` - this would be the **fully qualified name** of the table containing the prospect information (name, title, email, company name, company category, company employee count). This can be data sync-ed into the warehouse from the CRM using RudderStack Cloud Extract (https://www.rudderstack.com/docs/sources/extract/)
	- `prospect_identifier_field` - this would be the **column name** for the prospect identifier in the prospect information table mentioned above
	- `prospect_email_field`, `prospect_name_field`, `prospect_title_field`, `prospect_company_name_field`, `prospect_company_category_field`, `prospect_company_employee_num_field` - these would **all** be **names of columns** in the prospect information table
	- `pages_table_name` - this would be the **fully qualified name** of the table where the user's page view events have been captured. For RudderStack users this would be `pages`
	- `output_field` - this would be the **column name** where the output is expected to be generated. Example - `email_content`
- An additional column  `prompt` would also get included in the final table showing the prompt that was used for generating the content
- This supports OpenAI, Bedrock and Google - you need to specify a combination of  `endpoint`  and  `model`  in the  `profiles.yaml`  file of the PyNative project

	- For OpenAI

		- `endpoint: openai`
		- `model`  values can be be chosen from the model names specified in  [https://platform.openai.com/docs/models/](https://platform.openai.com/docs/models/)
		- To run use  `OPENAI_API_KEY=… pb run`

	- For Bedrock

		- `endpoint: bedrock`
		- `model`  values can be chosen from  [https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html)  (please make sure that you have enabled access to the model you’re trying to use)
		- AWS CLI should be have been configured and/or there should be valid  `.aws/credentials`  file under use home directory before  `pb run`  can be executed

	- For Google

		- `endpoint: google`
		- `model`  values can be chosen from  [https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models)  (except vision models)
		- To run use  `GOOGLE_API_KEY=… pb run`

