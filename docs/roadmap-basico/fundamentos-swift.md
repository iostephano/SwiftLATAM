---
sidebar_position: 1
title: Fundamentos Swift
---

# Fundamentos de Swift: La Base de Todo Desarrollador iOS

Swift es el lenguaje de programación creado por Apple en 2014 para desarrollar aplicaciones en todo su ecosistema: iOS, macOS, watchOS y tvOS. Si querés trabajar como desarrollador iOS en Latinoamérica — ya sea de forma freelance, en una startup local o para empresas internacionales — **dominar los fundamentos de Swift no es opcional, es el primer paso obligatorio**.

## ¿Por qué Swift y por qué importa en LATAM?

El mercado de desarrollo iOS en América Latina está en constante crecimiento. Empresas en México, Colombia, Argentina, Chile y Brasil buscan activamente desarrolladores iOS para proyectos locales y remotos con empresas de Estados Unidos y Europa. La demanda supera ampliamente la oferta.

Swift es un lenguaje:

- **Seguro**: El sistema de tipos te protege de errores comunes en tiempo de compilación.
- **Rápido**: Está optimizado para rendimiento, comparable a C++ en muchos escenarios.
- **Expresivo**: Su sintaxis moderna permite escribir código claro y mantenible.
- **Open Source**: Puedes contribuir y aprender directamente del código fuente.

Dominar sus fundamentos te permite no solo crear apps, sino **pensar como desarrollador iOS**, entender la documentación oficial de Apple y comunicarte efectivamente en entrevistas técnicas (que casi siempre incluyen preguntas sobre estos conceptos).

---

## Variables y Constantes

En Swift, toda información se almacena en variables (`var`) o constantes (`let`). Esta distinción es fundamental porque Swift promueve la **inmutabilidad** como buena práctica.

```swift
// Constante: su valor NO puede cambiar después de asignarse
let nombreApp = "MiPrimeraApp"

// Variable: su valor PUEDE cambiar
var contadorDescargas = 0
contadorDescargas += 1

print("\(nombreApp) tiene \(contadorDescargas) descargas")
```

> **Regla de oro**: Usá `let` siempre que sea posible. Solo usá `var` cuando realmente necesités cambiar el valor. Xcode incluso te va a advertir si usás `var` cuando podías usar `let`.

---

## Tipos de Datos Fundamentales

Swift es un lenguaje **fuertemente tipado** con inferencia de tipos. Esto significa que el compilador puede deducir el tipo, pero cada valor tiene un tipo definido.

```swift
// Tipos básicos
let nombre: String = "María"          // Texto
let edad: Int = 28                     // Número entero
let estatura: Double = 1.65           // Número decimal
let esDesarrolladora: Bool = true     // Valor booleano

// Inferencia de tipos: Swift deduce el tipo automáticamente
let ciudad = "Bogotá"        // Swift infiere que es String
let temperatura = 22.5       // Swift infiere que es Double
let activo = false           // Swift infiere que es Bool

// Type Safety: esto NO compila
// let suma = edad + estatura  // Error: no puedes sumar Int + Double directamente

// Conversión explícita
let suma = Double(edad) + estatura  // Ahora sí: 29.65
```

---

## Opcionales: El Concepto más Importante de Swift

Los **opcionales** son probablemente el concepto que más cuesta al principio, pero entenderlos es **absolutamente crítico**. Un opcional representa un valor que puede existir o ser `nil` (ausencia de valor).

```swift
// Un String opcional: puede contener texto o ser nil
var apodo: String? = nil

apodo = "La Maga"

// ❌ NUNCA hagas esto en producción (force unwrap)
// Si apodo es nil, tu app se crashea
// let texto = apodo!

// ✅ Opción 1: Optional Binding con if let
if let apodoSeguro = apodo {
    print("Su apodo es \(apodoSeguro)")
} else {
    print("No tiene apodo")
}

// ✅ Opción 2: Guard let (muy usado en funciones)
func saludar(nombre: String?) {
    guard let nombreSeguro = nombre else {
        print("No se proporcionó nombre")
        return
    }
    // Desde aquí, nombreSeguro es String (no opcional)
    print("¡Hola, \(nombreSeguro)!")
}

saludar(nombre: "Carlos")   // ¡Hola, Carlos!
saludar(nombre: nil)         // No se proporcionó nombre

// ✅ Opción 3: Nil Coalescing Operator (??)
let saludo = "Hola, \(apodo ?? "usuario")"
print(saludo)  // "Hola, La Maga"
```

