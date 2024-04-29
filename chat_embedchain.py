import os
import shutil
import tempfile
from string import Template
import streamlit as st
from dotenv import load_dotenv
from embedchain import App
from embedchain.models.data_type import DataType
import requests
import pafy


def create_yaml_from_template(
    db_path,
    openai_api_key,
    embedchain_api_key,
    template_path="gpt-3.5-turbo.template.yaml",
    output_path="gpt-3.5-turbo.yaml",
):
    # Leer la plantilla
    with open(template_path, "r") as file:
        src = Template(file.read())
        result = src.substitute(
            openai_api_key=openai_api_key,
            db_path=db_path,
            embedchain_api_key=embedchain_api_key,
        )

    # Escribir el archivo YAML final
    with open(output_path, "w") as file:
        file.write(result)
        return output_path


def embedchain_bot(db_path, openai_api_key, embedchain_api_key):
    print(
        f"embedchain_bot.\n db_path: {db_path}\n openai_api_key: {openai_api_key}\n embedchain_api_key: {embedchain_api_key}"
    )
    # Crear el archivo YAML con los valores reales
    output_path = create_yaml_from_template(
        db_path=db_path,
        openai_api_key=openai_api_key,
        embedchain_api_key=embedchain_api_key,
    )
    if output_path:
        try:
            # Cargar la configuración desde el nuevo archivo YAML
            return App().from_config(config_path=output_path)
        finally:
            shutil.rmtree(db_path, ignore_errors=True)


def display_history(history):
    if history:
        st.header("Conversation History")
        for i, (prompt, response) in enumerate(history):
            st.subheader(f"Prompt {i+1}")
            st.write(prompt)
            st.write(response)
            st.write("---")


def main():
    st.title = "Chat with the Embedchain AI Assistant"
    st.caption = (
        "This app uses the Embedchain library to provide an AI-powered chatbot."
    )
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embedchain_api_key = os.getenv("EMBEDCHAIN_API_KEY")
    openai_access_token = st.text_input(
        "Enter your openai_api_key API key:", type="password", value=openai_api_key
    )

    if openai_access_token and embedchain_api_key:
        db_path = tempfile.mkdtemp()
        app = embedchain_bot(db_path, openai_access_token, embedchain_api_key)
        # Get list of available LLM models from Embedchain (assuming a method exists)
        available_models = ["gpt-3.5-turbo", "text-davinci-003", "code-davinci-003"]

        selected_model = st.selectbox("Choose LLM Model:", available_models)

        # Initialize conversation history as an empty list
        conversation_history = []

        prompt = st.text_input("Enter a prompt for the AI assistant:", key="prompt")

        if st.button("Generate Response"):
            if prompt is not None and len(prompt.strip()) > 0:
                response = app.chat(prompt)
                # Append the new prompt and response to the history list
                conversation_history.append((prompt, response))
                st.write(response)
                st.success("Response generated!")
            else:
                st.warning("Please enter a prompt to get a response.")

        display_history(conversation_history)

    else:
        st.warning("Please enter a valid OpenAI API key.")

if __name__ == "__main__":
    load_dotenv()
    main()