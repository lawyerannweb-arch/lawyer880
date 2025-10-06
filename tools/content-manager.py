#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
內容管理系統
集成文章生成、管理、SEO優化的綜合工具
"""

import os
import json
import csv
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from article_generator import ArticleGenerator
from sitemap_generator import SitemapGenerator

class ContentManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.article_generator = ArticleGenerator(base_dir)
        self.sitemap_generator = SitemapGenerator(base_dir)
        self.config_file = os.path.join(base_dir, "tools", "content-config.json")
        self.load_config()

    def load_config(self):
        """載入配置文件"""
        default_config = {
            "seo": {
                "default_keywords": ["法律", "律師", "法律諮詢", "不動產", "繼承"],
                "title_suffix": " - 不動產繼承法律880",
                "description_template": "專業律師為您詳細解析{topic}相關法律問題，提供完整的法律諮詢服務。"
            },
            "content": {
                "default_sections": [
                    "法律概念說明",
                    "相關法條解析",
                    "實務案例分享",
                    "常見問題解答",
                    "專業建議"
                ],
                "article_length_target": 2000,
                "reading_time_target": 8
            },
            "automation": {
                "auto_update_sitemap": True,
                "auto_backup": True,
                "generate_social_meta": True
            }
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """儲存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def create_article_from_template(self,
                                   title: str,
                                   category: str,
                                   subcategory: str,
                                   **kwargs) -> str:
        """使用模板創建文章"""

        # 自動生成SEO元素
        seo_title = title + self.config["seo"]["title_suffix"]
        description = self.config["seo"]["description_template"].format(topic=title)
        keywords = self.config["seo"]["default_keywords"] + kwargs.get("keywords", [])

        # 創建文章
        filename = self.article_generator.create_article(
            title=title,
            category=category,
            subcategory=subcategory,
            description=description,
            keywords=keywords,
            table_of_contents=kwargs.get("table_of_contents", self.config["content"]["default_sections"]),
            **kwargs
        )

        # 自動更新sitemap
        if self.config["automation"]["auto_update_sitemap"]:
            self.update_sitemap()

        return filename

    def batch_create_from_csv(self, csv_file: str) -> List[str]:
        """從CSV文件批量創建文章"""
        created_files = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    filename = self.create_article_from_template(**row)
                    created_files.append(filename)
                    print(f"✓ Created: {filename}")
                except Exception as e:
                    print(f"✗ Error creating {row.get('title', 'Unknown')}: {e}")

        return created_files

    def update_sitemap(self):
        """更新sitemap"""
        try:
            self.sitemap_generator.generate_sitemap()
            self.sitemap_generator.update_robots_txt()
            print("✓ Sitemap updated successfully")
        except Exception as e:
            print(f"✗ Error updating sitemap: {e}")

    def generate_content_report(self) -> Dict:
        """生成內容報告"""
        index_data = self.article_generator.load_index()

        report = {
            "generation_time": datetime.now().isoformat(),
            "statistics": {
                "total_articles": len(index_data.get("articles", [])),
                "categories": {},
                "recent_articles": []
            },
            "seo": {
                "sitemap_status": "unknown",
                "robots_txt_status": "unknown"
            },
            "recommendations": []
        }

        # 統計分類文章數量
        for article in index_data.get("articles", []):
            category = article.get("category", "unknown")
            if category not in report["statistics"]["categories"]:
                report["statistics"]["categories"][category] = 0
            report["statistics"]["categories"][category] += 1

        # 最近文章
        articles = sorted(
            index_data.get("articles", []),
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        report["statistics"]["recent_articles"] = articles[:10]

        # SEO檢查
        sitemap_path = os.path.join(self.base_dir, "sitemap.xml")
        robots_path = os.path.join(self.base_dir, "robots.txt")

        report["seo"]["sitemap_status"] = "exists" if os.path.exists(sitemap_path) else "missing"
        report["seo"]["robots_txt_status"] = "exists" if os.path.exists(robots_path) else "missing"

        # 生成建議
        if report["statistics"]["total_articles"] < 50:
            report["recommendations"].append("考慮增加更多文章內容以提升SEO排名")

        if report["seo"]["sitemap_status"] == "missing":
            report["recommendations"].append("缺少sitemap.xml文件，建議立即生成")

        # 檢查分類平衡
        categories = report["statistics"]["categories"]
        if categories:
            max_count = max(categories.values())
            min_count = min(categories.values())
            if max_count > min_count * 3:
                report["recommendations"].append("文章分類分布不均，建議平衡各類別內容")

        return report

    def optimize_article_seo(self, filename: str) -> Dict:
        """優化單篇文章SEO"""
        file_path = os.path.join(self.base_dir, filename)

        if not os.path.exists(file_path):
            return {"error": f"File not found: {filename}"}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            optimization_report = {
                "filename": filename,
                "checks": {},
                "suggestions": []
            }

            # 檢查title標籤
            if "<title>" in content and "</title>" in content:
                title = content.split("<title>")[1].split("</title>")[0]
                optimization_report["checks"]["title_length"] = len(title)
                if len(title) > 60:
                    optimization_report["suggestions"].append("標題過長，建議控制在60字以內")
            else:
                optimization_report["suggestions"].append("缺少title標籤")

            # 檢查meta description
            if 'name="description"' in content:
                desc_start = content.find('name="description" content="') + 29
                desc_end = content.find('"', desc_start)
                description = content[desc_start:desc_end] if desc_end > desc_start else ""
                optimization_report["checks"]["description_length"] = len(description)
                if len(description) > 160:
                    optimization_report["suggestions"].append("描述過長，建議控制在160字以內")
            else:
                optimization_report["suggestions"].append("缺少meta description")

            # 檢查h1標籤
            h1_count = content.count("<h1")
            optimization_report["checks"]["h1_count"] = h1_count
            if h1_count != 1:
                optimization_report["suggestions"].append(f"h1標籤數量異常({h1_count})，建議每頁只有一個h1")

            # 檢查內部連結
            internal_links = content.count('href="legal-knowledge.html"') + content.count('href="index.html"')
            optimization_report["checks"]["internal_links"] = internal_links
            if internal_links < 3:
                optimization_report["suggestions"].append("內部連結過少，建議增加相關頁面連結")

            return optimization_report

        except Exception as e:
            return {"error": f"Error analyzing {filename}: {e}"}

    def backup_content(self, backup_dir: str = "backups") -> str:
        """備份所有內容"""
        import shutil
        import zipfile

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"content_backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)

        os.makedirs(backup_dir, exist_ok=True)

        # 創建備份目錄
        os.makedirs(backup_path, exist_ok=True)

        # 備份HTML文件
        for file in os.listdir(self.base_dir):
            if file.endswith('.html'):
                shutil.copy2(os.path.join(self.base_dir, file), backup_path)

        # 備份tools和templates目錄
        for dir_name in ['tools', 'templates']:
            src_dir = os.path.join(self.base_dir, dir_name)
            if os.path.exists(src_dir):
                dst_dir = os.path.join(backup_path, dir_name)
                shutil.copytree(src_dir, dst_dir)

        # 創建ZIP文件
        zip_path = f"{backup_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)

        # 刪除臨時目錄
        shutil.rmtree(backup_path)

        return zip_path

    def suggest_content_ideas(self, category: str = None) -> List[Dict]:
        """建議內容創作靈感"""

        content_ideas = {
            "inheritance": [
                {"title": "遺產稅申報完全攻略", "difficulty": "中級", "target_audience": "一般民眾"},
                {"title": "拋棄繼承vs限定繼承：選擇策略分析", "difficulty": "進階", "target_audience": "有債務考量者"},
                {"title": "遺囑效力爭議案例解析", "difficulty": "專業", "target_audience": "法律從業者"},
                {"title": "數位遺產繼承新趨勢", "difficulty": "初級", "target_audience": "年輕世代"},
                {"title": "跨國遺產繼承實務指南", "difficulty": "專業", "target_audience": "海外資產持有者"}
            ],
            "real-estate": [
                {"title": "預售屋契約陷阱解析", "difficulty": "中級", "target_audience": "首購族"},
                {"title": "不動產投資稅務規劃", "difficulty": "進階", "target_audience": "投資人"},
                {"title": "社區管理委員會法律問題", "difficulty": "中級", "target_audience": "住戶"},
                {"title": "都更權益保障指南", "difficulty": "進階", "target_audience": "都更戶"},
                {"title": "租賃新法重點解析", "difficulty": "初級", "target_audience": "房東房客"}
            ],
            "family-law": [
                {"title": "離婚財產分配實務", "difficulty": "中級", "target_audience": "離婚當事人"},
                {"title": "子女監護權爭取策略", "difficulty": "進階", "target_audience": "父母"},
                {"title": "家暴保護令申請流程", "difficulty": "初級", "target_audience": "受害者"},
                {"title": "收養程序完整指南", "difficulty": "中級", "target_audience": "收養家庭"},
                {"title": "夫妻財產制選擇建議", "difficulty": "初級", "target_audience": "新婚夫妻"}
            ]
        }

        if category and category in content_ideas:
            return content_ideas[category]

        # 返回所有分類的前3個建議
        all_ideas = []
        for cat, ideas in content_ideas.items():
            all_ideas.extend([{**idea, "category": cat} for idea in ideas[:3]])

        return all_ideas

# 命令行界面
def main():
    parser = argparse.ArgumentParser(description="內容管理系統")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 創建文章
    create_parser = subparsers.add_parser('create', help='創建新文章')
    create_parser.add_argument('--title', required=True, help='文章標題')
    create_parser.add_argument('--category', required=True, help='文章分類')
    create_parser.add_argument('--subcategory', required=True, help='子分類')
    create_parser.add_argument('--subtitle', help='副標題')

    # 批量創建
    batch_parser = subparsers.add_parser('batch', help='批量創建文章')
    batch_parser.add_argument('--csv', required=True, help='CSV文件路徑')

    # 生成報告
    report_parser = subparsers.add_parser('report', help='生成內容報告')

    # 更新sitemap
    sitemap_parser = subparsers.add_parser('sitemap', help='更新sitemap')

    # SEO優化
    seo_parser = subparsers.add_parser('seo', help='SEO分析')
    seo_parser.add_argument('--file', help='特定文件分析')

    # 備份
    backup_parser = subparsers.add_parser('backup', help='備份內容')

    # 靈感建議
    ideas_parser = subparsers.add_parser('ideas', help='內容創作建議')
    ideas_parser.add_argument('--category', help='特定分類')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = ContentManager()

    if args.command == 'create':
        filename = manager.create_article_from_template(
            title=args.title,
            category=args.category,
            subcategory=args.subcategory,
            subtitle=args.subtitle or ""
        )
        print(f"✓ 文章已創建: {filename}")

    elif args.command == 'batch':
        files = manager.batch_create_from_csv(args.csv)
        print(f"✓ 批量創建完成，共創建 {len(files)} 篇文章")

    elif args.command == 'report':
        report = manager.generate_content_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == 'sitemap':
        manager.update_sitemap()

    elif args.command == 'seo':
        if args.file:
            result = manager.optimize_article_seo(args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("請指定要分析的文件 (--file)")

    elif args.command == 'backup':
        backup_path = manager.backup_content()
        print(f"✓ 備份完成: {backup_path}")

    elif args.command == 'ideas':
        ideas = manager.suggest_content_ideas(args.category)
        print("=== 內容創作建議 ===")
        for idea in ideas:
            print(f"• {idea['title']} ({idea['difficulty']}) - 目標：{idea['target_audience']}")

if __name__ == "__main__":
    main()