> **¿Por qué importa esto?** En el desarrollo iOS real, los datos que vienen de APIs, bases de datos o la interfaz de usuario frecuentemente pueden ser `nil`. Un mal manejo de opcionales es la causa número uno de crashes en producción.

---

## Colecciones

Swift ofrece tres tipos principales de colecciones, todos genéricos y type-safe.

### Arrays

```swift
// Array: colección ordenada de elementos del mismo tipo
var lenguajes: [String] = ["Swift", "Kotlin", "Dart"]

// Agregar elementos
lenguajes.append("JavaScript")

// Acceder por índice (cuidado: puede crashear si el índice no existe)
let primero = lenguajes[0]  // "Swift"

// Forma segura de acceder
if let segundo = lenguajes.indices.contains(1) ? lenguajes[1] : nil {
    print(segundo)
}

// Iterar
for lenguaje in lenguajes {
    print("Conozco \(lenguaje)")
}

// Operaciones comunes
print(lenguajes.count)      // 4
print(lenguajes.isEmpty)    // false
print(lenguajes.contains("Swift"))  // true
```

### Diccionarios

```swift
// Diccionario: pares clave-valor
var capitales: [String: String] = [
    "México": "CDMX",
    "Colombia": "Bogotá",
    "Argentina": "Buenos Aires",
    "Chile": "Santiago"
]

// Acceder (siempre retorna un opcional)
if let capital = capitales["Colombia"] {
    print("La capital de Colombia es \(capital)")
}

// Agregar o modificar
capitales["Perú"] = "Lima"

// Iterar
for (pais, capital) in capitales {
    print("\(pais) → \(capital)")
}
```

### Sets

```swift
// Set: colección de valores únicos sin orden
var habilidades: Set<String> = ["Swift", "UIKit", "SwiftUI", "Swift"]
print(habilidades.count)  // 3 (el duplicado "Swift" se elimina automáticamente)

// Operaciones de conjuntos
let habilidadesRequeridas: Set<String> = ["Swift", "SwiftUI", "CoreData"]
let habilidadesFaltantes = habilidadesRequeridas.subtracting(habilidades)
print(habilidadesFaltantes)  // ["CoreData"]
```

---

## Control de Flujo

### Condicionales

```swift
let puntaje = 85

// if-else clásico
if puntaje >= 90 {
    print("Excelente")
} else if puntaje >= 70 {
    print("Aprobado")
} else {
    print("Reprobado")
}

// Switch: en Swift es mucho más poderoso que en otros lenguajes
let statusCode = 404

switch statusCode {
case 200:
    print("Éxito")
case 201:
    print("Creado")
case 400:
    print("Solicitud incorrecta")
case 401, 403:
    print("No autorizado")
case 404:
    print("No encontrado")
case 500...599:
    print("Error del servidor")
default:
    print("Código desconocido: \(statusCode)")
}
// Nota: en Swift NO necesitas break, cada caso termina automáticamente
```

### Bucles

```swift
// For-in con rangos
for i in 1...5 {
    print("Iteración \(i)")  // 1, 2, 3, 4, 5
}

// For-in con rango abierto
for i in 0..<3 {
    print("Índice \(i)")  // 0, 1, 2
}

// While
var intentos = 3
while intentos > 0 {
    print("Te quedan \(intentos) intentos")
    intentos -= 1
}

// Enumerar con índice
let frutas = ["manzana", "banana", "naranja"]
for (indice, fruta) in frutas.enumerated() {
    print("\(indice): \(fruta)")
}
```

---

## Funciones

Las funciones en Swift tienen una sintaxis clara con etiquetas de argumentos que hacen el código muy legible.

```swift
// Función básica
func saludar() {
    print("¡Hola, mundo!")
}

// Con parámetros y valor de retorno
func calcularIMC(peso: Double, estatura: Double) -> Double {
    return peso / (estatura * estatura)
}

let imc = calcularIMC(peso: 70.0, estatura: 1.75)
print("Tu IMC es: \(String(format: "%.1f", imc))")

// Etiquetas externas e internas
func enviarMensaje(de remitente: String, para destinatario: String) -> String {
    return "\(remitente) → \(destinatario)"
}
let msg = enviarMensaje(de: "Ana", para: "Luis")

// Omitir etiqueta externa con _
func cuadrado(_ numero: Int) -> Int {
    return numero * numero
}
let resultado = cuadrado(5)  // Se lee más natural

// Valores por defecto
func configurarServidor(host: String = "localhost", puerto: Int = 8080) {
    print("Conectando a \(host):\(puerto)")
}
configurarServidor()                          // localhost:8080
configurarServidor(host: "api.miapp.com")     // api.miapp.com:8080
configurarServidor(host: "prod.com", puerto: 443)

// Funciones que retornan opcionales
func buscarUsuario(id: Int) -> String? {
    let usuarios = [1: "Ana", 2: "Carlos", 3: "María"]
    return usuarios[id]
}

if let usuario = buscarUsuario(id: 2) {
    print("Usuario encontrado: \(usuario)")
}
```

