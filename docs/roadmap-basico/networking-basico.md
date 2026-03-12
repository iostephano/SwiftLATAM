---
sidebar_position: 1
title: Networking Basico
---

# Networking Básico en iOS

## ¿Qué es el Networking en iOS?

El **networking** (o comunicación en red) es la capacidad que tiene tu aplicación de enviar y recibir datos a través de Internet. Cada vez que abres Instagram y ves fotos nuevas, cuando revisas el clima en tu app favorita, o cuando inicias sesión en cualquier servicio, tu aplicación está haciendo **peticiones de red** a un servidor remoto.

En el desarrollo iOS, el networking es el puente entre tu aplicación y el mundo exterior. Sin él, tu app sería simplemente una caja cerrada sin acceso a información actualizada.

## ¿Por qué es fundamental para un dev iOS en LATAM?

En Latinoamérica, el networking cobra una relevancia especial por varias razones:

- **Conectividad variable**: Muchos usuarios en LATAM navegan con conexiones 3G/4G inestables. Saber manejar errores de red, timeouts y reintentos es **crítico** para ofrecer una buena experiencia.
- **Consumo de datos**: Una parte significativa de los usuarios tiene planes de datos limitados. Optimizar las peticiones y cachear respuestas no es un lujo, es una necesidad.
- **Integración con APIs locales**: Ya sea que trabajes con pasarelas de pago como MercadoPago, Stripe para LATAM, o servicios gubernamentales, vas a consumir APIs REST constantemente.
- **El mercado lo exige**: Prácticamente el 100% de las ofertas laborales para iOS en la región requieren experiencia con consumo de APIs. Es una habilidad no negociable.

## Fundamentos: ¿Cómo funciona una petición HTTP?

Antes de escribir código, entendamos el flujo básico:

```
Tu App  →  Petición HTTP (Request)  →  Servidor
Tu App  ←  Respuesta HTTP (Response) ←  Servidor
```

Una petición HTTP tiene estos componentes esenciales:

| Componente | Descripción | Ejemplo |
|---|---|---|
| **URL** | Dirección del recurso | `https://api.example.com/users` |
| **Método HTTP** | Acción a realizar | `GET`, `POST`, `PUT`, `DELETE` |
| **Headers** | Metadatos de la petición | `Content-Type: application/json` |
| **Body** | Datos enviados (opcional) | `{"nombre": "Carlos", "email": "carlos@mail.com"}` |

Los métodos más comunes son:

- **GET**: Obtener datos (leer)
- **POST**: Crear datos nuevos
- **PUT/PATCH**: Actualizar datos existentes
- **DELETE**: Eliminar datos

## URLSession: La herramienta nativa de Apple

`URLSession` es la clase fundamental que Apple proporciona para realizar peticiones de red. No necesitas ninguna librería externa para empezar — todo viene incluido en el SDK de iOS.

### Tu primera petición GET

Vamos a consumir una API pública gratuita para obtener una lista de tareas pendientes (todos):

```swift
import Foundation

// 1. Crear la URL
guard let url = URL(string: "https://jsonplaceholder.typicode.com/todos/1") else {
    print("URL inválida")
    return
}

// 2. Crear la tarea de red (data task)
let task = URLSession.shared.dataTask(with: url) { data, response, error in
    // 3. Verificar que no haya errores
    if let error = error {
        print("Error en la petición: \(error.localizedDescription)")
        return
    }
    
    // 4. Verificar el código de respuesta HTTP
    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        print("Respuesta del servidor inválida")
        return
    }
    
    // 5. Verificar que tengamos datos
    guard let data = data else {
        print("No se recibieron datos")
        return
    }
    
    // 6. Convertir los datos a texto legible
    if let jsonString = String(data: data, encoding: .utf8) {
        print("Respuesta: \(jsonString)")
    }
}

// 7. ¡No olvides iniciar la tarea!
task.resume()
```

