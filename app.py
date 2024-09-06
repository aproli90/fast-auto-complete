import os

import gradio as gr
from groq import Groq
import datetime as DT
import pytz

from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

SYSTEM_PROMPT = """
You complete every sentence in a very interesting way. Use emojis wherever possible.
Preserve everything in the user prompt and append to it to complete the ongoing sentence.
Don't add additional sentences.

eg:
Q. What's my
A. What's my name? 🤔

Q. I love to eat
A. I love to eat eggs for breakfast! 🧦🍳

Q. The weather is
A. The weather is perfect for surfing! 🏄‍♀️

Q. My favorite hobby is
A. My favorite hobby is collecting playing cards! 🐰💨

Q. The meaning of life is
A. The meaning of life is to find what impact you can create in the life of others! 🍕🕵️‍♂️

Q. The weather is perfect for surfing! 🏄‍♀️ My favorite hobby is
A. The weather is perfect for surfing! 🏄‍♀️ My favorite hobby is collecting playing cards! 🐰💨

Q. I love to eat eggs for breakfast! 🧦🍳 Eggs are
A. I love to eat eggs for breakfast! 🧦🍳 Eggs are healthy as well as tasty 😋

"""

ipAddress = ""
lastResponse = ""


def __nowInIST():
    return DT.datetime.now(pytz.timezone("Asia/Kolkata"))


def __attachIp(request: gr.Request):
    global ipAddress
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        ipAddress = x_forwarded_for


def pprint(log: str):
    now = __nowInIST()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] [{ipAddress}] {log}")


def autocomplete(text):
    global lastResponse

    if text != "":
        if text[-1] != " ":
            yield lastResponse
            return

        pprint(f"{text=}")

        response = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.8,
            max_tokens=100,
            stream=True
        )

        partialMessage = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                partialMessage = partialMessage + chunk.choices[0].delta.content
                yield partialMessage
        pprint(f"{partialMessage=}")
        lastResponse = partialMessage
    else:
        lastResponse = ""


css = """
# .generating {
#     display: none
# }
"""

with gr.Blocks(css=css, title="Create interesting sentences on the fly ✈") as demo:
    demo.load(__attachIp, None, None)
    gr.Markdown("# Create interesting sentences on the fly ✈")
    gr.Markdown("Powered by Groq & Llama 3.1")

    with gr.Row():
        input_box = gr.Textbox(
            lines=2,
            placeholder="Start typing ...",
            label="Input Sentence",
        )
        output_box = gr.Markdown(
            label="Output Sentence"
        )

    copy_button = gr.Button("Use Output", variant="primary")

    input_box.change(
        fn=autocomplete,
        inputs=input_box,
        outputs=output_box,
        show_progress="minimal",
        api_name=None,
        queue=True,
    )

    copy_button.click(
        fn=lambda x: x,
        inputs=output_box,
        outputs=input_box,
    )


# inputBox = gr.Textbox(
#     lines=2,
#     placeholder="Start typing ...",
#     label="Input Sentence",
# )
# outputBox = gr.Markdown(
#     label="Output Sentence"
# )

# with gr.Interface(
#     fn=autocomplete,
#     inputs=inputBox,
#     outputs=outputBox,
#     title="Create interesting sentences on the fly ✈",
#     description="Powered by Groq & Llama 3.1",
#     live=True,  # Set live to True for real-time feedback
#     allow_flagging="never",  # Disable flagging
#     css=css
# ) as demo:
#     # demo.load(__attachIp, None, None)
#     copyButton = gr.Button(
#         "Use Output",
#         elem_id="copy-button",
#         variant="primary"
#     ).click(
#         fn=lambda x: x,
#         inputs=outputBox,
#         outputs=inputBox,
#     )

# Launch the app
demo.launch(
    debug=True,
    server_name="0.0.0.0",
)
