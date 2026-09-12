class BillOCRService:

    async def extract_text(
        self,
        image_bytes: bytes,
        content_type: str,
    ) -> str:

        """
        OCR provider will be connected here.

        Keep this method independent from
        the rest of the application so we can
        replace the OCR provider later.
        """

        raise NotImplementedError(
            "OCR provider is not configured yet."
        )