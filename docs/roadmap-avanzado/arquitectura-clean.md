---
sidebar_position: 1
title: Arquitectura Clean
---

# Arquitectura Clean en iOS

## ¿Qué es Clean Architecture?

Clean Architecture es un conjunto de principios propuestos por Robert C. Martin (Uncle Bob) que buscan crear sistemas de software con **separación clara de responsabilidades**, donde la lógica de negocio es completamente independiente de frameworks, interfaces de usuario y bases de datos.

La idea central es simple pero poderosa: **tu código de negocio no debería saber que existe UIKit, SwiftUI, Core Data ni ningún framework externo**. Esto se logra organizando el código en capas concéntricas donde las dependencias siempre apuntan hacia adentro, hacia las reglas de negocio.

```
┌─────────────────────────────────────────────┐
│              Presentation Layer              │
│         (ViewModels, Views, UIKit)           │
│   ┌─────────────────────────────────────┐   │
│   │           Domain Layer              │   │
│   │    (Use Cases, Entities, Repos      │   │
│   │         Interfaces)                 │   │
│   │   ┌─────────────────────────────┐   │   │
│   │   │        Data Layer           │   │   │
│   │   │  (Repos Implementation,     │   │   │
│   │   │   API, Database, DTOs)      │   │   │
│   │   └─────────────────────────────┘   │   │
│   └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘

        La dependencia apunta → hacia adentro
```

## ¿Por qué es importante para un dev iOS en LATAM?

El mercado de desarrollo iOS en Latinoamérica ha madurado enormemente. Las empresas —desde fintechs en Colombia y México hasta startups en Argentina y Chile— ya no buscan solo "alguien que haga apps". Buscan **ingenieros de software que piensen en arquitectura**.

Estas son las razones concretas por las que dominar Clean Architecture te posiciona mejor:

1. **Las entrevistas técnicas lo exigen**: Empresas como Mercado Libre, Rappi, Globant, Kavak y consultoras internacionales con presencia en LATAM evalúan conocimiento arquitectónico. Si no puedes explicar por qué separas capas, quedas fuera.

2. **Proyectos reales crecen rápido**: Una app de delivery que empieza con 5 pantallas termina con 50. Sin arquitectura clara, el código se convierte en un monolito imposible de mantener.

3. **Facilita el trabajo en equipo**: En equipos distribuidos (muy comunes en LATAM por el trabajo remoto), tener fronteras claras entre capas permite que varios desarrolladores trabajen en paralelo sin pisarse.

4. **Testabilidad real**: Clean Architecture hace que escribir unit tests sea natural, no un dolor de cabeza. Esto eleva la calidad del producto y tu perfil profesional.

5. **Independencia tecnológica**: Si mañana necesitas migrar de UIKit a SwiftUI, de Alamofire a async/await nativo, o de Core Data a SwiftData, solo cambias la capa externa. El negocio no se toca.

## Las tres capas fundamentales

### 1. Domain Layer (El corazón)

Esta es la capa más importante y la más **pura**. No importa ningún framework. Aquí viven:

- **Entities**: Los modelos de negocio
- **Use Cases (Interactors)**: Las reglas de negocio
- **Repository Protocols**: Los contratos que definen qué datos necesitamos

```swift
// MARK: - Entity (Modelo de negocio puro)
struct Product {
    let id: String
    let name: String
    let price: Decimal
    let currency: Currency
    let isAvailable: Bool
    
    enum Currency: String {
        case mxn = "MXN"
        case cop = "COP"
        case ars = "ARS"
        case usd = "USD"
    }
    
    var formattedPrice: String {
        "\(currency.rawValue) \(price)"
    }
}
```

```swift
// MARK: - Repository Protocol (Contrato)
// Domain define QUÉ necesita, no CÓMO se obtiene
protocol ProductRepositoryProtocol {
    func fetchProducts() async throws -> [Product]
    func fetchProduct(byId id: String) async throws -> Product
    func searchProducts(query: String) async throws -> [Product]
}
```