:::caution Punto crítico
El error más común de principiantes es olvidar llamar a `task.resume()`. Sin esa línea, la petición **nunca se ejecuta**. URLSession crea las tareas en estado suspendido por defecto.
:::

## Decodificando JSON con Codable

Las APIs modernas devuelven datos en formato **JSON**. Swift tiene un protocolo llamado `Codable` que convierte JSON a objetos Swift de manera elegante y segura.

### Paso 1: Definir el modelo

```swift
struct Todo: Codable {
    let userId: Int
    let id: Int
    let title: String
    let completed: Bool
}
```

### Paso 2: Decodificar la respuesta

```swift
func fetchTodo(completion: @escaping (Result<Todo, Error>) -> Void) {
    guard let url = URL(string: "https://jsonplaceholder.typicode.com/todos/1") else {
        return
    }
    
    URLSession.shared.dataTask(with: url) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }
        
        guard let data = data else {
            completion(.failure(URLError(.badServerResponse)))
            return
        }
        
        do {
            let decoder = JSONDecoder()
            let todo = try decoder.decode(Todo.self, from: data)
            completion(.success(todo))
        } catch {
            completion(.failure(error))
        }
    }.resume()
}

// Uso:
fetchTodo { result in
    switch result {
    case .success(let todo):
        print("Tarea: \(todo.title)")
        print("¿Completada?: \(todo.completed)")
    case .failure(let error):
        print("Error: \(error.localizedDescription)")
    }
}
```

### Cuando las claves del JSON no coinciden con Swift

Es muy común que las APIs usen `snake_case` mientras que Swift usa `camelCase`. Tienes dos opciones:

```swift
// Opción 1: Configurar el decoder (recomendado para casos simples)
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase

// Opción 2: Usar CodingKeys (control total)
struct User: Codable {
    let id: Int
    let fullName: String
    let profileImageUrl: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case fullName = "full_name"
        case profileImageUrl = "profile_image_url"
    }
}
```

## Peticiones POST: Enviando datos al servidor

No todo es leer datos. Frecuentemente necesitarás **enviar** información:

```swift
struct NewPost: Codable {
    let title: String
    let body: String
    let userId: Int
}

struct CreatedPost: Codable {
    let id: Int
    let title: String
    let body: String
    let userId: Int
}

func createPost(_ post: NewPost, completion: @escaping (Result<CreatedPost, Error>) -> Void) {
    guard let url = URL(string: "https://jsonplaceholder.typicode.com/posts") else {
        return
    }
    
    // 1. Configurar la petición
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    // 2. Codificar el cuerpo de la petición
    do {
        let encoder = JSONEncoder()
        request.httpBody = try encoder.encode(post)
    } catch {
        completion(.failure(error))
        return
    }
    
    // 3. Ejecutar la petición
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }
        
        guard let httpResponse = response as? HTTPURLResponse else {
            completion(.failure(URLError(.badServerResponse)))
            return
        }
        
        // Para POST exitoso, el servidor típicamente responde con 201 (Created)
        print("Código de estado: \(httpResponse.statusCode)")
        
        guard let data = data else {
            completion(.failure(URLError(.badServerResponse)))
            return
        }
        
        do {
            let createdPost = try JSONDecoder().decode(CreatedPost.self, from: data)
            completion(.success(createdPost))
        } catch {
            completion(.failure(error))
        }
    }.resume()
}

// Uso:
let newPost = NewPost(title: "Hola desde LATAM", body: "Aprendiendo networking en iOS", userId: 1)
createPost(newPost) { result in
    switch result {
    case .success(let post):
        print("Post creado con ID: \(post.id)")
    case .failure(let error):
        print("Error al crear post: \(error)")
    }
}
```

## Networking moderno con async/await

A partir de iOS 15, Swift introdujo **concurrencia estructurada** que simplifica enormemente el código de networking. Adiós a los closures anidados (callback hell):

