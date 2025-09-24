import json
import os
from typing import List

from litellm import completion
from pydantic import BaseModel

os.environ["LM_STUDIO_API_BASE"] = "http://localhost:1234/v1"


class LocaleEntry(BaseModel):
    id: str
    context: str
    source: str
    target: str


class LocaleEntries(BaseModel):
    batch: List[LocaleEntry]


entries_to_translate = LocaleEntries(
    batch=[
        LocaleEntry(
            id="title",
            context="Title of the confirm action title",
            source="Confirm",
            target="",
        ),
        LocaleEntry(
            id="cancel",
            context="Label on the cancel button in a modal dialog",
            source="Cancel",
            target="",
        ),
        LocaleEntry(
            id="welcome_msg",
            context="Greeting shown on the home page",
            source="Welcome to our site!",
            target="",
        ),
        LocaleEntry(
            id="error_404",
            context="Message shown when a page is not found",
            source="Page not found.",
            target="",
        ),
        LocaleEntry(
            id="app.title",
            context="",
            source="My Application",
            target="",
        ),
        LocaleEntry(
            id="app.subtitle",
            context="",
            source="The best way to manage your tasks",
            target="",
        ),
        LocaleEntry(
            id="app.version",
            context="",
            source="Version 1.0.0",
            target="",
        ),
        LocaleEntry(
            id="app.build_date",
            context="",
            source="Build date: 2025-09-21",
            target="",
        ),
        LocaleEntry(
            id="greeting",
            context="Template for the user's name in English as 'first_name, last_name'",
            source="%1$s, %2$s",
            target="",
        ),
        LocaleEntry(
            id="share-email-button",
            context="Button user clicks to share a file through email. Make it similar in length to the enlish version.",
            source="Share by Email",
            target="",
        ),
    ]
)


class Translator:

    def __init__(self, model="lm_studio/microsoft/phi-4", prompt=""):
        self.model = model
        self.prompt = prompt
        self.prompt += (
            "Return **exactly** a JSON array that matches the following schema:\n\n"
        )
        self.prompt += f"{json.dumps(LocaleEntries.model_json_schema(), indent=2)}\n\n"

    def translate(self, entries: LocaleEntries):
        prompt = self.prompt
        prompt += "Entries to translate:\n"
        for entry in entries.batch:
            d = entry.model_dump_json(by_alias=True)
            prompt += f"- {d}\n"

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format=LocaleEntries,
            )

            response_content = response.choices[0].message.content
            translated_entries_dict = json.loads(response_content)
            translated_entries = LocaleEntries(**translated_entries_dict)

            print("✅ Translation batch completed!\n")
            print(translated_entries)
            print("\n\n")
            for entry in translated_entries.batch:
                print(f"{entry.id}: {entry.source}, {entry.target}")
                print("\n")

        except Exception as e:
            print(f"Error during translation: {e}")


english_to_japanese = (
    "You are a professional translator. Translate the following source (en-US) strings into culturaly appropriate target (ja-JP) strings."
    "Names in Japanese are last-name, first-name."
)

english_to_spanish: str = (
    "You are a professional translator. Translate the following source (en-US) strings into culturaly appropriate target (es-US) strings."
)


translator = Translator("lm_studio/microsoft/phi-4", english_to_spanish)
translator.translate(entries_to_translate)
