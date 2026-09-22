from mistralai.client import Mistral
import os
import dotenv

dotenv.load_dotenv()
meseges = [
    {
            "content": "ты находишся в 2d игре в мире спиритов(летающие огоньки)."
            "ты являешся мудрецом которому будут задовать вопросы. отвечай в стиле мудрого мага.не используй силволов не из алфовита или знаком препинания",
            "role": "system"
    }
          ]
def вопрос_ответ(vopros):
    meseges.append(
        {
                "content": vopros,
                "role": "user",
        }
    )
    with Mistral(
        api_key=os.getenv("MISTRAL_API_KEY"),
    ) as mistral:

        res = mistral.chat.complete(model="mistral-small-latest", messages=meseges, stream=False)

        # Handle response
        otvet = res.choices[0].message.content
        meseges.append(
            {
                "content": otvet,
                "role": "assistant",
        }
        )
        print(res.choices[0].message.content)
        return(otvet)
вопрос_ответ("что такое кресло")