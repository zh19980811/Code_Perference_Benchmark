
import ast
import re
from collections import Counter

# 工具函数
def is_snake_case(name):
    return bool(re.fullmatch(r'[a-z_][a-z0-9_]*', name))

def count_return_statements(node):
    return sum(isinstance(n, ast.Return) for n in ast.walk(node))

def has_try_except(node):
    return any(isinstance(n, ast.Try) for n in ast.walk(node))

def get_call_depth(node, depth=0):
    if isinstance(node, ast.Call):
        return max([get_call_depth(arg, depth + 1) for arg in ast.iter_child_nodes(node)] + [depth])
    else:
        return max([get_call_depth(child, depth) for child in ast.iter_child_nodes(node)] + [depth])

def get_control_structure_count(node):
    return sum(isinstance(n, (ast.If, ast.For, ast.While)) for n in ast.walk(node))

def get_annotation_ratio(func_node):
    args = func_node.args.args
    if not args:
        return 1.0
    annotated = sum(1 for arg in args if arg.annotation is not None)
    return round(annotated / len(args), 2)

def get_exception_specificity(func_node):
    specificity = 1.0
    for node in ast.walk(func_node):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                specificity -= 0.5
    return max(0.0, specificity)

def get_comment_ratio(func_node, source_lines):
    if hasattr(func_node, 'lineno') and hasattr(func_node, 'end_lineno'):
        func_lines = source_lines[func_node.lineno - 1:func_node.end_lineno]
        total_lines = len(func_lines)
        comment_lines = sum(1 for line in func_lines if line.strip().startswith('#'))
        return round(comment_lines / total_lines, 2) if total_lines else 0.0
    return 0.0

def get_average_name_length(func_node):
    names = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Name):
            names.append(len(node.id))
    return round(sum(names) / len(names), 2) if names else 0.0

def get_repetition_ratio(func_node, source_lines):
    if hasattr(func_node, 'lineno') and hasattr(func_node, 'end_lineno'):
        func_lines = source_lines[func_node.lineno - 1:func_node.end_lineno]
        norm_lines = [line.strip() for line in func_lines if line.strip()]
        total = len(norm_lines)
        unique = len(set(norm_lines))
        return round((total - unique) / total, 2) if total else 0.0
    return 0.0

def get_function_score_quantified(func_node, source_lines, verbose=False):
    metrics = {}

    length = func_node.end_lineno - func_node.lineno + 1 if hasattr(func_node, 'end_lineno') else 0
    metrics['length'] = length
    metrics['argument_count'] = len(func_node.args.args)
    metrics['has_docstring'] = int(ast.get_docstring(func_node) is not None)
    metrics['has_try_except'] = int(has_try_except(func_node))
    metrics['is_snake_case'] = int(is_snake_case(func_node.name))
    metrics['function_name_length'] = len(func_node.name)
    metrics['return_count'] = count_return_statements(func_node)
    metrics['call_depth'] = get_call_depth(func_node)

    metrics['comment_ratio'] = get_comment_ratio(func_node, source_lines)
    metrics['control_structures'] = get_control_structure_count(func_node)
    metrics['annotation_ratio'] = get_annotation_ratio(func_node)
    metrics['exception_specificity'] = get_exception_specificity(func_node)
    metrics['avg_name_length'] = get_average_name_length(func_node)
    metrics['repetition_ratio'] = get_repetition_ratio(func_node, source_lines)

    weights = {
        'length': -0.1,
        'argument_count': -0.2,
        'has_docstring': 1.0,
        'has_try_except': 0.5,
        'is_snake_case': 1.0,
        'function_name_length': -0.05,
        'return_count': 0.3,
        'call_depth': -0.2,
        'comment_ratio': 2.0,
        'control_structures': -0.2,
        'annotation_ratio': 1.0,
        'exception_specificity': 1.0,
        'avg_name_length': -0.1,
        'repetition_ratio': -1.0
    }

    score = 0
    for k, v in metrics.items():
        if k in weights:
            score += weights[k] * v

    final_score = round(max(0, min(score + 5, 10)), 2)
    if verbose:
        return final_score, metrics
    return final_score
