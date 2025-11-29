from openai import OpenAI, OpenAIError

output = ""
def runAi(prompt, apiKey):
    global output
    try:
        client = OpenAI(
            api_key=apiKey, # Api Key
            base_url="https://api.groq.com/openai/v1" # AI Model Base URL
        )   # Defining Client for Hola.


        response = client.responses.create(
            model="openai/gpt-oss-20b", # Selecting the ai model.
            input=[
                {
                    "role": "system",   
                    "content": (
                        "You are Hola, a human-like personal assistant. Keep your replies short, natural, and friendly, Don't reply with long texts."                        
                    )       # Hola Role and rules.
                },
                {
                    "role": "user",
                    "content": prompt       # User Prompts.
                }
            ]
        )

        output = response.output_text
        return output   # Returing the output.

    except OpenAIError as e:    # Catching Errors.
        output = f"[Error]: {e}"
        return output