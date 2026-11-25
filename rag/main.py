import os
import glob
from dotenv import load_dotenv
from pathlib import Path
import gradio as gr
from openai import OpenAI



load_dotenv(override=True)

api_key = os.getenv("OPENROUTER_API_KEY")

client =  OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


knowledge = {}

filenames = glob.glob("../knowledge-base/employees/*")

for filename in filenames:
    name = Path(filename).stem.split(" ")[-1]
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
        knowledge[name.lower()] = text


product_filenames = glob.glob("../knowledge-base/products/*")

for filename in product_filenames:
    name = Path(filename).stem.split(" ")[-1]
    with open(filename,'r', encoding='utf-8') as f:
        text = f.read()
        knowledge[name.lower()] = text
        
        
SYSTEM_PREFIX = """
You represent Insurellm, the Insurance Tech company.
You are an expert in answering questions about Insurellm; its employees and its products.
You are provided with additional context that might be relevant to the user's question.
Give brief, accurate answers. If you don't know the answer, say so.

Relevant context:
"""


def get_relevant_context(message):
    text = "".join(ch for ch in message if ch.isalpha() or ch.isspace()) 
    words = text.lower().split()
    relevant_context = []
    for word in words:
        if word in knowledge:
            relevant_context.append(knowledge[word])
            
    return relevant_context


def get_relevant_context_pythonic(message):
    text = "".join(ch for ch in message if ch.isalpha() or ch.isspace()) 
    words = text.lower().split()
    return [knowledge[word] for word in words if word in knowledge]


print( "Response Before additional context ==============\n\n",get_relevant_context_pythonic("Who is lancaster?"))

def additional_context(message):
    relevant_context = get_relevant_context_pythonic(message)
    print("Response after relevant context ==============\n\n",relevant_context)
    if not relevant_context:
        result = "There is no relevant context to the users question"
    else:
        result = "The following context is might be relevant to answer the user's question: \n\n"
        result += "\n\n".join(relevant_context)
        
    return result
        
MODEL = "gpt-4.1-nano" 

print("Response after additional context ==============\n\n",additional_context("Who is lancaster?"))
    
def chat(message, history):
    system_context = SYSTEM_PREFIX + additional_context("who is lancaster?")
    print("SYSTEM CONTEXT ===================\n\n",system_context)
    messages = [{"role":"system","content":system_context}] + history + [{"role":"user","content":message}]
    response = client.chat.completions.create(model=MODEL,messages=messages)
    return response.choices[0].message.content

chat("who r u", [])

view = gr.ChatInterface(chat).launch(server_port=5678,inbrowser=True)