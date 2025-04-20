from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentProcessor:

    def __init__(self, sourcre_path: str):
        self.sourcre_path = sourcre_path

    def load_document(self) -> list[str]:
        with open(self.sourcre_path, "r") as file:
            document = file.read()
        splitted = self._split_document(document)
        return splitted

    def _split_document(self, document: str) -> list[str]:
        spliter = RecursiveCharacterTextSplitter(
            separators=["# ", "## ", "### ", "///Separator///"]
        )
        documents = spliter.split_text(document)
        return documents
