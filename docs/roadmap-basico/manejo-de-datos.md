---
sidebar_position: 1
title: Manejo De Datos
---

# Manejo de Datos en iOS

## ¿Qué es el manejo de datos?

El manejo de datos es la columna vertebral de cualquier aplicación iOS. Se refiere a todas las técnicas, herramientas y patrones que usamos para **crear, leer, almacenar, transformar y transmitir información** dentro de nuestras aplicaciones. Desde una simple lista de tareas hasta una app de fintech que procesa miles de transacciones, todo depende de cómo gestionamos los datos.

Como desarrollador iOS, vas a interactuar con datos constantemente: los que el usuario ingresa, los que llegan de un servidor, los que persistes localmente y los que compartes entre pantallas. Dominar este tema no es opcional — es **fundamental**.

---

## ¿Por qué es crucial para un dev iOS en LATAM?

En Latinoamérica, el contexto de desarrollo tiene particularidades que hacen el manejo de datos aún más relevante:

- **Conectividad intermitente**: Muchos usuarios en la región no cuentan con conexión estable. Saber almacenar datos localmente y sincronizar después es una ventaja competitiva enorme.
- **Diversidad de dispositivos**: No todos usan el último iPhone. Optimizar el uso de memoria y almacenamiento es clave para ofrecer buena experiencia en dispositivos con recursos limitados.
- **Apps de alto impacto regional**: Fintech, delivery, salud, educación — los sectores que más crecen en LATAM dependen de un manejo robusto de datos.
- **Oportunidades laborales**: Empresas como Mercado Libre, Rappi, Nubank y startups locales buscan devs que dominen persistencia, networking y arquitectura de datos.

---

## Los pilares del manejo de datos en iOS

### 1. Tipos de datos y estructuras en Swift

Swift es un lenguaje fuertemente tipado. Entender sus tipos de datos es el primer paso.

```swift
// Tipos básicos
let nombre: String = "Carlos"
let edad: Int = 28
let saldo: Double = 15000.50
let estaActivo: Bool = true

// Colecciones
var frutas: [String] = ["Mango", "Papaya", "Guayaba"]
var capitales: [String: String] = [
    "México": "CDMX",
    "Colombia": "Bogotá",
    "Argentina": "Buenos Aires"
]

// Tuplas
let coordenadas: (Double, Double) = (19.4326, -99.1332)
```

### 2. Modelos de datos con Structs y Codable

En el mundo real, los datos tienen forma. Modelarlos correctamente es esencial.

```swift
struct Usuario: Codable {
    let id: Int
    let nombre: String
    let email: String
    let pais: String
    let saldoDisponible: Double

    enum CodingKeys: String, CodingKey {
        case id
        case nombre = "full_name"
        case email
        case pais = "country"
        case saldoDisponible = "available_balance"
    }
}
```

El protocolo `Codable` (que combina `Encodable` y `Decodable`) te permite convertir datos entre JSON y objetos Swift de manera sencilla:

```swift
// Decodificar JSON a objeto Swift
let json = """
{
    "id": 1,
    "full_name": "María González",
    "email": "maria@ejemplo.com",
    "country": "Colombia",
    "available_balance": 250000.75
}
""".data(using: .utf8)!

do {
    let decoder = JSONDecoder()
    let usuario = try decoder.decode(Usuario.self, from: json)
    print("Usuario: \(usuario.nombre), País: \(usuario.pais)")
} catch {
    print("Error al decodificar: \(error.localizedDescription)")
}
```

```swift
// Codificar objeto Swift a JSON
let nuevoUsuario = Usuario(
    id: 2,
    nombre: "Pedro Ramírez",
    email: "pedro@ejemplo.com",
    pais: "México",
    saldoDisponible: 18500.00
)

do {
    let encoder = JSONEncoder()
    encoder.outputFormatting = .prettyPrinted
    let data = try encoder.encode(nuevoUsuario)
    if let jsonString = String(data: data, encoding: .utf8) {
        print(jsonString)
    }
} catch {
    print("Error al codificar: \(error.localizedDescription)")
}
```

### 3. Persistencia local de datos

Aquí es donde muchos devs junior tropiezan. iOS ofrece múltiples opciones para almacenar datos localmente, cada una con su caso de uso ideal.

