# main.py - واجهة المستخدم للآلة الحاسبة
from calculator import Calculator
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    calc = Calculator()
    clear_screen()
    
    print("="*60)
    print("          🧮 آلة حاسبة علمية - النسخة الأساسية")
    print("="*60)
    print("الأمثلة المدعومة حالياً:")
    print("  • 2+2, 5*3, 10/2, 2^3")
    print("  • sin(30), cos(60), tan(45)")
    print("  • sqrt(16), 5!, log(10), ln(e)")
    print("  • pi, e (ثوابت)")
    print("-"*60)
    print("أوامر خاصة:")
    print("  • 'ans' - النتيجة الأخيرة")
    print("  • 'clear' - مسح الشاشة")
    print("  • 'exit' - خروج")
    print("="*60)
    
    while True:
        try:
            # عرض prompt مع النتيجة الأخيرة
            prompt = "\n>>> "
            if calc.last_result is not None:
                prompt = f"\n[النتيجة: {calc.last_result}] >>> "
            
            cmd = input(prompt).strip()
            
            if not cmd:
                continue
            
            if cmd.lower() == 'exit':
                print("وداعاً 👋")
                break
            
            if cmd.lower() == 'clear':
                clear_screen()
                continue
            
            if cmd.lower() == 'ans':
                if calc.last_result is not None:
                    print(f"النتيجة الأخيرة: {calc.last_result}")
                else:
                    print("لا توجد نتيجة سابقة")
                continue
            
            # حساب التعبير
            result = calc.calculate(cmd)
            
            if isinstance(result, float):
                # تقريب النتائج الطويلة
                if abs(result) > 1e10 or (abs(result) < 1e-4 and result != 0):
                    print(f"✅ = {result:.6e}")
                else:
                    print(f"✅ = {result:.6f}".rstrip('0').rstrip('.'))
            elif isinstance(result, str) and result.startswith('خطأ'):
                print(f"❌ {result}")
            else:
                print(f"✅ {result}")
            
        except KeyboardInterrupt:
            print("\nوداعاً 👋")
            break
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
