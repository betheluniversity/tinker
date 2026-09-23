from ast import literal_eval

def _coerce_value(value):
    if not isinstance(value, str):
        return value

    text = value.strip()
    if text.lower() == 'true':
        return True
    if text.lower() == 'false':
        return False

    try:
        return literal_eval(text)
    except Exception:
        return value


def load_config_from_block(tinker_controller, block_id):
    raw = tinker_controller.read(block_id, type='block')
    block = raw.get('asset', {}).get('xhtmlDataDefinitionBlock', {})
    structured_data = block.get('structuredData', {})
    nodes = structured_data.get('structuredDataNodes', {}).get('structuredDataNode', [])

    if isinstance(nodes, dict):
        nodes = [nodes]

    loaded_values = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue

        key = node.get('identifier')
        if not key:
            continue

        value = None
        node_type = node.get('type', '')
        asset_type = node.get('assetType', '')
        if node_type == 'text':
            value = node.get('text')
        elif node_type == 'asset':
            if asset_type == 'block':
                value = node.get('blockId')
            elif asset_type == 'page':
                value = node.get('pageId')
            elif asset_type == 'file':
                value = node.get('fileId')
        
        if value is None:
            continue

        coerced = _coerce_value(value)
        loaded_values[key] = coerced
        globals()[key] = coerced

    return loaded_values