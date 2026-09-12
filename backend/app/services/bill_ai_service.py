import json

from google import genai
from google.genai import types

from app.core.ai_config import (
    AI_API_KEY,
    AI_MODEL,
)


class BillAIService:

    def __init__(self):
        self.client = genai.Client(
            api_key=AI_API_KEY
        )

    async def extract_bill(
        self,
        image_bytes: bytes,
        content_type: str,
    ) -> dict:

        prompt = """
You are a highly accurate financial bill extraction
assistant.

Analyze the provided restaurant/shop bill image.

Extract ONLY information that is actually visible
on the bill.

Do not invent missing information.

Return the following JSON structure:

{
  "merchant_name": string or null,
  "bill_date": string or null,
  "subtotal": number or null,
  "tax": number or null,
  "discount": number or null,
  "total": number or null,
  "items": [
    {
      "name": string,
      "quantity": number,
      "unit_price": number,
      "total_price": number
    }
  ],
  "confidence": number between 0 and 1,
  "warnings": [
    string
  ]
}

Important rules:

1. Read the final payable total carefully.
2. Do not guess unreadable numbers.
3. If something is unclear, put null and add a warning.
4. Preserve item quantities.
5. Calculate item totals only when the bill provides
   enough information.
6. confidence must represent your confidence in the
   extracted financial information.
7. If the image is not a bill, return low confidence
   and explain it in warnings.
"""

        response = await self.client.aio.models.generate_content(
            model=AI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=content_type,
                ),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema={
                    "type": "object",
                    "properties": {
                        "merchant_name": {
                            "type": [
                                "string",
                                "null",
                            ]
                        },
                        "bill_date": {
                            "type": [
                                "string",
                                "null",
                            ]
                        },
                        "subtotal": {
                            "type": [
                                "number",
                                "null",
                            ]
                        },
                        "tax": {
                            "type": [
                                "number",
                                "null",
                            ]
                        },
                        "discount": {
                            "type": [
                                "number",
                                "null",
                            ]
                        },
                        "total": {
                            "type": [
                                "number",
                                "null",
                            ]
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "quantity": {
                                        "type": "number"
                                    },
                                    "unit_price": {
                                        "type": "number"
                                    },
                                    "total_price": {
                                        "type": "number"
                                    },
                                },
                                "required": [
                                    "name",
                                    "quantity",
                                    "unit_price",
                                    "total_price",
                                ],
                            },
                        },
                        "confidence": {
                            "type": "number"
                        },
                        "warnings": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                        },
                    },
                    "required": [
                        "merchant_name",
                        "bill_date",
                        "subtotal",
                        "tax",
                        "discount",
                        "total",
                        "items",
                        "confidence",
                        "warnings",
                    ],
                },
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        try:
            return json.loads(
                response.text
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from exc