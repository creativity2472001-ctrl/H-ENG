# core/calculator.py
import ast
from typing import Dict, Any

class Calculator:
    """آلة حاسبة بسيطة - تعمل بدون AI"""
    
    def __init__(self):
        self.allowed_functions = {
            'abs': abs, 'round': round,
            'int': int, 'float': float
        }
    
    def evaluate(self, expression: str) -> Dict[str, Any]:
        """
        تقييم تعبير رياضي بسيط
        مثال: "1+1", "2*3", "10/2"
        """
        try:
            # تحليل التعبير للتحقق من الأمان
            tree = ast.parse(expression, mode='eval')
            
            # التأكد من عدم وجود دوال خطيرة
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if not isinstance(node.func, ast.Name):
                        return {
                            "success": False,
                            "error": "عملية غير مسموح بها"
                        }
                    if node.func.id not in self.allowed_functions:
                        return {
                            "success": False,
                            "error": f"دالة '{node.func.id}' غير مسموح بها"
                        }
            
            # تنفيذ التعبير بأمان
            code = compile(tree, '<string>', 'eval')
            result = eval(code, {"__builtins__": {}}, self.allowed_functions)
            
            return {
                "success": True,
                "result": str(result),
                "steps": [{"text": f"{expression} = {result}"}]
            }
            
        except ZeroDivisionError:
            return {"success": False, "error": "لا يمكن القسمة على صفر"}
        except SyntaxError:
            return {"success": False, "error": "تعبير غير صحيح"}
        except Exception as e:
            return {"success": False, "error": str(e)}