#### UserDefaults — Para datos simples y configuraciones

```swift
// Guardar
UserDefaults.standard.set("es_MX", forKey: "idioma_preferido")
UserDefaults.standard.set(true, forKey: "modo_oscuro")
UserDefaults.standard.set(5, forKey: "numero_de_intentos")

// Leer
let idioma = UserDefaults.standard.string(forKey: "idioma_preferido") ?? "es"
let modoOscuro = UserDefaults.standard.bool(forKey: "modo_oscuro")
let intentos = UserDefaults.standard.integer(forKey: "numero_de_intentos")

print("Idioma: \(idioma), Modo oscuro: \(modoOscuro), Intentos: \(intentos)")
```

> ⚠️ **Precaución**: UserDefaults NO es para datos sensibles como contraseñas o tokens. Para eso existe **Keychain**.

#### Keychain — Para datos sensibles

```swift
import Security

struct KeychainHelper {

    static func guardar(servicio: String, cuenta: String, datos: Data) -> Bool {
        // Primero eliminamos cualquier dato existente
        eliminar(servicio: servicio, cuenta: cuenta)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: servicio,
            kSecAttrAccount as String: cuenta,
            kSecValueData as String: datos
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    static func leer(servicio: String, cuenta: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: servicio,
            kSecAttrAccount as String: cuenta,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var resultado: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &resultado)

        guard status == errSecSuccess else { return nil }
        return resultado as? Data
    }

    static func eliminar(servicio: String, cuenta: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: servicio,
            kSecAttrAccount as String: cuenta
        ]

        SecItemDelete(query as CFDictionary)
    }
}

// Uso
let token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
if let datos = token.data(using: .utf8) {
    let guardado = KeychainHelper.guardar(
        servicio: "com.miapp.auth",
        cuenta: "token_acceso",
        datos: datos
    )
    print("Token guardado: \(guardado)")
}

// Recuperar
if let datosRecuperados = KeychainHelper.leer(
    servicio: "com.miapp.auth",
    cuenta: "token_acceso"
),
   let tokenRecuperado = String(data: datosRecuperados, encoding: .utf8) {
    print("Token recuperado: \(tokenRecuperado)")
}
```

#### FileManager — Para archivos y datos más grandes

```swift
struct ArchivoManager {

    static var directorio: URL {
        FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first!
    }

    static func guardarJSON<T: Encodable>(_ objeto: T, nombreArchivo: String) throws {
        let url = directorio.appendingPathComponent(nombreArchivo)
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        let datos = try encoder.encode(objeto)
        try datos.write(to: url, options: .atomic)
        print("Archivo guardado en: \(url.path)")
    }

    static func cargarJSON<T: Decodable>(nombreArchivo: String, tipo: T.Type) throws -> T {
        let url = directorio.appendingPathComponent(nombreArchivo)
        let datos = try Data(contentsOf: url)
        return try JSONDecoder().decode(tipo, from: datos)
    }

    static func existeArchivo(nombreArchivo: String) -> Bool {
        let url = directorio.appendingPathComponent(nombreArchivo)
        return FileManager.default.fileExists(atPath: url.path)
    }
}

// Ejemplo práctico: guardar una lista de productos
struct Producto: Codable {
    let id: Int
    let nombre: String
    let precio: Double
    let moneda: String
}

let productos = [
    Producto(id: 1, nombre: "Tacos al pastor", precio: 85.00, moneda: "MXN"),
    Producto(id: 2, nombre: "Arepa reina pepiada", precio: 15000.00, moneda: "COP"),
    Producto(id: 3, nombre: "Empanada criolla", precio: 350.00, moneda: "ARS")
]

// Guardar
do {
    try ArchivoManager.guardarJSON(productos, nombreArchivo: "productos.json")
} catch {
    print("Error al guardar: \(error)")
}

// Cargar
do {
    let productosRecuperados = try ArchivoManager.cargarJSON(
        nombreArchivo: "productos.json",
        tipo: [Producto].self
    )
    productosRecuperados.forEach { producto in
        print("\(producto.nombre): \(producto.precio) \(producto.moneda)")
    }
} catch {
    print("Error al cargar: \(error)")
}
```

