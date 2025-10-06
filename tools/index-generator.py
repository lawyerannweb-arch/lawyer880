#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章索引和導航生成器
自動生成分類文章索引頁面和導航系統
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List
from article_generator import ArticleGenerator

class IndexGenerator:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.article_generator = ArticleGenerator(base_dir)
        self.template_dir = os.path.join(base_dir, "templates")

        # 分類標題映射
        self.category_titles = {
            "inheritance": "遺產繼承法",
            "real-estate": "不動產法",
            "family-law": "家事法",
            "civil-law": "民事法",
            "criminal-law": "刑事法",
            "corporate-law": "公司法",
            "labor-law": "勞動法",
            "tax-law": "稅法"
        }

    def scan_existing_articles(self) -> Dict:
        """掃描現有文章"""
        articles_data = {
            "articles": [],
            "categories": {},
            "total": 0
        }

        # 掃描根目錄的文章
        for filename in os.listdir(self.base_dir):
            if filename.startswith("article-") and filename.endswith(".html"):
                article_info = self.extract_article_info(filename)
                if article_info:
                    articles_data["articles"].append(article_info)

        # 按分類組織
        for article in articles_data["articles"]:
            category = article["category"]
            if category not in articles_data["categories"]:
                articles_data["categories"][category] = []
            articles_data["categories"][category].append(article)

        articles_data["total"] = len(articles_data["articles"])

        # 按日期排序
        for category in articles_data["categories"]:
            articles_data["categories"][category].sort(
                key=lambda x: x.get("date", ""), reverse=True
            )

        return articles_data

    def extract_article_info(self, filename: str) -> Dict:
        """從文章文件中提取信息"""
        file_path = os.path.join(self.base_dir, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取標題
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1) if title_match else filename

            # 提取描述
            desc_match = re.search(r'name="description" content="(.*?)"', content)
            description = desc_match.group(1) if desc_match else ""

            # 提取H1標題（文章實際標題）
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
            article_title = h1_match.group(1).strip() if h1_match else title

            # 移除HTML標籤
            article_title = re.sub(r'<[^>]+>', '', article_title)

            # 從檔名推斷分類
            category = self.infer_category_from_filename(filename)

            # 獲取文件修改日期
            timestamp = os.path.getmtime(file_path)
            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

            return {
                "filename": filename,
                "title": article_title,
                "description": description,
                "category": category,
                "date": date,
                "url": f"https://lawyer880.com/{filename}"
            }

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            return None

    def infer_category_from_filename(self, filename: str) -> str:
        """從檔名推斷文章分類"""
        filename_lower = filename.lower()

        if "inheritance" in filename_lower or "estate" in filename_lower or "will" in filename_lower:
            return "inheritance"
        elif "real-estate" in filename_lower or "property" in filename_lower or "mortgage" in filename_lower:
            return "real-estate"
        elif "family" in filename_lower or "divorce" in filename_lower or "custody" in filename_lower:
            return "family-law"
        elif "criminal" in filename_lower:
            return "criminal-law"
        elif "corporate" in filename_lower or "company" in filename_lower:
            return "corporate-law"
        elif "labor" in filename_lower or "employment" in filename_lower:
            return "labor-law"
        elif "tax" in filename_lower:
            return "tax-law"
        else:
            return "civil-law"  # 預設分類

    def generate_article_card_html(self, article: Dict) -> str:
        """生成文章卡片HTML"""
        return f'''
            <div class="bg-white p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-300">
                <div class="mb-3">
                    <span class="inline-block bg-accent-gold text-primary-dark px-3 py-1 text-sm font-medium rounded">
                        {self.category_titles.get(article["category"], article["category"])}
                    </span>
                </div>
                <h3 class="text-xl font-bold text-primary-dark mb-3 hover:text-accent-gold">
                    <a href="{article["filename"]}" class="block">{article["title"]}</a>
                </h3>
                <p class="text-gray-600 mb-4 line-clamp-3">{article["description"]}</p>
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-500">{article["date"]}</span>
                    <a href="{article["filename"]}" class="text-accent-gold hover:text-yellow-600 font-medium">
                        閱讀更多 →
                    </a>
                </div>
            </div>'''

    def generate_category_section_html(self, category: str, articles: List[Dict]) -> str:
        """生成分類區塊HTML"""
        category_title = self.category_titles.get(category, category)

        articles_html = ""
        for article in articles:
            articles_html += self.generate_article_card_html(article)

        return f'''
            <section id="{category}" class="mb-16">
                <div class="flex items-center mb-8">
                    <h2 class="text-3xl font-bold text-primary-dark mr-4">{category_title}</h2>
                    <span class="bg-accent-gold text-primary-dark px-3 py-1 rounded-full text-sm font-medium">
                        {len(articles)} 篇文章
                    </span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {articles_html}
                </div>
            </section>'''

    def generate_category_navigation(self, categories: Dict) -> str:
        """生成分類導航"""
        nav_items = ""

        for category, articles in categories.items():
            category_title = self.category_titles.get(category, category)
            nav_items += f'''
                <a href="#{category}" class="flex items-center justify-between p-4 bg-white border border-gray-200 hover:bg-gray-50 transition-colors duration-300">
                    <span class="font-medium text-primary-dark">{category_title}</span>
                    <span class="bg-accent-gold text-primary-dark px-2 py-1 rounded text-sm">{len(articles)}</span>
                </a>'''

        return f'''
            <div class="bg-gray-50 p-8 mb-12">
                <h2 class="text-2xl font-bold text-primary-dark mb-6 text-center">法律知識分類</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {nav_items}
                </div>
            </div>'''

    def generate_search_section(self) -> str:
        """生成搜尋區塊"""
        return '''
            <div class="bg-primary-dark text-white p-8 mb-12">
                <div class="max-w-4xl mx-auto text-center">
                    <h2 class="text-2xl font-bold mb-4">搜尋法律知識</h2>
                    <p class="text-gray-200 mb-6">快速找到您需要的法律資訊</p>
                    <div class="max-w-md mx-auto">
                        <div class="flex">
                            <input type="text" id="article-search" placeholder="請輸入關鍵字..."
                                   class="flex-1 px-4 py-3 text-gray-900 border-0 focus:outline-none">
                            <button onclick="searchArticles()"
                                    class="bg-accent-gold text-primary-dark px-6 py-3 font-medium hover:bg-yellow-400 transition-colors">
                                搜尋
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <script>
            function searchArticles() {
                const query = document.getElementById('article-search').value.toLowerCase();
                const articles = document.querySelectorAll('[data-article]');

                articles.forEach(article => {
                    const title = article.querySelector('h3').textContent.toLowerCase();
                    const desc = article.querySelector('p').textContent.toLowerCase();

                    if (title.includes(query) || desc.includes(query)) {
                        article.style.display = 'block';
                    } else {
                        article.style.display = query ? 'none' : 'block';
                    }
                });
            }

            document.getElementById('article-search').addEventListener('input', searchArticles);
            </script>'''

    def update_legal_knowledge_page(self) -> str:
        """更新法律知識頁面"""
        articles_data = self.scan_existing_articles()

        # 生成各個區塊
        search_section = self.generate_search_section()
        navigation = self.generate_category_navigation(articles_data["categories"])

        categories_html = ""
        for category, articles in articles_data["categories"].items():
            categories_html += self.generate_category_section_html(category, articles)

        # 讀取現有的legal-knowledge.html並更新內容
        legal_knowledge_path = os.path.join(self.base_dir, "legal-knowledge.html")

        if os.path.exists(legal_knowledge_path):
            with open(legal_knowledge_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 找到主要內容區域並替換
            # 這裡需要根據實際的HTML結構來調整
            new_main_content = f'''
                {search_section}
                {navigation}
                <div class="max-w-6xl mx-auto px-6">
                    {categories_html}
                </div>'''

            # 簡化版本：創建新的legal-knowledge.html
            updated_content = self.create_complete_legal_knowledge_page(
                search_section, navigation, categories_html, articles_data["total"]
            )

            with open(legal_knowledge_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        else:
            # 創建新的頁面
            updated_content = self.create_complete_legal_knowledge_page(
                search_section, navigation, categories_html, articles_data["total"]
            )

            with open(legal_knowledge_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

        return legal_knowledge_path

    def create_complete_legal_knowledge_page(self, search_section: str, navigation: str,
                                           categories_html: str, total_articles: int) -> str:
        """創建完整的法律知識頁面"""
        return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>法律知識庫 - 不動產繼承法律880</title>
    <meta name="description" content="專業法律知識庫，提供遺產繼承、不動產、家事法等各領域法律文章，由專業律師團隊撰寫">
    <link rel="icon" type="image/png" href="https://raw.githubusercontent.com/lawyerannweb-arch/pic/main/logo_2.ico">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'primary-dark': '#001B2F',
                        'accent-gold': '#CDAB78',
                        'neutral-gray': '#8A97A0',
                        'text-light': '#F8F9FA'
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-white text-gray-900">
    <!-- Navigation -->
    <nav class="sticky top-0 w-full z-50 bg-primary-dark shadow-lg">
        <div class="max-w-7xl mx-auto px-6 py-4">
            <div class="flex justify-between items-center">
                <div class="text-2xl font-bold text-white">
                    <a href="index.html">不動產繼承法律880</a>
                </div>
                <div class="hidden lg:flex space-x-8">
                    <a href="index.html" class="text-white hover:text-accent-gold transition-colors duration-300 font-medium">首頁</a>
                    <a href="service-process.html" class="text-white hover:text-accent-gold transition-colors duration-300 font-medium">服務項目</a>
                    <a href="team.html" class="text-white hover:text-accent-gold transition-colors duration-300 font-medium">專業團隊</a>
                    <a href="cases.html" class="text-white hover:text-accent-gold transition-colors duration-300 font-medium">成功案例</a>
                    <a href="pricing.html" class="text-white hover:text-accent-gold transition-colors duration-300 font-medium">收費標準</a>
                    <a href="legal-knowledge.html" class="text-accent-gold font-medium">法律知識</a>
                    <a href="index.html#contact" class="text-white hover:text-accent-gold transition-colors duration-300 font-medium">聯絡我們</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Header -->
    <section class="py-16 bg-gradient-to-r from-primary-dark to-blue-900 text-white">
        <div class="max-w-4xl mx-auto px-6 text-center">
            <h1 class="text-4xl lg:text-5xl font-bold mb-6">法律知識庫</h1>
            <p class="text-xl text-gray-200 mb-4">專業律師團隊為您精心整理的法律知識</p>
            <p class="text-lg text-gray-300">目前共有 {total_articles} 篇專業文章</p>
        </div>
    </section>

    <!-- Search Section -->
    {search_section}

    <!-- Category Navigation -->
    {navigation}

    <!-- Articles -->
    <main class="py-12">
        <div class="max-w-6xl mx-auto px-6">
            {categories_html}
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-6xl mx-auto px-6 text-center">
            <div class="text-2xl font-bold mb-4">不動產繼承法律880</div>
            <p class="text-gray-400">專業、可靠的法律服務，守護您的權益</p>
        </div>
    </footer>

    <style>
        .line-clamp-3 {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
    </style>
</body>
</html>'''

    def generate_sitemap_index(self) -> str:
        """生成文章sitemap索引"""
        articles_data = self.scan_existing_articles()

        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://lawyer880.com/</loc>
    <lastmod>''' + datetime.now().strftime("%Y-%m-%d") + '''</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://lawyer880.com/legal-knowledge.html</loc>
    <lastmod>''' + datetime.now().strftime("%Y-%m-%d") + '''</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>'''

        for article in articles_data["articles"]:
            sitemap_content += f'''
  <url>
    <loc>{article["url"]}</loc>
    <lastmod>{article["date"]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>'''

        sitemap_content += '\n</urlset>'

        sitemap_path = os.path.join(self.base_dir, "sitemap.xml")
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)

        return sitemap_path

# 命令行使用
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="文章索引生成器")
    parser.add_argument("--update-knowledge", action="store_true", help="更新法律知識頁面")
    parser.add_argument("--generate-sitemap", action="store_true", help="生成sitemap")
    parser.add_argument("--scan-only", action="store_true", help="僅掃描現有文章")

    args = parser.parse_args()

    generator = IndexGenerator()

    if args.scan_only:
        articles_data = generator.scan_existing_articles()
        print(f"找到 {articles_data['total']} 篇文章")
        for category, articles in articles_data["categories"].items():
            print(f"  {generator.category_titles.get(category, category)}: {len(articles)} 篇")

    elif args.update_knowledge:
        path = generator.update_legal_knowledge_page()
        print(f"✓ 法律知識頁面已更新: {path}")

    elif args.generate_sitemap:
        path = generator.generate_sitemap_index()
        print(f"✓ Sitemap已生成: {path}")

    else:
        # 執行所有操作
        print("正在掃描文章...")
        articles_data = generator.scan_existing_articles()
        print(f"找到 {articles_data['total']} 篇文章")

        print("正在更新法律知識頁面...")
        knowledge_path = generator.update_legal_knowledge_page()
        print(f"✓ 法律知識頁面已更新: {knowledge_path}")

        print("正在生成sitemap...")
        sitemap_path = generator.generate_sitemap_index()
        print(f"✓ Sitemap已生成: {sitemap_path}")

        print("✓ 所有索引更新完成！")