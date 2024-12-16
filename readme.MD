# Resume-Docs-Based-RAG-LLM

Resume-Docs-Based-RAG-LLM is a system combining Retrieval-Augmented Generation (RAG) with LLMs to extract, retrieve, and generate insights from resumes and documents. Ideal for HR and document analysis, it supports smart search, contextual responses, and seamless integration into workflows.

## Video

[![Watch the video](https://img.youtube.com/vi/pgW_L4qVdiM/maxresdefault.jpg)](https://youtu.be/pgW_L4qVdiM)

## Features

- **Document Analysis**: Extract insights from resumes and documents
- **Smart Search**: Retrieve relevant information quickly
- **Contextual Responses**: Generate responses based on context
- **Workflow Integration**: Seamlessly integrate into existing workflows

## Colab Notebook to run the server

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1IrSCU4nlVm8VFVSC98kJPXv98rFauwLR?usp=sharing)
- Replace the `HF_TOKEN` and `NGROK_AUTHTOKEN`
- Run the notebook and the server will be up and running
- <b>Copy the ngrok link and use it in the frontend</b>

## Installation

1. Clone the repository
```
git clone https://github.com/Priyanshu-hawk/Resume-Docs-Based-Rag-LLM
cd Resume-Docs-Based-Rag-LLM
```

2. Install the required packages
```
pip install -r requirements.txt
```

3. Run the application
```
streamlit run web.py
```

4. Open http://localhost:8501 in your browser

## Usage

1. Enter the ngrok link in the frontend
2. Upload a resume or document
3. Click enter to extract insights
4. View the extracted insights
5. Chat back and forth with the system