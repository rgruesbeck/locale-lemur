# ---------------------------------------------------------------
#  Batch locale translation: id + context + source + target
# ---------------------------------------------------------------

from typing import List

from litellm import completion
from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# 1️⃣  Pydantic model – represents one locale entry
# ------------------------------------------------------------------


class LocaleEntry(BaseModel):
    id: str = Field(..., description="Unique key used in your code")
    context: str = Field(
        ...,
        description=(
            "Short note that explains the purpose of this string "
            "(helps the LLM choose the right translation)"
        ),
    )
    en_US: str = Field(..., alias="en-US", description="English source")
    es_MX: str = Field("", alias="es-MX", description="Mexican Spanish target")

    class Config:
        # Allow the model to read/write using the aliases (`en-US`, `es-MX`)
        allow_population_by_field_name = True
        # When dumping to JSON, keep the aliases (so output matches the prompt)
        use_enum_values = True


# ------------------------------------------------------------------
# 2️⃣  Build a batch of entries (the ones you want translated)
# ------------------------------------------------------------------

entries_to_translate: List[LocaleEntry] = [
    LocaleEntry(
        id="title", context="Title of the confirm action title", en_US="Confirm"
    ),
    LocaleEntry(
        id="cancel",
        context="Label on the cancel button in a modal dialog",
        en_US="Cancel",
    ),
    LocaleEntry(
        id="welcome_msg",
        context="Greeting shown on the home page",
        en_US="Welcome to our site!",
    ),
    LocaleEntry(
        id="error_404",
        context="Message shown when a page is not found",
        en_US="Page not found.",
    ),
]

# ------------------------------------------------------------------
# 3️⃣  Build the prompt
# ------------------------------------------------------------------

prompt = (
    "You are a professional translator. Translate the following English strings "
    "(en-US) into Mexican Spanish (es-MX). Return **exactly** a JSON array that "
    "matches the following schema:\n\n"
)

# Show the target schema so the model knows what to output
prompt += f"{LocaleEntry.schema_json(indent=2)}\n\n"

# Show the list of entries – note that we keep the `es-MX` field empty
prompt += "Entries to translate:\n"
for entry in entries_to_translate:
    # Convert each entry to a dict using the alias names
    d = entry.dict(by_alias=True)
    prompt += f"- {d}\n"

# ------------------------------------------------------------------
# 4️⃣  Call the LLM via Litellm
# ------------------------------------------------------------------

response = completion(
    model="lm_studio/llama-3-8b-instruct",  # choose your own model
    messages=[{"role": "user", "content": prompt}],
    response_format=List[LocaleEntry],  # Litellm will parse into this list
)

# ------------------------------------------------------------------
# 5️⃣  Parsed result – a list of LocaleEntry objects with es-MX filled
# ------------------------------------------------------------------

translated_entries: List[LocaleEntry] = response.choices[0].message.content

print("✅ Translation batch completed!\n")
for e in translated_entries:
    print(f"id      : {e.id}")
    print(f"context : {e.context}")
    print(f"en-US   : {e.en_US}")
    print(f"es-MX   : {e.es_MX}\n---")
