
import ast
import re
import keyword
from collections import defaultdict, Counter

class NameExtractor(ast.NodeVisitor):
    def __init__(self):
        self.names = defaultdict(set)

    def visit_FunctionDef(self, node):
        self.names['function'].add(node.name)
        for arg in node.args.args:
            self.names['parameter'].add(arg.arg)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.names['class'].add(node.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        self.names['variable'].add(node.id)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name.isupper():
                    self.names['constant'].add(name)
                else:
                    self.names['variable'].add(name)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            self.names['attribute'].add(node.attr)
        self.generic_visit(node)

def classify_naming_style(name):
    if name.startswith('__') and name.endswith('__'):
        return 'dunder_method'
    if name.startswith('_') and not name.startswith('__'):
        return 'private'
    if re.fullmatch(r'[a-z]+(_[a-z0-9]+)*', name):
        return 'snake_case'
    if re.fullmatch(r'[A-Z][a-zA-Z0-9]+', name):
        return 'PascalCase'
    if re.fullmatch(r'[a-z]+([A-Z][a-z0-9]*)+', name):
        return 'camelCase'
    if re.fullmatch(r'[A-Z]+(_[A-Z0-9]+)*', name):
        return 'UPPER_CASE'
    return 'invalid'

def check_naming_rules(name: str, kind: str) -> dict:
    result = {}
    score = 0
    total = 0

    total += 1
    result['starts_with_letter'] = name[0].isalpha()
    score += int(result['starts_with_letter'])

    if kind == 'class':
        total += 1
        result['is_pascal_case'] = bool(re.match(r'^[A-Z][a-zA-Z0-9]+$', name))
        score += int(result['is_pascal_case'])

    elif kind in ['function', 'variable', 'parameter', 'attribute']:
        total += 1
        result['is_snake_case'] = bool(re.match(r'^[a-z]+(_[a-z0-9]+)*$', name))
        score += int(result['is_snake_case'])

    elif kind == 'constant':
        total += 1
        result['is_upper_case'] = bool(re.match(r'^[A-Z]+(_[A-Z0-9]+)*$', name))
        score += int(result['is_upper_case'])

    elif kind == 'magic_method':
        total += 1
        result['is_dunder'] = name.startswith('__') and name.endswith('__')
        score += int(result['is_dunder'])

    elif kind == 'private':
        total += 1
        result['starts_with_underscore'] = name.startswith('_') and not name.startswith('__')
        score += int(result['starts_with_underscore'])

    total += 1
    result['is_keyword'] = name in keyword.kwlist
    score += int(not result['is_keyword'])

    result['score'] = round(score / total, 2)
    return result

def compute_style_distribution(names):
    styles = [classify_naming_style(name) for name in names]
    counter = Counter(styles)
    return dict(counter)

def compute_style_stats(names):
    total_chars = sum(len(name) for name in names)
    stats = {'uppercase': 0, 'lowercase': 0, 'underscore': 0, 'digit': 0, 'symbol': 0}
    for name in names:
        for char in name:
            if char.isupper():
                stats['uppercase'] += 1
            elif char.islower():
                stats['lowercase'] += 1
            elif char == '_':
                stats['underscore'] += 1
            elif char.isdigit():
                stats['digit'] += 1
            else:
                stats['symbol'] += 1
    return {k + '_ratio': round(v / total_chars, 3) if total_chars else 0 for k, v in stats.items()}
