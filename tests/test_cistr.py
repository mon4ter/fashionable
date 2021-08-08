from pytest import mark

from fashionable import CIStr


@mark.parametrize('left,right', [
    (CIStr('test'), 'test'),
    (CIStr('test'), CIStr('test')),
    (CIStr('TEST'), 'test'),
    (CIStr('test'), CIStr('TEST')),
    (CIStr('camelCase'), 'camel_case'),
    (CIStr('camelCase'), 'camel-case'),
    (CIStr('camelCase'), 'CamelCase'),
    (CIStr('camelCase'), 'CAMEL_CASE'),
    (CIStr('snake_case'), 'snakeCase'),
    (CIStr('snake_case'), 'SnakeCase'),
    (CIStr('snake_case'), 'snake-case'),
    (CIStr('snake_case'), 'SNAKE_CASE'),
    (CIStr('PascalCase'), 'pascalCase'),
    (CIStr('PascalCase'), 'pascal_case'),
    (CIStr('PascalCase'), 'pascal-case'),
    (CIStr('PascalCase'), 'PASCAL_CASE'),
    (CIStr('kebab-case'), 'kebabCase'),
    (CIStr('kebab-case'), 'kebab_case'),
    (CIStr('kebab-case'), 'KebabCase'),
    (CIStr('kebab-case'), 'KEBAB_CASE'),
    (CIStr('UPPER_CASE'), 'upperCase'),
    (CIStr('UPPER_CASE'), 'upper-case'),
    (CIStr('UPPER_CASE'), 'upper_case'),
    (CIStr('UPPER_CASE'), 'UpperCase'),
    (CIStr('HUNCase'), 'hunCase'),
    (CIStr('HUNCase'), 'hun-case'),
    (CIStr('HUNCase'), 'hun_case'),
    (CIStr('HUNCase'), 'HUN_CASE'),
])
def test_cistr_eq(left: str, right: str):
    assert left == right