```swift
// MARK: - Use Case (Regla de negocio)
protocol FetchAvailableProductsUseCaseProtocol {
    func execute() async throws -> [Product]
}

final class FetchAvailableProductsUseCase: FetchAvailableProductsUseCaseProtocol {
    
    private let repository: ProductRepositoryProtocol
    
    init(repository: ProductRepositoryProtocol) {
        self.repository = repository
    }
    
    func execute() async throws -> [Product] {
        let allProducts = try await repository.fetchProducts()
        
        // Regla de negocio: solo devolvemos productos disponibles
        // y los ordenamos por precio (menor a mayor)
        return allProducts
            .filter { $0.isAvailable }
            .sorted { $0.price < $1.price }
    }
}
```

> **Nota clave**: Observa que `FetchAvailableProductsUseCase` no sabe si los datos vienen de una API REST, de Core Data, de un archivo JSON o de Firebase. Solo sabe que existe un repositorio que cumple un contrato. Esa es la magia.

### 2. Data Layer (El mundo exterior)

Aquí implementamos los contratos definidos en Domain. Esta capa conoce los detalles técnicos: APIs, bases de datos, caché, etc.

```swift
// MARK: - DTO (Data Transfer Object)
// Representa la respuesta exacta de la API
struct ProductDTO: Decodable {
    let id: String
    let name: String
    let price: Double
    let currencyCode: String
    let status: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case price
        case currencyCode = "currency_code"
        case status
    }
}

// MARK: - Mapper (DTO → Entity)
extension ProductDTO {
    func toDomain() -> Product {
        Product(
            id: id,
            name: name,
            price: Decimal(price),
            currency: Product.Currency(rawValue: currencyCode) ?? .usd,
            isAvailable: status == "active"
        )
    }
}
```

```swift
// MARK: - Data Source Protocol
protocol ProductRemoteDataSourceProtocol {
    func getProducts() async throws -> [ProductDTO]
    func getProduct(id: String) async throws -> ProductDTO
    func searchProducts(query: String) async throws -> [ProductDTO]
}

// MARK: - Implementación concreta del Data Source
final class ProductRemoteDataSource: ProductRemoteDataSourceProtocol {
    
    private let baseURL = "https://api.mitienda.com/v1"
    private let session: URLSession
    
    init(session: URLSession = .shared) {
        self.session = session
    }
    
    func getProducts() async throws -> [ProductDTO] {
        guard let url = URL(string: "\(baseURL)/products") else {
            throw NetworkError.invalidURL
        }
        
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError
        }
        
        return try JSONDecoder().decode([ProductDTO].self, from: data)
    }
    
    func getProduct(id: String) async throws -> ProductDTO {
        guard let url = URL(string: "\(baseURL)/products/\(id)") else {
            throw NetworkError.invalidURL
        }
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(ProductDTO.self, from: data)
    }
    
    func searchProducts(query: String) async throws -> [ProductDTO] {
        guard let encoded = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let url = URL(string: "\(baseURL)/products?search=\(encoded)") else {
            throw NetworkError.invalidURL
        }
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode([ProductDTO].self, from: data)
    }
}

// MARK: - Errores de red
enum NetworkError: LocalizedError {
    case invalidURL
    case serverError
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "URL inválida"
        case .serverError: return "Error del servidor"
        case .decodingError: return "Error al procesar datos"
        }
    }
}
```

```swift
// MARK: - Repository Implementation
// Aquí conectamos Domain con Data
final class ProductRepository: ProductRepositoryProtocol {
    
    private let remoteDataSource: ProductRemoteDataSourceProtocol
    private let localDataSource: ProductLocalDataSourceProtocol?
    
    init(
        remoteDataSource: ProductRemoteDataSourceProtocol,
        localDataSource: ProductLocalDataSourceProtocol? = nil
    ) {
        self.remoteDataSource = remoteDataSource
        self.localDataSource = localDataSource
    }
    
    func fetchProducts() async throws -> [Product] {
        // Estrategia: intentar caché primero, luego red
        if let cached = try? await localDataSource?.getCachedProducts(),
           !cached.isEmpty {
            return cached.map { $0.toDomain() }
        }
        
        let dtos = try await remoteDataSource.getProducts()
        
        // Guardar en caché para la próxima vez
        try? await localDataSource?.save(products: dtos)
        
        return dtos.map { $0.toDomain() }
    }
    
    func fetchProduct(byId id: String) async throws -> Product {
        let dto = try await remoteDataSource.getProduct(id: id)
        return dto.toDomain()
    }
    
    func searchProducts(query: String) async throws -> [Product] {
        let dtos = try await remoteDataSource.searchProducts(query: query)
        return dtos.map { $0.toDomain() }
    }
}
```

