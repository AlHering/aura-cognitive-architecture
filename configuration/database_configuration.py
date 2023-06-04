# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture
*            (c) 2023 Alexander Hering             *
****************************************************
"""
ENTITY_PROFILE = {
    "model": {
        "#meta": {
            "schema": "machine_learning_models",
            "description": "Local Machine Learning models.",
            "keep_deleted": True
        },
        "id": {
            "type": "int",
            "key": True,
            "autoincrement": True,
            "required": True,
            "description": "ID of the model (file)."
        },
        "file_name": {
            "type": "str",
            "required": True,
            "description": "File name, consisting of name and extension.",
        },
        "folder": {
            "type": "text",
            "required": True,
            "description": "Folder of model file.",
        },
        "status": {
            "type": "str",
            "required": True,
            "description": "Status of the model: 'unknown' -> 'linked' -> 'collected' -> 'tracked'",
            "post": "lambda _: 'unknown'"
        },
        "created": {
            "type": "datetime",
            "description": "Timestamp of creation.",
            "post": "lambda _: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')"
        },
        "inactive": {
            "type": "char",
            "description": "Flag for marking inactive entries.",
            "delete": "lambda _: 'X'"
        }
    }
}

LINKAGE_PROFILE = {

}

VIEW_PROFILE = {

}
