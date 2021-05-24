# SAF JSONSchema

**SAF JSONSchema** — это плагин для SmartApp Framework который позволяет валидировать
входящие и исходящие сообщение по JSON-Schema файлам, а также предоставляет стандартный набор схем.

## Оглавление
   * [Установка](#Установка)
   * [Новый функционал](#Новый)
   * [Обратная связь](#Обратная)

____

# Установка

Установить плагин можно из git.

```bash
python -m pip install git+https://github.com/sberdevices/saf_jsonschema@main
```

# Новый функционал

Плагин предоставляет следующие сущности:
- Класс `SchemaStaticResolver`, который позволяет подгрузить набор взаимосвязанных схем
и валидировать объекты по ним. Внутри используется библиотека [`jsonschema`](https://python-jsonschema.readthedocs.io),
которая предоставляет класс `RefResolver`, над ним добавлена подгрузка схем из файлов
и возможность проверки объектов с разными схемами.
При этом, поддерживаются файлы схем не только в формате JSON, но и YAML.
- Объект `default_static_resolver` – экземпляр класса `SchemaStaticResolver` со стандартными схемами,
из которых самая актуальная для смартапов – `ANSWER_TO_USER`.
- Класс `ByNameMessageValidator` – наследник класса `core.message.msg_validator.MessageValidator`,
может использоваться как готовый валидатор в конфиге смартапа.

С помощью `ByNameMessageValidator` можно легко добавить валидацию исходящих сообщений прописав
в конфиг следующую пару строк: 

```python
from saf_jsonschema import ByNameMessageValidator
TO_MSG_VALIDATORS = (ByNameMessageValidator(name="AppAnswer"),)
```

Помимо этого, объекты класса `ByNameMessageValidator` легко расширяются:
- Можно использовать стандартные схемы, но переопределить стандартный маппинг
имён сообщений к схемам используя словарик `name_to_schema`, а также
отключить использование стандартного маппинга флаго `direct_pass`.
Либо отнаследовать класс и переопределить метод `_get_schema_by_message`.
- Можно передать собственный объект `SchemaStaticResolver` с нестандартными схемами.

# Обратная связь

C вопросами и предложениями пишите нам по адресу developer@sberdevices.ru
или вступайте в наш Telegram канал - [SmartMarket Community](https://t.me/smartmarket_community). 
