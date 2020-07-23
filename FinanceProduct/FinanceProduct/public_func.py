def convert_risk(key):
    risk = {'1': '低风险',
            '2': '较低风险',
            '3': '中等风险',
            '4': '较高风险',
            '5': '高风险'
            }

    return risk[key]


def has_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def convert_number(character):
    table = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11,
             '十二': 12}
    return table[character]


def convert_product_type(key):
    type = {'1': '活期',
            '2': '定期',
            '3': '结构化',
            '4': '特色'
            }

    return type[key]