---

## Closures (Clausuras)

Los closures son bloques de código autocontenidos que se pueden pasar como valores. Son **fundamentales** en el desarrollo iOS: los vas a usar en animaciones, llamadas a APIs, ordenamiento de datos, callbacks y muchísimo más.

```swift
// Closure básico
let saludoClosure = { (nombre: String) -> String in
    return "¡Hola, \(nombre)!"
}
print(saludoClosure("Desarrollador"))

// Uso práctico: ordenar un array
var numeros = [3, 1, 4, 1, 5, 9, 2, 6]

// Forma completa
numeros.sort(by: { (a: Int, b: Int) -> Bool in
    return a < b
})

// Forma simplificada (trailing closure + inferencia + shorthand)
numeros.sort { $0 < $1 }

print(numeros)  // [1, 1, 2, 3, 4, 5, 6, 9]

// Uso con map, filter y reduce
let precios = [100.0, 250.0, 50.0, 300.0, 175.0]

// Aplicar descuento del 20%
let preciosConDescuento = precios.map { $0 * 0.80 }
print(preciosConDescuento)  // [80.0, 200.0, 40.0, 240.0, 140.0]

// Filtrar precios mayores a 100
let preciosAltos = precios.filter { $0 > 100 }
print(preciosAltos)  // [250.0, 300.0, 175.0]

// Sumar todos los precios
let total = precios.reduce(0) { $0 + $1 }
print("Total: $\(total)")  // Total: $875.0

// Encadenar operaciones (muy común en apps reales)
let totalConDescuento = precios
    .filter { $0 > 100 }
    .map { $0 * 0.80 }
    .reduce(0, +)
print("Total con descuento: $\(totalConDescuento)")  // $580.0
```

---

## Enumeraciones

Las enumeraciones en Swift son extremadamente poderosas comparadas con otros lenguajes. Pueden tener valores asociados, propiedades computadas y métodos.

```swift
// Enum básico
enum EstadoPedido {
    case pendiente
    case enProceso
    case enviado
    case entregado
    case cancelado
}

var miPedido = EstadoPedido.pendiente
miPedido = .enviado  // Swift infiere el tipo

// Switch exhaustivo (el compilador te obliga a cubrir todos los casos)
switch miPedido {
case .pendiente:
    print("Tu pedido está pendiente")
case .enProceso:
    print("Estamos preparando tu pedido")
case .enviado:
    print("Tu pedido va en camino")
case .entregado:
    print("¡Pedido entregado!")
case .cancelado:
    print("Pedido cancelado")
}

// Enum con valores asociados (muy usado para manejar resultados de red)
enum ResultadoRed {
    case exito(datos: Data, codigo: Int)
    case error(mensaje: String, codigo: Int)
    case sinConexion
}

let respuesta = ResultadoRed.exito(datos: Data(), codigo: 200)

switch respuesta {
case .exito(let datos, let codigo):
    print("Éxito (\(codigo)): \(datos.count) bytes recibidos")
case .error(let mensaje, let codigo):
    print("Error \(codigo): \(mensaje)")
case .sinConexion:
    print("Verifica tu conexión a internet")
}

// Enum con Raw Values
enum Moneda: String {
    case pesoMexicano = "MXN"
    case pesoColombiano = "COP"
    case pesoArgentino = "ARS"
    case solPeruano = "PEN"
    case dolar = "USD"
}

let moneda = Moneda.pesoMexicano
print("Código: \(moneda.rawValue)")  // "MXN"

// Crear desde raw value (retorna opcional)
if let monedaDesdeAPI = Moneda(rawValue: "COP") {
    print("Moneda válida: \(monedaDesdeAPI)")
}
```

---

## Structs vs Classes

Entender la diferencia entre structs (tipos de valor) y classes (tipos de referencia) es **esencial** para el desarrollo iOS. SwiftUI trabaja principalmente con structs, UIKit con classes.

```swift
// STRUCT: Tipo de valor (se COPIA al asignar)
struct Coordenada {
    var latitud: Double
    var longitud: Double
    
    // Propiedad computada
    var descripcion: String {
        return "(\(latitud), \(longitud))"
    }
    
    //