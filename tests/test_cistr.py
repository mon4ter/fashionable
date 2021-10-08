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


@mark.parametrize('left,right', [
    (CIStr('test'), CIStr('test')),
    (CIStr('TEST'), CIStr('test')),
    (CIStr('test'), CIStr('TEST')),
    (CIStr('camelCase'), CIStr('camel_case')),
    (CIStr('camelCase'), CIStr('camel-case')),
    (CIStr('camelCase'), CIStr('CamelCase')),
    (CIStr('camelCase'), CIStr('CAMEL_CASE')),
    (CIStr('snake_case'), CIStr('snakeCase')),
    (CIStr('snake_case'), CIStr('SnakeCase')),
    (CIStr('snake_case'), CIStr('snake-case')),
    (CIStr('snake_case'), CIStr('SNAKE_CASE')),
    (CIStr('PascalCase'), CIStr('pascalCase')),
    (CIStr('PascalCase'), CIStr('pascal_case')),
    (CIStr('PascalCase'), CIStr('pascal-case')),
    (CIStr('PascalCase'), CIStr('PASCAL_CASE')),
    (CIStr('kebab-case'), CIStr('kebabCase')),
    (CIStr('kebab-case'), CIStr('kebab_case')),
    (CIStr('kebab-case'), CIStr('KebabCase')),
    (CIStr('kebab-case'), CIStr('KEBAB_CASE')),
    (CIStr('UPPER_CASE'), CIStr('upperCase')),
    (CIStr('UPPER_CASE'), CIStr('upper-case')),
    (CIStr('UPPER_CASE'), CIStr('upper_case')),
    (CIStr('UPPER_CASE'), CIStr('UpperCase')),
    (CIStr('HUNCase'), CIStr('hunCase')),
    (CIStr('HUNCase'), CIStr('hun-case')),
    (CIStr('HUNCase'), CIStr('hun_case')),
    (CIStr('HUNCase'), CIStr('HUN_CASE')),
])
def test_cistr_hash(left: str, right: str):
    assert hash(left) == hash(right)