```swift
struct TodoService {
    
    func fetchTodo(id: Int) async throws -> Todo {
        guard let url = URL(string: "https://jsonplaceholder.typicode.com/todos/\(id)") else {
            throw URLError(.badURL)
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
        
        return try JSONDecoder().decode(Todo.self, from: data)
    }
    
    func fetchAllTodos() async throws -> [Todo] {
        guard let url = URL(string: "https://jsonplaceholder.typicode.com/todos") else {
            throw URLError(.badURL)
        }
        
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([Todo].self, from: data)
    }
    
    func createPost(_ post: NewPost) async throws -> CreatedPost {
        guard let url = URL(string: "https://jsonplaceholder.typicode.com/posts") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(post)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(CreatedPost.self, from: data)
    }
}
```

### Uso en SwiftUI con async/await

```swift
import SwiftUI

struct TodoListView: View {
    @State private var todos: [Todo] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    private let service = TodoService()
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Cargando tareas...")
                } else if let error = errorMessage {
                    VStack(spacing: 16) {
                        Image(systemName: "wifi.slash")
                            .font(.largeTitle)
                            .foregroundColor(.red)
                        Text(error)
                            .multilineTextAlignment(.center)
                        Button("Reintentar") {
                            Task { await loadTodos() }
                        }
                    }
                    .padding()
                } else {
                    List(todos, id: \.id) { todo in
                        HStack {
                            Image(systemName: todo.completed ? "checkmark.circle.fill" : "circle")
                                .foregroundColor(todo.completed ? .green : .gray)
                            Text(todo.title)
                                .strikethrough(todo.completed)
                        }
                    }
                }
            }
            .navigationTitle("Mis Tareas")
            .task {
                await loadTodos()
            }
        }
    }
    
    private func loadTodos() async {
        isLoading = true
        errorMessage = nil
        
        do {
            todos = try await service.fetchAllTodos()
        } catch {
            errorMessage = "No se pudieron cargar las tareas.\nVerifica tu conexión a Internet."
        }
        
        isLoading = false
    }
}
```

:::tip Buena práctica
Siempre muestra al usuario un estado de carga, un estado de error con opción de reintento, y el contenido exitoso. Estos tres estados son especialmente importantes en LATAM donde la conectividad puede fallar.
:::

## Construyendo un Network Layer reutilizable

En proyectos reales, no querrás repetir el mismo código de networking en cada pantalla. Aquí tienes una estructura básica pero sólida para un **network layer** que puedes usar en tus proyectos:

```swift
// MARK: - Errores personalizados
enum NetworkError: LocalizedError {
    case invalidURL
    case noData
    case decodingError
    case serverError(statusCode: Int)
    case noInternetConnection
    case unknown(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "La URL proporcionada no es válida"
        case .noData:
            return "No se recibieron datos del servidor"
        case .decodingError:
            return "Error al procesar la respuesta del servidor"
        case .serverError(let code):
            return "Error del servidor (código: \(code))"
        case .noInternetConnection:
            return "Sin conexión a Internet. Verifica tu red."
        case .unknown(let error):
            return error.localizedDescription
        }
    }
}

// MARK: - Métodos HTTP
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
    case patch = "PATCH"
}

// MARK: - Endpoint
struct Endpoint {
    let path: String
    let method: HTTPMethod
    let headers: [String: String]?
    let body: Data?
    
    init(
        path: String,
        method: HTTPMethod = .get,
        headers: [String: String]? = nil,
        body: Data? = nil
    ) {
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
    }
}

// MARK: - Network Manager
final class NetworkManager {
    static let shared = NetworkManager()
    
    private let baseURL = "https://jsonplaceholder.typicode.com"
    private let session: URLSession
    private let decoder: JSONDecoder
    
    private init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        configuration.waitsForConnectivity = true // Espera conectividad en lugar de fallar inmediato
        
        self.session = URLSession(configuration: configuration)
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
    }
    
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T