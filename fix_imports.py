# fix_imports.py
import re
import ast
from pathlib import Path

def find_missing_attributes():
    """Detecta erros de atributo e sugere correções"""
    
    errors = []
    
    for py_file in Path('backend').rglob('*.py'):
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id == 'models':
                            errors.append({
                                'file': py_file,
                                'attribute': node.attr,
                                'line': node.lineno
                            })
        except:
            pass
    
    return errors

def suggest_fix(errors):
    """Gera código de correção"""
    models_file = Path('backend/database/models.py')
    
    with open(models_file) as f:
        existing = f.read()
    
    suggestions = []
    
    for error in errors:
        attr = error['attribute']
        if attr not in existing:
            suggestions.append(f"""
# Adicionar em models.py:
class {attr}(Base):
    __tablename__ = "{attr.lower()}s"
    id = Column(Integer, primary_key=True)
    # TODO: Adicionar campos baseado no uso em {error['file']}
""")
    
    return suggestions

if __name__ == '__main__':
    errors = find_missing_attributes()
    if errors:
        print("❌ Erros encontrados:")
        for e in errors:
            print(f"  {e['file']}:{e['line']} → models.{e['attribute']}")
        
        print("\n✅ Sugestões:")
        for fix in suggest_fix(errors):
            print(fix)
    else:
        print("✅ Nenhum erro de atributo detectado!")