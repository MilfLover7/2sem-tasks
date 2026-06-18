
"""
Программа для моделирования поведения молекул идеального газа в фазовомпереходе на плоскости
"""

import sys
from prodgect2semInterface import Interface

def main():
    app = Interface()
    app.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Ошибка: {error}")
        sys.exit(1)