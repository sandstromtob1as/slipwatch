from llmSHAP import DataHandler, BasicPromptCodec, ShapleyAttribution
from llmSHAP.llm import OpenAIInterface
import json 
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "test_file.json")

with open("test_file.json", "r") as f:
    data = json.load(f)

#Ta bort timestamp innan anropar llmSHAP
timestamp = data.pop("timestamp")

handler = DataHandler(data)


#Prompt som skickas med till ChatGPT för varje anrop
prompt_codec = BasicPromptCodec(system="Analyze the given data and answer with a simple" \
"and consise explaination of the sequence of events from the perspective of analyzing a potential fall of an elderly person")

#Creates LLM interface
llm = OpenAIInterface(model_name="gpt-4o-mini")

shap = ShapleyAttribution(model=llm, data_handler=handler, prompt_codec=prompt_codec, use_cache=True)
result = shap.attribution()

print("\n\nGenerated message:")
print(result.output) # The LLM's answer to the question.

print("\n\n### ATTRIBUTION ###")
print(result.attribution) # The attribution score mapping.