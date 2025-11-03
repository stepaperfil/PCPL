
def field(items, *args):
    assert len(args) > 0
    for dict_item in items:
        if len(args) == 1:

            value = dict_item.get(*args)
            if value is not None:
                yield value
        else:
            result = {}
            has_valid_fields = False
            for key in args:
                value = dict_item.get(key)
                if value is not None:
                    result[key] = value
                    has_valid_fields = True
            if has_valid_fields:
                yield result


if __name__ == '__main__':
    goods = [
        {'title': 'Ковер', 'price': 2000, 'color': 'green'},
        {'title': 'Диван для отдыха', 'color': 'black'}
    ]

    print("field(goods, 'title'):")
    for title in field(goods, 'title'):
        print(title)

    print("\nfield(goods, 'title', 'price'):")
    for product in field(goods, 'title', 'price'):
        print(product)
