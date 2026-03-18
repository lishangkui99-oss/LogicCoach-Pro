import io
import json
import os
import tempfile

import docx
import pdfplumber
from llama_parse import LlamaParse
from openai import OpenAI


def fallback_docx_extract(file_bytes: bytes) -> str:
    """Fallback parser for Word documents using python-docx."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        print(f"[document_processing] Word fallback failed: {e}")
        return ""


def fallback_pdfplumber_extract(file_bytes: bytes) -> str:
    """Fallback parser for PDFs using pdfplumber."""
    text_content = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
        return text_content
    except Exception as e:
        print(f"[document_processing] PDF fallback failed: {e}")
        return ""


def fallback_extract(file_bytes: bytes, filename: str) -> str:
    """Route fallback parsing by extension."""
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        return fallback_pdfplumber_extract(file_bytes)
    if ext in [".docx", ".doc"]:
        return fallback_docx_extract(file_bytes)
    if ext in [".png", ".jpg", ".jpeg"]:
        print("[document_processing] Image fallback OCR is not configured.")
        return ""
    return ""


async def extract_document_content(
    file_bytes: bytes,
    filename: str,
    llama_cloud_api_key: str | None,
) -> str:
    """Parse document via LlamaParse first, then local fallback."""
    ext = os.path.splitext(filename.lower())[1] or ".pdf"
    if not llama_cloud_api_key:
        return fallback_extract(file_bytes, filename)

    print(f"[document_processing] LlamaParse parsing: {filename}")
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        parser = LlamaParse(
            api_key=llama_cloud_api_key,
            result_type="markdown",
            language="ch_sim+en",
            verbose=False,
        )
        documents = await parser.aload_data(temp_file_path)
        markdown_content = "\n\n".join([doc.text for doc in documents])
        os.remove(temp_file_path)
        return markdown_content
    except Exception as e:
        print(f"[document_processing] LlamaParse failed, fallback used: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return fallback_extract(file_bytes, filename)


def extract_profile_json(
    ai_client: OpenAI,
    chat_model: str,
    text: str,
    doc_type: str = "resume",
) -> dict:
    """Extract structured profile JSON from resume/JD text."""
    if not text or len(text) < 10:
        return {}

    if doc_type == "resume":
        system_prompt = """
        你是一个专业的人力资源数据提取专家。
        请从提供的候选人简历文本中提取核心信息，并严格输出以下 JSON 结构：
        {
            "基本信息": {"姓名": "", "工作年限": ""},
            "核心技能栈": ["技能1", "技能2"],
            "工作经历摘要": [{"公司": "", "职位": "", "核心职责": ""}],
            "高价值项目经验": [{"项目名称": "", "业务价值或数据指标": ""}]
        }
        要求：未提及项填 null，绝不产生幻觉。
        """
    else:
        system_prompt = """
        你是一个专业的招聘专家。
        请从提供的岗位 JD (Job Description) 文本中提取核心要求，并严格输出以下 JSON 结构：
        {
            "岗位基础": {"职位名称": "", "经验要求": ""},
            "必须具备的硬技能": ["技能1", "技能2"],
            "核心业务职责": ["职责1", "职责2"]
        }
        要求：未提及项填 null，绝不产生幻觉。
        """

    try:
        response = ai_client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请提取以下文本：\n{text}"},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[document_processing] JSON extraction failed: {e}")
        return {}
