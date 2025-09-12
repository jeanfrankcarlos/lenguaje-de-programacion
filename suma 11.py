def cal_media(*args):
    total = 0
    for i in args:
        total =total + i
        resultado = total / len(args)
    return resultado
a, b, c, d, e = 3, 5, 10, 15, 160
media = cal_media(a, b, c, d, e)
print(media)

print(cal_media(12,11))
print(cal_media(2,20,15))
print(cal_media(100,500,600,700))

print("La media es:")
print(media)
print("Programa terminado")
print(cal_media(2,3,4))
