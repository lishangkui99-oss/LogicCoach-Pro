import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# ================= 配置区域 =================
# 1. 自动下载并使用免费的 Embedding 模型 (all-MiniLM-L6-v2)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 2. 文件夹配置
DOCS_DIR = "knowledge_base"  # 你的 PDF/TXT 放在这里
DB_PATH = "chroma_db"        # 向量数据库生成在这个文件夹

def read_file(filepath):
    """读取 PDF 或 TXT 文件内容"""
    if filepath.endswith('.pdf'):
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
            return text
        except Exception as e:
            print(f"⚠️ 无法读取 PDF {filepath}: {e}")
            return ""
    else:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ 无法读取文本 {filepath}: {e}")
            return ""

def build_database():
    print("📚 [1/3] 正在初始化向量数据库...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # 每次重建前，先删除旧的数据集合，确保数据最新
    try: client.delete_collection("product_manager_knowledge")
    except: pass
    
    collection = client.create_collection(
        name="product_manager_knowledge",
        embedding_function=emb_fn
    )

    print(f"📂 [2/3] 正在扫描 '{DOCS_DIR}' 文件夹...")
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"❌ 错误：找不到文件夹，已自动创建空文件夹 '{DOCS_DIR}'，请放入文件后重试！")
        return

    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(('.pdf', '.txt', '.md'))]
    if not files:
        print("⚠️ 文件夹是空的！请至少放入一个 PDF 或 TXT 文件。")
        return

    documents = []
    metadatas = []
    ids = []

    print(f"   发现 {len(files)} 个文件，开始读取...")
    for idx, filename in enumerate(files):
        path = os.path.join(DOCS_DIR, filename)
        content = read_file(path)
        
        # 只有内容长度超过 50 个字符才存入，过滤空文件
        if len(content) > 50:
            documents.append(content)
            ids.append(f"doc_{idx}")
            metadatas.append({"source": filename})
            # 打印进度，每读取一个文件显示一次
            print(f"   -> 已加载: {filename}")
        else:
            print(f"   -> 跳过(内容太少): {filename}")

    if documents:
        print(f"🚀 [3/3] 正在将 {len(documents)} 篇文档转化为向量 (这可能需要几分钟)...")
        # 批量写入数据库
        batch_size = 20
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                ids=ids[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
        print(f"\n✅✅✅ 建库成功！数据库已保存在 '{DB_PATH}' 文件夹中。")
    else:
        print("❌ 未提取到有效内容，建库失败。")

if __name__ == "__main__":
    build_database()