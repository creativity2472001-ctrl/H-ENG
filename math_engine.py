# math_engine.py
import sympy as sp
import traceback
from typing import Optional, List, Any
from dataclasses import dataclass, field

@dataclass
class Step:
    """خطوة حل مع LaTeX"""
    text: str
    latex: str = ""
    equation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {"text": self.text, "latex": self.latex, "equation": self.equation or ""}

@dataclass
class ExecutionResult:
    """نتيجة تنفيذ الكود"""
    success: bool
    result: Any = None
    result_str: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None

class MathEngine:
    """محرك رياضيات لتنفيذ كود SymPy"""
    
    def __init__(self):
        print("✅ Math Engine ready")
    
    async def shutdown(self):
        """تنظيف الموارد"""
        pass
    
    async def execute(self, code: str) -> ExecutionResult:
        """
        تنفيذ كود SymPy واستخراج النتائج
        
        Args:
            code: كود SymPy (يجب أن يحتوي على final_result و steps)
            
        Returns:
            ExecutionResult: النتيجة
        """
        try:
            # تنفيذ الكود
            namespace = {'sp': sp}
            exec(code, namespace)
            
            # استخراج النتائج
            final_result = namespace.get('final_result')
            steps_data = namespace.get('steps', [])
            
            # تحويل الخطوات
            steps = []
            for s in steps_data:
                if isinstance(s, dict):
                    steps.append(Step(
                        text=s.get('text', ''),
                        latex=s.get('latex', '')
                    ))
                elif isinstance(s, str):
                    steps.append(Step(text=s))
            
            return ExecutionResult(
                success=True,
                result=final_result,
                result_str=str(final_result) if final_result is not None else "",
                steps=steps
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )
