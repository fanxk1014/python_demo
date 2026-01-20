import math

current_number = 0
while current_number < 10:
    current_number += 12
    if current_number % 2 == 0:
        continue

    print(current_number)

print("""君不见黄河之水天上来
奔流到海不复回
君不见高堂明镜悲白发
朝如青丝暮成雪""")

result = math.sin(1)
print(result)

a = '你的'
b = 123

print(len(a+str(b)))