from llmSHAP import DataHandler, BasicPromptCodec, ShapleyAttribution
from llmSHAP.llm import OpenAIInterface

#Skapa lista med onödiga permanent keys som ignoreras här!!
data = "In what city is the Eiffel Tower?"
handler = DataHandler(data, permanent_keys={0,3,4})

#Prompt som skickas med till ChatGPT för varje anrop
prompt_codec = BasicPromptCodec(system="Answer the question briefly.")

#Creates LLM interface
llm = OpenAIInterface(model_name="gpt-4o-mini")

shap = ShapleyAttribution(model=llm, data_handler=handler, prompt_codec=prompt_codec, use_cache=True)
result = shap.attribution()

print("\n\n### OUTPUT ###")
print(result.output) # The LLM's answer to the question.

print("\n\n### ATTRIBUTION ###")
print(result.attribution) # The attribution score mapping.