### 3. Presentation Layer (Lo que ve el usuario)

Aquí vive la interfaz de usuario y los ViewModels que la alimentan. Esta capa solo conoce a Domain (use cases), nunca a Data directamente.

```swift
// MARK: - ViewModel
@MainActor
final class ProductListViewModel: ObservableObject {
    
    // MARK: - Published State
    @Published private(set) var products: [ProductItemViewModel] = []
    @Published private(set) var isLoading = false
    @Published private(set) var errorMessage: String?
    @Published var searchQuery = ""
    
    // MARK: - Dependencies (solo Use Cases)
    private let fetchAvailableProducts: FetchAvailableProductsUseCaseProtocol
    private let searchProducts: SearchProductsUseCaseProtocol
    
    // MARK: - Init
    init(
        fetchAvailableProducts: FetchAvailableProductsUseCaseProtocol,
        searchProducts: SearchProductsUseCaseProtocol
    ) {
        self.fetchAvailableProducts = fetchAvailableProducts
        self.searchProducts = searchProducts
    }
    
    // MARK: - Actions
    func onAppear() {
        Task {
            await loadProducts()
        }
    }
    
    func onSearch() {
        Task {
            await performSearch()
        }
    }
    
    func onRetry() {
        errorMessage = nil
        Task {
            await loadProducts()
        }
    }
    
    // MARK: - Private
    private func loadProducts() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let domainProducts = try await fetchAvailableProducts.execute()
            products = domainProducts.map { ProductItemViewModel(product: $0) }
        } catch {
            errorMessage = "No pudimos cargar los productos. Verifica tu conexión."
        }
        
        isLoading = false
    }
    
    private func performSearch() async {
        guard !searchQuery.trimmingCharacters(in: .whitespaces).isEmpty else {
            await loadProducts()
            return
        }
        
        isLoading = true
        
        do {
            let results = try await searchProducts.execute(query: searchQuery)
            products = results.map { ProductItemViewModel(product: $0) }
        } catch {
            errorMessage = "Error al buscar productos."
        }
        
        isLoading = false
    }
}

// MARK: - Item ViewModel (para la vista)
struct ProductItemViewModel: Identifiable {
    let id: String
    let name: String
    let displayPrice: String
    
    init(product: Product) {
        self.id = product.id
        self.name = product.name
        self.displayPrice = product.formattedPrice
    }
}
```

```swift
// MARK: - SwiftUI View
struct ProductListView: View {
    
    @StateObject private var viewModel: ProductListViewModel
    
    init(viewModel: ProductListViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }
    
    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView("Cargando productos...")
                } else if let error = viewModel.errorMessage {
                    errorView(message: error)
                } else {
                    productList
                }
            }
            .navigationTitle("Productos")
            .searchable(text: $viewModel.searchQuery, prompt: "Buscar productos")
            .onSubmit(of: .search) {
                viewModel.onSearch()
            }
        }
        .onAppear {
            viewModel.onAppear()
        }
    }
    
    private var productList: some View {
        List(viewModel.products) { product in
            HStack {
                Text(product.name)
                    .font(.headline)
                Spacer()
                Text(product.displayPrice)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
    }
    
    private func errorView(message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "wifi.slash")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)
            
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            
            Button("Reintentar") {
                viewModel.onRetry()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}
```

## Inyección de dependencias: conectando todo

El punto donde todo se ensambla es crucial. Aquí es donde creamos las instancias concretas y las inyectamos:

```swift
// MARK: - Dependency Container
final class AppDIContainer {
    
    // MARK: - Data Layer
    private lazy var productRemoteDataSource: ProductRemoteDataSourceProtocol = {
        ProductRemoteDataSource()
    }()
    
    private lazy var productRepository: ProductRepositoryProtocol = {
        ProductRepository(remoteDataSource: productRemoteDataSource)
    }()
    
    // MARK: - Domain Layer (Use Cases)
    private func makeFetchAvail