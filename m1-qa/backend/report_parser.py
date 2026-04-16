"""
M1-QA 投研问答助手 — 研报文本提取模块
支持 PDF（pdfplumber）、DOCX（python-docx）格式
"""


def extract_text_from_pdf(file_path: str) -> tuple:
    """
    从 PDF 文件提取文本内容及元数据。
    返回: (文本内容: str, 元数据: dict)
    元数据包含: pages（页数）、author（作者）
    """
    import pdfplumber

    text_parts = []
    metadata = {"pages": 0, "author": None}

    with pdfplumber.open(file_path) as pdf:
        metadata["pages"] = len(pdf.pages)
        # 尝试从 PDF 元数据中提取作者
        if pdf.metadata:
            metadata["author"] = pdf.metadata.get("Author") or pdf.metadata.get("author")
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)

    return "\n\n".join(text_parts), metadata


def extract_text_from_docx(file_path: str) -> tuple:
    """
    从 DOCX 文件提取文本内容及元数据。
    返回: (文本内容: str, 元数据: dict)
    元数据包含: pages（None，DOCX 不支持精确页数）、author（作者）
    """
    from docx import Document

    doc = Document(file_path)
    text_parts = []
    # 尝试从文档核心属性中提取作者
    try:
        author = doc.core_properties.author or None
    except Exception:
        author = None
    metadata = {"pages": None, "author": author}

    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)

    return "\n\n".join(text_parts), metadata


def extract_text(file_path: str, file_type: str) -> tuple:
    """
    统一入口：根据文件类型调用对应提取器。
    返回: (文本内容: str, 元数据: dict)
    抛出: ValueError（不支持的类型）、Exception（解析失败）
    """
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")
