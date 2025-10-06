#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sitemap 自動生成器
掃描所有HTML文件並自動生成sitemap.xml
"""

import os
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin

class SitemapGenerator:
    def __init__(self, base_dir: str = ".", domain: str = "https://lawyer880.com"):
        self.base_dir = base_dir
        self.domain = domain
        self.sitemap_path = os.path.join(base_dir, "sitemap.xml")

        # 頁面優先級配置
        self.page_priorities = {
            "index.html": {"priority": "1.0", "changefreq": "weekly"},
            "services-tailwind.html": {"priority": "0.9", "changefreq": "monthly"},
            "service-process.html": {"priority": "0.8", "changefreq": "monthly"},
            "team.html": {"priority": "0.8", "changefreq": "monthly"},
            "cases.html": {"priority": "0.8", "changefreq": "weekly"},
            "legal-knowledge.html": {"priority": "0.8", "changefreq": "weekly"},
            "pricing.html": {"priority": "0.7", "changefreq": "monthly"},
        }

        # 排除的文件
        self.excluded_files = {
            "googlecaf92c162f582b73.html",
            "article-template.html"
        }

    def scan_html_files(self) -> list:
        """掃描所有HTML文件"""
        html_files = []

        # 掃描根目錄的HTML文件
        root_files = glob.glob(os.path.join(self.base_dir, "*.html"))
        for file_path in root_files:
            filename = os.path.basename(file_path)
            if filename not in self.excluded_files:
                html_files.append({
                    "path": filename,
                    "full_path": file_path,
                    "type": self.classify_page(filename)
                })

        # 掃描articles目錄的HTML文件
        articles_pattern = os.path.join(self.base_dir, "articles", "**", "*.html")
        article_files = glob.glob(articles_pattern, recursive=True)
        for file_path in article_files:
            rel_path = os.path.relpath(file_path, self.base_dir)
            html_files.append({
                "path": rel_path,
                "full_path": file_path,
                "type": "article"
            })

        return html_files

    def classify_page(self, filename: str) -> str:
        """分類頁面類型"""
        if filename.startswith("article-"):
            return "article"
        elif filename == "index.html":
            return "homepage"
        elif filename in ["services-tailwind.html", "service-process.html"]:
            return "service"
        elif filename in ["team.html", "cases.html"]:
            return "info"
        elif filename == "legal-knowledge.html":
            return "knowledge"
        else:
            return "other"

    def get_file_modification_date(self, file_path: str) -> str:
        """獲取文件修改日期"""
        try:
            timestamp = os.path.getmtime(file_path)
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def get_page_config(self, filename: str, page_type: str) -> dict:
        """獲取頁面SEO配置"""
        if filename in self.page_priorities:
            return self.page_priorities[filename]

        # 根據頁面類型設定預設值
        type_configs = {
            "homepage": {"priority": "1.0", "changefreq": "weekly"},
            "service": {"priority": "0.9", "changefreq": "monthly"},
            "info": {"priority": "0.8", "changefreq": "monthly"},
            "knowledge": {"priority": "0.8", "changefreq": "weekly"},
            "article": {"priority": "0.6", "changefreq": "monthly"},
            "other": {"priority": "0.5", "changefreq": "monthly"}
        }

        return type_configs.get(page_type, {"priority": "0.5", "changefreq": "monthly"})

    def generate_sitemap(self) -> str:
        """生成sitemap.xml"""
        # 建立XML根元素
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # 掃描所有HTML文件
        html_files = self.scan_html_files()

        for file_info in html_files:
            url_element = ET.SubElement(urlset, "url")

            # URL位置
            loc = ET.SubElement(url_element, "loc")
            file_url = urljoin(self.domain + "/", file_info["path"])
            loc.text = file_url

            # 最後修改日期
            lastmod = ET.SubElement(url_element, "lastmod")
            lastmod.text = self.get_file_modification_date(file_info["full_path"])

            # 獲取頁面配置
            config = self.get_page_config(os.path.basename(file_info["path"]), file_info["type"])

            # 更新頻率
            changefreq = ET.SubElement(url_element, "changefreq")
            changefreq.text = config["changefreq"]

            # 優先級
            priority = ET.SubElement(url_element, "priority")
            priority.text = config["priority"]

        # 生成XML樹
        tree = ET.ElementTree(urlset)

        # 設定XML格式化
        self.indent_xml(urlset)

        # 寫入檔案
        with open(self.sitemap_path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

        return self.sitemap_path

    def indent_xml(self, elem, level=0):
        """格式化XML縮排"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def validate_sitemap(self) -> dict:
        """驗證sitemap格式"""
        try:
            tree = ET.parse(self.sitemap_path)
            root = tree.getroot()

            url_count = len(root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"))

            return {
                "valid": True,
                "url_count": url_count,
                "file_size": os.path.getsize(self.sitemap_path),
                "message": f"Sitemap包含 {url_count} 個URL"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": f"Sitemap驗證失敗: {e}"
            }

    def update_robots_txt(self):
        """更新robots.txt，確保包含sitemap"""
        robots_path = os.path.join(self.base_dir, "robots.txt")
        sitemap_url = urljoin(self.domain + "/", "sitemap.xml")

        robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {sitemap_url}

# Disallow sensitive files
Disallow: /googlecaf92c162f582b73.html
Disallow: /templates/
Disallow: /tools/
"""

        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)

    def generate_report(self) -> dict:
        """生成詳細報告"""
        html_files = self.scan_html_files()

        report = {
            "generation_time": datetime.now().isoformat(),
            "total_pages": len(html_files),
            "sitemap_path": self.sitemap_path,
            "domain": self.domain,
            "page_breakdown": {}
        }

        # 統計不同類型頁面數量
        for file_info in html_files:
            page_type = file_info["type"]
            if page_type not in report["page_breakdown"]:
                report["page_breakdown"][page_type] = 0
            report["page_breakdown"][page_type] += 1

        # 驗證sitemap
        validation = self.validate_sitemap()
        report["validation"] = validation

        return report

# 使用範例和命令行工具
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="生成網站sitemap.xml")
    parser.add_argument("--domain", default="https://lawyer880.com", help="網站域名")
    parser.add_argument("--output", help="輸出sitemap路徑")
    parser.add_argument("--report", action="store_true", help="生成詳細報告")
    parser.add_argument("--validate", action="store_true", help="僅驗證現有sitemap")

    args = parser.parse_args()

    generator = SitemapGenerator(domain=args.domain)

    if args.validate:
        validation = generator.validate_sitemap()
        print(json.dumps(validation, indent=2, ensure_ascii=False))
    else:
        print("正在生成sitemap...")
        sitemap_path = generator.generate_sitemap()
        print(f"✓ Sitemap已生成: {sitemap_path}")

        print("正在更新robots.txt...")
        generator.update_robots_txt()
        print("✓ robots.txt已更新")

        if args.report:
            report = generator.generate_report()
            print("\n=== 生成報告 ===")
            print(json.dumps(report, indent=2, ensure_ascii=False))

            # 儲存報告
            report_path = os.path.join("tools", "sitemap-report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"詳細報告已儲存至: {report_path}")