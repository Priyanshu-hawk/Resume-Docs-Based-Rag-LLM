from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import PromptTemplate
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.core import Settings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.core.node_parser import SentenceSplitter
import torch
from transformers import BitsAndBytesConfig
from dotenv import load_dotenv
load_dotenv()

def get_llm_settings(contect_window: int, max_new_token: int, ):
    system_prompt = """
    You are a Q&A assistant. Your goal is to answer questions based on the text \
    given. You'll also provide the previous chat history if there is any so \
    answer to the last question asked.
    """

    query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")

    llm = HuggingFaceLLM(
        context_window=contect_window,
        max_new_tokens=max_new_token,
        generate_kwargs={"temperature": 0.0, "do_sample": False},
        system_prompt=system_prompt,
        query_wrapper_prompt=query_wrapper_prompt,
        tokenizer_name='meta-llama/Llama-3.2-1B-Instruct',
        model_name='meta-llama/Llama-3.2-1B-Instruct',
        device_map='auto',
        model_kwargs={"torch_dtype": torch.float16, "quantization_config": BitsAndBytesConfig(num_bits=8)}
    )

    embed_model = LangchainEmbedding(
        HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"))

    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.node_parser = SentenceSplitter(chunk_size=1024)
    settings = Settings

    return settings