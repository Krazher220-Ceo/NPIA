"""
Генератор PDF для данных входа
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
from typing import Dict


def generate_credentials_pdf(data: Dict[str, str]) -> BytesIO:
    """
    Генерация PDF с данными для входа
    
    Args:
        data: Словарь с ключами 'username', 'password', 'email'
    
    Returns:
        BytesIO объект с PDF содержимым
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Заголовок
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1 * inch, height - 1 * inch, "Данные для входа в систему")
    
    # Данные
    y_position = height - 1.5 * inch
    c.setFont("Helvetica", 12)
    
    c.drawString(1 * inch, y_position, "ЛОГИН:")
    c.setFont("Courier-Bold", 14)
    c.drawString(1 * inch, y_position - 0.3 * inch, data.get('username', ''))
    
    y_position -= 0.8 * inch
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, y_position, "ПАРОЛЬ:")
    c.setFont("Courier-Bold", 14)
    c.drawString(1 * inch, y_position - 0.3 * inch, data.get('password', ''))
    
    y_position -= 0.8 * inch
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, y_position, "EMAIL:")
    c.setFont("Courier-Bold", 14)
    c.drawString(1 * inch, y_position - 0.3 * inch, data.get('email', ''))
    
    # Предупреждение
    y_position -= 1 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColorRGB(1, 0, 0)  # Красный цвет
    c.drawString(1 * inch, y_position, "⚠️ Сохраните эти данные в безопасном месте!")
    c.setFillColorRGB(0, 0, 0)  # Возвращаем черный
    
    c.save()
    buffer.seek(0)
    return buffer

