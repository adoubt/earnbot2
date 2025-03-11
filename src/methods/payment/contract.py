import markdown
import pdfkit
import aiosqlite
from typing import Dict
from jinja2 import Template
from pathlib import Path

from src.methods.database.licenses_manager import LicensesDatabase,LicensesProductsDatabase,LicenseTemplates

# async def get_markdown_from_db(db_path: str) -> str:
#     """Получить дефолтный шаблон из базы данных."""
#     async with aiosqlite.connect(db_path) as db:
#         cursor = await db.execute('SELECT markdown FROM templates WHERE license_id IS NULL LIMIT 1')
#         row = await cursor.fetchone()
#         return row[0] if row else ''


def generate_html_from_markdown(markdown_text: str, variables: Dict[str, str]) -> str:
    """Заменить переменные в маркдауне и конвертировать в HTML."""
    # Используем Jinja2 для замены переменных
    template = Template(markdown_text)
    filled_markdown = template.render(variables)

    # Конвертируем Markdown в HTML
    html = markdown.markdown(filled_markdown)
    return html


def generate_pdf_from_html(html: str, output_path: str) -> None:
    """Конвертировать HTML в PDF и сохранить."""
    # Конвертируем HTML в PDF с помощью pdfkit
    pdfkit.from_string(html, output_path)


async def create_contract_pdf( variables: Dict[str, str], output_path: str) -> None:
    """Создать PDF контракт и вернуть путь к файлу."""
    # Получаем шаблон markdown из базы данных
    markdown_text = await LicenseTemplates.get_markdown()

    # Генерируем HTML из markdown
    html = generate_html_from_markdown(markdown_text, variables)

    # Генерируем PDF из HTML
    generate_pdf_from_html(html, output_path)


# Пример использования
if __name__ == "__main__":
    db_path = "src/databases/licenses"
    output_path = "contract.pdf"
    variables = {
        'buyer_name': 'Иван Иванов',
        'product_name': 'Инструментал для песни',
        'product_price': '1000 рублей'
    }

    # Вызов асинхронной функции для создания контракта
    import asyncio
    asyncio.run(create_contract_pdf(db_path, variables, output_path))

    print(f"PDF контракт сохранён по пути: {output_path}")
