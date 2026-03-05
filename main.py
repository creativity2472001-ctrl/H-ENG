# main.py - واجهة سطر الأوامر
from calculator import Calculator
import os
import re

calc = Calculator()

def main():
    os.system('cls')
    print("="*50)
    print("        🧮 آلة حاسبة علمية (CLI)")
    print("="*50)
    print("أمثلة: 2+2, 5*3, 10/2, 2^3, sqrt(100), sin(30), x+5=10")
    print("أوامر: exit, clear")
    print("-"*50)
    
    while True:
        try:
            cmd = input("\n>>> ").strip().lower()
            
            if cmd == 'exit':
                break
            if cmd == 'clear':
                os.system('cls')
                continue
            
            # معالجة الدوال المثلثية
            if 'sin' in cmd and '(' in cmd and ')' in cmd:
                match = re.search(r'sin\((\d+)\)', cmd)
                if match:
                    angle = float(match.group(1))
                    result = calc.sin(angle)
                    print(f"= {result}")
                    continue
            
            if 'cos' in cmd and '(' in cmd and ')' in cmd:
                match = re.search(r'cos\((\d+)\)', cmd)
                if match:
                    angle = float(match.group(1))
                    result = calc.cos(angle)
                    print(f"= {result}")
                    continue
            
            if 'tan' in cmd and '(' in cmd and ')' in cmd:
                match = re.search(r'tan\((\d+)\)', cmd)
                if match:
                    angle = float(match.group(1))
                    result = calc.tan(angle)
                    print(f"= {result}")
                    continue
            
            # معادلات
            if '=' in cmd:
                result = calc.solve_equation(cmd)
                print(f"= {result}")
                continue
            
            # عمليات عادية
            result = calc.calculate(cmd)
            print(f"= {result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
