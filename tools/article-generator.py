#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律文章生成器
用於批量生成和管理法律文章
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List

class ArticleGenerator:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.template_path = os.path.join(base_dir, "templates", "article-template.html")
        self.articles_dir = os.path.join(base_dir, "articles")
        self.index_file = os.path.join(base_dir, "tools", "articles-index.json")

        # 文章分類配置
        self.categories = {
            "inheritance": {
                "name": "繼承法",
                "page": "legal-knowledge.html#inheritance",
                "subcategories": ["tax-planning", "registration", "disputes", "wills"]
            },
            "real-estate": {
                "name": "不動產法",
                "page": "legal-knowledge.html#real-estate",
                "subcategories": ["transactions", "mortgages", "disputes", "registration"]
            },
            "family-law": {
                "name": "家事法",
                "page": "legal-knowledge.html#family-law",
                "subcategories": ["divorce", "custody", "property", "support"]
            },
            "civil-law": {
                "name": "民事法",
                "page": "legal-knowledge.html#civil-law",
                "subcategories": ["contracts", "torts", "property", "obligations"]
            },
            "criminal-law": {
                "name": "刑事法",
                "page": "legal-knowledge.html#criminal-law",
                "subcategories": ["crimes", "procedures", "evidence", "penalties"]
            },
            "corporate-law": {
                "name": "公司法",
                "page": "legal-knowledge.html#corporate-law",
                "subcategories": ["formation", "governance", "securities", "mergers"]
            },
            "labor-law": {
                "name": "勞動法",
                "page": "legal-knowledge.html#labor-law",
                "subcategories": ["employment", "disputes", "benefits", "safety"]
            },
            "tax-law": {
                "name": "稅法",
                "page": "legal-knowledge.html#tax-law",
                "subcategories": ["income", "estate", "corporate", "international"]
            }
        }

        self.ensure_directories()

    def ensure_directories(self):
        """確保必要的目錄存在"""
        os.makedirs(os.path.join(self.base_dir, "templates"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "tools"), exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)

        for category in self.categories.keys():
            category_dir = os.path.join(self.articles_dir, category)
            os.makedirs(category_dir, exist_ok=True)

    def generate_filename(self, category: str, subcategory: str, title: str, date: str = None) -> str:
        """生成文章檔名"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")

        # 清理標題，移除特殊字符
        clean_title = re.sub(r'[^\w\s-]', '', title).strip()
        clean_title = re.sub(r'[-\s]+', '-', clean_title)

        return f"{category}-{subcategory}-{clean_title}-{date}.html"

    def create_article(self,
                      title: str,
                      category: str,
                      subcategory: str,
                      subtitle: str = "",
                      description: str = "",
                      keywords: List[str] = None,
                      table_of_contents: List[str] = None,
                      content: str = "",
                      related_articles: List[str] = None) -> str:
        """創建新文章"""

        if category not in self.categories:
            raise ValueError(f"Unknown category: {category}")

        if subcategory not in self.categories[category]["subcategories"]:
            raise ValueError(f"Unknown subcategory: {subcategory}")

        # 讀取模板
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # 生成檔名和日期
        today = datetime.now().strftime("%Y-%m-%d")
        filename = self.generate_filename(category, subcategory, title)

        # 準備替換內容
        replacements = {
            "{{ARTICLE_TITLE}}": title,
            "{{ARTICLE_DESCRIPTION}}": description or f"{title} - 專業律師為您詳細解析",
            "{{ARTICLE_KEYWORDS}}": ", ".join(keywords) if keywords else f"{title}, 法律, 律師, 法律諮詢",
            "{{ARTICLE_FILENAME}}": filename,
            "{{ARTICLE_SUBTITLE}}": subtitle or "專業律師為您詳細解析相關法律問題",
            "{{CATEGORY_NAME}}": self.categories[category]["name"],
            "{{CATEGORY_PAGE}}": self.categories[category]["page"],
            "{{PUBLISH_DATE}}": today,
            "{{MODIFIED_DATE}}": today,
            "{{TABLE_OF_CONTENTS}}": self.format_table_of_contents(table_of_contents),
            "{{ARTICLE_CONTENT}}": content or self.generate_default_content(title),
            "{{RELATED_ARTICLES}}": self.format_related_articles(related_articles)
        }

        # 執行替換
        article_html = template
        for placeholder, value in replacements.items():
            article_html = article_html.replace(placeholder, value)

        # 寫入檔案
        article_path = os.path.join(self.base_dir, filename)
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(article_html)

        # 更新索引
        self.update_index(filename, title, category, subcategory, today)

        return filename

    def format_table_of_contents(self, toc: List[str] = None) -> str:
        """格式化目錄"""
        if not toc:
            toc = ["法律概念說明", "相關法條解析", "實務案例分享", "常見問題解答", "專業建議"]

        html = ""
        for i, item in enumerate(toc, 1):
            html += f'''
                    <div class="flex items-start">
                        <span class="inline-flex items-center justify-center w-8 h-8 bg-accent-gold text-primary-dark rounded-full text-sm font-bold mr-3 flex-shrink-0">{i}</span>
                        <a href="#{item.replace(' ', '-').lower()}" class="text-primary-dark hover:text-accent-gold font-medium">{item}</a>
                    </div>'''
        return html

    def format_related_articles(self, articles: List[str] = None) -> str:
        """格式化相關文章"""
        if not articles:
            return '''
                <div class="bg-white p-6 shadow-sm border">
                    <h3 class="text-xl font-bold text-primary-dark mb-3">更多相關文章</h3>
                    <p class="text-gray-600">更多精彩內容即將推出...</p>
                </div>'''

        html = ""
        for article in articles[:3]:  # 限制3篇
            html += f'''
                <div class="bg-white p-6 shadow-sm border hover:shadow-md transition-shadow">
                    <h3 class="text-xl font-bold text-primary-dark mb-3">
                        <a href="{article['link']}" class="hover:text-accent-gold">{article['title']}</a>
                    </h3>
                    <p class="text-gray-600 mb-4">{article['description']}</p>
                    <a href="{article['link']}" class="text-accent-gold hover:text-yellow-600 font-medium">閱讀更多 →</a>
                </div>'''
        return html

    def generate_default_content(self, title: str) -> str:
        """生成預設內容結構"""
        return f'''
            <h2 id="法律概念說明">法律概念說明</h2>
            <p>關於{title}的基本法律概念和重要性...</p>

            <h2 id="相關法條解析">相關法條解析</h2>
            <p>相關的法律條文詳細解析...</p>

            <h2 id="實務案例分享">實務案例分享</h2>
            <p>實際案例分析和處理方式...</p>

            <h2 id="常見問題解答">常見問題解答</h2>
            <p>民眾最常遇到的問題和解答...</p>

            <h2 id="專業建議">專業建議</h2>
            <p>律師的專業建議和注意事項...</p>
        '''

    def update_index(self, filename: str, title: str, category: str, subcategory: str, date: str):
        """更新文章索引"""
        index_data = self.load_index()

        article_info = {
            "filename": filename,
            "title": title,
            "category": category,
            "subcategory": subcategory,
            "date": date,
            "url": f"https://lawyer880.com/{filename}"
        }

        index_data["articles"].append(article_info)
        index_data["total_articles"] = len(index_data["articles"])
        index_data["last_updated"] = datetime.now().isoformat()

        self.save_index(index_data)

    def load_index(self) -> Dict:
        """載入文章索引"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "articles": [],
                "total_articles": 0,
                "categories": self.categories,
                "last_updated": datetime.now().isoformat()
            }

    def save_index(self, data: Dict):
        """儲存文章索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update_sitemap(self):
        """更新sitemap.xml"""
        index_data = self.load_index()
        sitemap_path = os.path.join(self.base_dir, "sitemap.xml")

        # 讀取現有sitemap
        if os.path.exists(sitemap_path):
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_content = f.read()
        else:
            sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>'''

        # 生成新的文章URL項目
        new_urls = ""
        for article in index_data["articles"]:
            new_urls += f'''
  <url>
    <loc>{article['url']}</loc>
    <lastmod>{article['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>'''

        # 更新sitemap（這裡需要更複雜的邏輯來避免重複）
        # 簡化版本：重新生成整個sitemap

    def generate_batch_articles(self, articles_config: List[Dict]):
        """批量生成文章"""
        created_files = []
        for config in articles_config:
            try:
                filename = self.create_article(**config)
                created_files.append(filename)
                print(f"✓ Created: {filename}")
            except Exception as e:
                print(f"✗ Error creating {config.get('title', 'Unknown')}: {e}")

        return created_files

# 使用範例
if __name__ == "__main__":
    generator = ArticleGenerator()

    # 範例：創建單篇文章
    filename = generator.create_article(
        title="遺產稅申報期限與罰則",
        category="inheritance",
        subcategory="tax-planning",
        subtitle="錯過申報期限的嚴重後果與補救方式",
        description="詳細解析遺產稅申報的法定期限、逾期罰則，以及補救措施",
        keywords=["遺產稅", "申報期限", "罰則", "補救"],
        table_of_contents=["申報期限規定", "逾期罰則計算", "補救措施", "實務建議"]
    )

    print(f"Article created: {filename}")