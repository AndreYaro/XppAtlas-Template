# tools/

## index_model.py — X++ Model Indexer

Парсит XML-исходники AOT и создаёт компактный JSON-индекс модели.

### Запуск

Основной источник model source code теперь только D365 MCP server. Примеры ниже считаются legacy-подходом для локально выгруженного mirror и не должны быть основным способом чтения исходников при анализе или внесении изменений.

```bash
# Legacy: индексировать локальный mirror, если он был отдельно выгружен из MCP
python tools/index_model.py <legacy-exported-source-folder>

# Legacy: указать путь к выходному файлу
python tools/index_model.py <legacy-exported-source-folder> --out .claude/index/DYSBillingIntegration.json

# Legacy: другая модель
python tools/index_model.py <legacy-exported-source-folder> --out .claude/index/DYSGEPIntegration.json
```

### Что индексируется

| Тип AOT-объекта | Что извлекается |
|-----------------|-----------------|
| `AxClass` | имя, summary, modifiers, extends, implements, поля, методы (имя, returnType, params, attributes, summary) |
| `AxTable` / `AxTableExtension` | имя, поля (тип, EDT, enum), relation-ы, индексы |
| `AxEnum` / `AxEnumExtension` | имя, values |
| `AxEdt` / `AxEdtExtension` | имя, extends, label |
| `AxDataEntityView` | имя, publicName, primaryTable, поля |
| `AxService` | имя, serviceClass, operations |
| `AxQuery` | имя, dataSources |

### Использование индекса в Claude

Файлы `.claude/index/*.json` можно читать в начале сессии как контекст модели вместо построчного чтения XML-исходников:

```
Прочитай .claude/index/DYSBillingIntegration.json и используй его как карту модели при ответах на вопросы.
```

Или агент сам читает индекс через Read tool в начале задачи.

### Обновление индекса

После изменения исходников — перезапустить скрипт. Рекомендуется добавить в CI или запускать перед сессией работы с новой моделью.

## bootstrap_context.py — Session Bootstrap Helper

Определяет активную цепочку `context_setup.md` и подсказывает, какие индексные файлы читать первыми.

### Запуск

```bash
python tools/bootstrap_context.py
python tools/bootstrap_context.py Models/DYSNepi/Tasks/22822_UpdateInvoiceWIthKSeFFields
python tools/bootstrap_context.py --json
```

### Что делает

- находит ближайший `context_setup.md` и поднимается вверх до корня репозитория
- собирает эффективный контекст `project -> model -> task`
- определяет активную модель
- показывает `.claude/index/{ModelName}_summary.json`, `.claude/index/{ModelName}.json` и `_all_summary.json`
- напоминает, что перед правками нужно сверяться с реальными XML/X++ исходниками, загруженными через D365 MCP

`bootstrap_context.py` автоматически вызывает `ensure_index.py`, поэтому перед выдачей путей к индексам они будут проверены и при необходимости обновлены инкрементально.

## ensure_index.py — Incremental Freshness Check

Проверяет, устарели ли файлы в `.claude/index`, и запускает `index_all.py --incremental` только если это действительно нужно.

### Запуск

```bash
python tools/ensure_index.py
python tools/ensure_index.py --model DYSNepi
python tools/ensure_index.py --quiet
```

### Где используется

- `bootstrap_context.py` перед чтением индексов
- `search_index.py` перед поиском
- `.claude/settings.json` в stop hook для фонового обновления после сессии

Примечание для шаблона: пока в репозитории есть только `_Model_Template`, индексных файлов может не быть. После создания реальной модели без начального `_` автоматическая индексация начнёт работать как обычно.
