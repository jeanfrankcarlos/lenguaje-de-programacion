def cal_suma(*args):
  total = 0
  for i in args:
    total = total + i
  return total

a, b, c, d, e = 3, 5, 10, 15, 160
suma = cal_suma(a, b, c, d, e)

print("La suma es:")
print(suma)
print("La suma de 4 y 35 es:")
print(cal_suma(4,35))
print("La suma de 3, 14 y 10 es:")
print(cal_suma(3,14,10))
print("La suma de 10, 50, 60 y 70 es:")
print(cal_suma(10,50,60,70))
print("Programa terminado")






