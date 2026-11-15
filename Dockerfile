# ---- Stage 1: сборка зависимостей (builder) ----
FROM python:3.12-slim AS builder

WORKDIR /build

# создаём виртуальное окружение и ставим зависимости —
# в финальный образ попадёт только готовое venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: рантайм (только нужное) ----
FROM python:3.12-slim

WORKDIR /app

# копируем готовое venv из builder-этапа
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# код приложения
COPY app ./app

# работаем от непривилегированного пользователя
RUN useradd --create-home --shell /bin/false appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