### 4. SwiftData — Persistencia moderna (iOS 17+)

SwiftData es el sucesor moderno de Core Data, con una API mucho más limpia e integrada con SwiftUI.

```swift
import SwiftData

@Model
class Tarea {
    var titulo: String
    var descripcion: String
    var completada: Bool
    var fechaCreacion: Date
    var prioridad: Int

    init(titulo: String, descripcion: String, prioridad: Int = 0) {
        self.titulo = titulo
        self.descripcion = descripcion
        self.completada = false
        self.fechaCreacion = Date()
        self.prioridad = prioridad
    }
}
```

```swift
import SwiftUI
import SwiftData

struct ListaTareasView: View {
    @Environment(\.modelContext) private var contexto
    @Query(sort: \Tarea.fechaCreacion, order: .reverse) private var tareas: [Tarea]
    @State private var mostrarFormulario = false

    var body: some View {
        NavigationStack {
            List {
                ForEach(tareas) { tarea in
                    HStack {
                        Image(systemName: tarea.completada
                              ? "checkmark.circle.fill"
                              : "circle")
                            .foregroundColor(tarea.completada ? .green : .gray)
                            .onTapGesture {
                                tarea.completada.toggle()
                            }

                        VStack(alignment: .leading) {
                            Text(tarea.titulo)
                                .font(.headline)
                                .strikethrough(tarea.completada)
                            Text(tarea.descripcion)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .onDelete(perform: eliminarTareas)
            }
            .navigationTitle("Mis Tareas")
            .toolbar {
                Button(action: agregarTareaEjemplo) {
                    Image(systemName: "plus")
                }
            }
        }
    }

    private func agregarTareaEjemplo() {
        let nueva = Tarea(
            titulo: "Nueva tarea",
            descripcion: "Creada el \(Date().formatted())",
            prioridad: 1
        )
        contexto.insert(nueva)
    }

    private func eliminarTareas(en offsets: IndexSet) {
        for index in offsets {
            contexto.delete(tareas[index])
        }
    }
}

// En tu App principal
@main
struct MiApp: App {
    var body: some Scene {
        WindowGroup {
            ListaTareasView()
        }
        .modelContainer(for: Tarea.self)
    }
}
```

### 5. Consumo de APIs (Networking)

La mayoría de las apps necesitan comunicarse con servidores. Aquí un patrón robusto y reutilizable:

```swift
enum NetworkError: Error, LocalizedError {
    case urlInvalida
    case sinRespuesta
    case codigoHTTP(Int)
    case decodificacion(Error)
    case sinConexion

    var errorDescription: String? {
        switch self {
        case .urlInvalida:
            return "La URL proporcionada no es válida"
        case .sinRespuesta:
            return "No se recibió respuesta del servidor"
        case .codigoHTTP(let codigo):
            return "Error del servidor: código \(codigo)"
        case .decodificacion(let error):
            return "Error al procesar datos: \(error.localizedDescription)"
        case .sinConexion:
            return "Sin conexión a internet. Verifica tu red."
        }
    }
}

class ServicioRed {

    static let compartido = ServicioRed()
    private let sesion: URLSession

    private init() {
        let configuracion = URLSessionConfiguration.default
        configuracion.timeoutIntervalForRequest = 30
        configuracion.requestCachePolicy = .returnCacheDataElseLoad
        self.sesion = URLSession(configuration: configuracion)
    }

    func obtener<T: Decodable>(
        url urlString: String,
        tipo: T.Type,
        headers: [String: String] = [:]
    ) async throws -> T {
        guard let url = URL(string: urlString) else {
            throw NetworkError.urlInvalida
        }

        var solicitud = URLRequest(url: url)
        solicitud.httpMethod = "GET"
        solicitud.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // Agregar headers personalizados
        headers.forEach { clave, valor in
            solicitud.setValue(valor, forHTTPHeaderField: clave)
        }

        let (datos, respuesta) = try await sesion.data(for: solicitud)

        guard let httpRespuesta = respuesta as? HTTPURLResponse else {
            throw NetworkError.sinRespuesta
        }

        guard (200...299).contains(httpRespuesta.statusCode) else {
            throw NetworkError.codigoHTTP(httpRespuesta.statusCode)
        }

        do {
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convert