# main.py - واجهة سطر الأوامر
from calculator import Calculator
import os

calc = Calculator()

def main():
    os.system('cls')
    print("="*50)
    print("        🧮 آلة حاسبة علمية (CLI)")
    print("="*50)
    print("أمثلة: 2+2, 5*3, 10/2, 2^3, sqrt(100), sin(30)")
    print("أوامر: exit, clear")
    print("-"*50)
    
    while True:
        try:
            cmd = input("\n>>> ").strip()
            
            if cmd.lower() == 'exit':
                break
            if cmd.lower() == 'clear':
                os.system('cls')
                continue
            
            result = calc.calculate(cmd)
            print(f"= {result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
