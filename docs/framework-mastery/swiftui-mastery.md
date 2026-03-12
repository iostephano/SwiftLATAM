---
sidebar_position: 1
title: Swiftui Mastery
---

# SwiftUI Mastery: Dominio Completo del Framework Declarativo de Apple

## ¿Qué es SwiftUI y por qué dominarlo cambia todo?

SwiftUI es el framework **declarativo** de Apple para construir interfaces de usuario en todas sus plataformas: iOS, iPadOS, macOS, watchOS y tvOS. Introducido en 2019, representa un cambio de paradigma fundamental respecto a UIKit: en lugar de decirle al sistema **cómo** construir la interfaz paso a paso (imperativo), le describes **qué** quieres ver (declarativo).

Para un desarrollador iOS en Latinoamérica, dominar SwiftUI no es opcional: **es la dirección hacia donde Apple empuja todo su ecosistema**. Las ofertas de trabajo remotas para empresas de Estados Unidos, Canadá y Europa —que representan las mejores oportunidades salariales para devs en LATAM— exigen cada vez más SwiftUI como requisito principal.

## Los Pilares Fundamentales de SwiftUI

### 1. Vistas como Estructuras (Views as Structs)

Todo en SwiftUI es un `struct` que conforma el protocolo `View`. Este es el concepto más importante que debes internalizar:

```swift
struct ProfileCard: View {
    let name: String
    let role: String
    let avatarURL: URL?

    var body: some View {
        HStack(spacing: 16) {
            AsyncImage(url: avatarURL) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Circle()
                    .fill(Color.gray.opacity(0.3))
                    .overlay {
                        ProgressView()
                    }
            }
            .frame(width: 60, height: 60)
            .clipShape(Circle())

            VStack(alignment: .leading, spacing: 4) {
                Text(name)
                    .font(.headline)
                    .foregroundStyle(.primary)

                Text(role)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}
```

**¿Por qué structs y no clases?** Las estructuras en Swift son tipos por valor. Esto significa que SwiftUI puede comparar eficientemente el estado anterior con el nuevo para determinar qué partes de la interfaz necesitan re-renderizarse. Es la base del sistema de *diffing* que hace a SwiftUI rápido.

### 2. El Sistema de Estado (State Management)

Este es donde el 80% de los desarrolladores cometen errores. SwiftUI ofrece múltiples property wrappers para manejar estado, y **elegir el correcto es crítico**:

```swift
// MARK: - @State: Estado local y privado de una vista
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Contador: \(count)")
                .font(.largeTitle)
                .fontWeight(.bold)

            HStack(spacing: 16) {
                Button("Decrementar") {
                    count -= 1
                }
                .buttonStyle(.bordered)

                Button("Incrementar") {
                    count += 1
                }
                .buttonStyle(.borderedProminent)
            }
        }
    }
}
```

```swift
// MARK: - @Binding: Referencia bidireccional al estado de otra vista
struct ToggleRow: View {
    let title: String
    @Binding var isOn: Bool

    var body: some View {
        Toggle(title, isOn: $isOn)
            .tint(.blue)
    }
}

struct SettingsView: View {
    @State private var notificationsEnabled = true
    @State private var darkModeEnabled = false

    var body: some View {
        Form {
            ToggleRow(title: "Notificaciones", isOn: $notificationsEnabled)
            ToggleRow(title: "Modo Oscuro", isOn: $darkModeEnabled)
        }
    }
}
```

```swift
// MARK: - @Observable (iOS 17+): El enfoque moderno para modelos de datos
@Observable
class TaskStore {
    var tasks: [TaskItem] = []
    var isLoading = false
    var errorMessage: String?

    func loadTasks() async {
        isLoading = true
        defer { isLoading = false }

        do {
            // Simula una llamada a API
            try await Task.sleep(for: .seconds(1))
            tasks = [
                TaskItem(title: "Revisar PR del equipo", isCompleted: false),
                TaskItem(title: "Actualizar dependencias", isCompleted: true),
                TaskItem(title: "Escribir unit tests", isCompleted: false)
            ]
        } catch {
            errorMessage = "Error al cargar tareas: \(error.localizedDescription)"
        }
    }

    func toggleCompletion(for task: TaskItem) {
        guard let index = tasks.firstIndex(where: { $0.id == task.id }) else { return }
        tasks[index].isCompleted.toggle()
    }
}

struct TaskItem: Identifiable {
    let id = UUID()
    let title: String
    var isCompleted: Bool
}
```

```swift
// MARK: - Vista que consume el @Observable
struct TaskListView: View {
    @State private var store = TaskStore()
    @State private var showCompletedOnly = false

    private var filteredTasks: [TaskItem] {
        if showCompletedOnly {
            return store.tasks.filter { $0.isCompleted }
        }
        return store.tasks
    }

    var body: some View {
        NavigationStack {
            Group {
                if store.isLoading {
                    ProgressView("Cargando tareas...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = store.errorMessage {
                    ContentUnavailableView {
                        Label("Error", systemImage: "exclamationmark.triangle")
                    } description: {
                        Text(error)
                    } actions: {
                        Button("Reintentar") {
                            Task { await store.loadTasks() }
                        }
                    }
                } else if filteredTasks.isEmpty {
                    ContentUnavailableView(
                        "Sin tareas",
                        systemImage: "checkmark.circle",
                        description: Text("No hay tareas que mostrar")
                    )
                } else {
                    List(filteredTasks) { task in
                        TaskRow(task: task) {
                            store.toggleCompletion(for: task)
                        }
                    }
                }
            }
            .navigationTitle("Mis Tareas")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Toggle(isOn: $showCompletedOnly) {
                        Label("Completadas", systemImage: "checkmark.circle.fill")
                    }
                }
            }
            .task {
                await store.loadTasks()
            }
        }
    }
}

struct TaskRow: View {
    let task: TaskItem
    let onToggle: () -> Void

    var body: some View {
        HStack {
            Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(task.isCompleted ? .green : .gray)
                .onTapGesture { onToggle() }

            Text(task.title)
                .strikethrough(task.isCompleted)
                .foregroundStyle(task.isCompleted ? .secondary : .primary)
        }
        .animation(.easeInOut(duration: 0.2), value: task.isCompleted)
    }
}
```

### Guía rápida para elegir el property wrapper correcto

| Escenario | Property Wrapper | Versión mínima |
|---|---|---|
| Estado local simple (Int, Bool, String) | `@State` | iOS 13+ |
| Pasar estado editable a vista hija | `@Binding` | iOS 13+ |
| Modelo de datos observable | `@Observable` + `@State` | iOS 17+ |
| Modelo observable (compatibilidad) | `@ObservedObject` / `@StateObject` | iOS 13+ |
| Datos compartidos en jerarquía | `@Environment` | iOS 13+ |
| Valores globales de la app | `@Environment` con custom keys | iOS 17+ |

### 3. Composición: El Superpoder de SwiftUI

La filosofía de SwiftUI es crear vistas pequeñas y componerlas. **No temas crear vistas con 5 líneas de código.** Esta mentalidad de composición es lo que diferencia a un desarrollador SwiftUI competente de uno avanzado:

```swift
// MARK: - Componentes atómicos reutilizables
struct BadgeView: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text)
            .font(.caption2)
            .fontWeight(.semibold)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(color.opacity(0.15), in: Capsule())
            .foregroundStyle(color)
    }
}

struct StarRating: View {
    let rating: Int
    let maxRating: Int

    init(rating: Int, maxRating: Int = 5) {
        self.rating = min(rating, maxRating)
        self.maxRating = maxRating
    }

    var body: some View {
        HStack(spacing: 2) {
            ForEach(1...maxRating, id: \.self) { index in
                Image(systemName: index <= rating ? "star.fill" : "star")
                    .foregroundStyle(index <= rating ? .yellow : .gray.opacity(0.3))
                    .font(.caption)
            }
        }
    }
}

struct PriceTag: View {
    let amount: Decimal
    let currency: String

    var body: some View {
        Text(amount, format: .currency(code: currency))
            .font(.title3)
            .fontWeight(.bold)
            .foregroundStyle(.primary)
    }
}

// MARK: - Composición de componentes
struct ProductCard: View {
    let product: Product

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Imagen del producto
            AsyncImage(url: product.imageURL) { phase in
                switch phase {
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                case .failure:
                    Image(systemName: "photo")
                        .font(.largeTitle)
                        .foregroundStyle(.tertiary)
                default:
                    ProgressView()
                }
            }
            .frame(height: 200)
            .frame(maxWidth: .infinity)
            .background(Color.gray.opacity(0.1))
            .clipShape(RoundedRectangle(cornerRadius: 12))

            // Información del producto
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    BadgeView(text: product.category, color: .blue)
                    if product.isNew {
                        BadgeView(text: "Nuevo", color: .green)
                    }
                }

                Text(product.name)
                    .font(.headline)
                    .lineLimit(2)

                StarRating(rating: product.rating)

                PriceTag(amount: product.price, currency: "MXN")
            }
            .padding(.horizontal, 4)
        }
        .padding(8)
        .background(.background, in: RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.05), radius: 8, y: 4)
    }
}

struct Product: Identifiable {
    let id = UUID()
    let name: String
    let category: String
    let price: Decimal
    let rating: Int
    let isNew: Bool
    let imageURL: URL?
}
```

### 4. Navegación Moderna con NavigationStack

A partir de iOS 16, Apple introdujo `NavigationStack` con navegación basada en datos. Este patrón es esencial para apps de producción:

```swift
// MARK: - Modelo de rutas de navegación
enum AppRoute: Hashable {
    case productDetail(Product)
    case categoryList(String)
    case cart
    case profile
    case settings
}

// MARK: - Coordinador de navegación
@Observable
class NavigationCoordinator {
    var path = NavigationPath()

    func goToProduct(_ product: Product) {
        path.append(AppRoute.productDetail(product))
    }

    func goToCategory(_ category: String) {
        path.append(AppRoute.categoryList(category))
    }

    func goToCart() {
        path.append(AppRoute.cart)
    }

    func goBack() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func goToRoot() {
        path.removeLast(path.count)
    }
}

// MARK: - Vista principal con navegación
struct MainStoreView: View {
    @State private var coordinator = NavigationCoordinator()
    @State private var searchText = ""

    var body: some View {
        NavigationStack(path: $coordinator.path) {
            ScrollView {
                LazyVStack(spacing: 16) {
                    // Sección de categorías
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(categories, id: \.self) { category in
                                Button(category) {
                                    coordinator.goToCategory(category)
                                }
                                .buttonStyle(.bordered)
                                .tint(.blue)
                            }
                        }
                        .padding(.horizontal)
                    }

                    // Grid de productos
                    LazyVGrid(
                        columns: [
                            GridItem(.flexible(), spacing: 12),
                            GridItem(.flexible(), spacing: 12)
                        ],
                        spacing: 12
                    ) {
                        ForEach(sampleProducts) { product in
                            ProductCard(product: product)
                                .onTapGesture {
                                    coordinator.goToProduct(product)
                                }
                        }
                    }
                    .padding(.horizontal)
                }
            }
            .navigationTitle("Tienda")
            .searchable(text: $searchText, prompt: "Buscar productos...")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        coordinator.goToCart()
                    } label: {
                        Image(systemName: "cart.fill")
                    }
                }
            }
            .navigationDestination(for: AppRoute.self) { route in
                switch route {
                case .productDetail(let product):
                    ProductDetailView(product: product)
                case .categoryList(let category):
                    CategoryView(category: category)
                case .cart:
                    CartView()
                case .profile:
                    ProfileView()
                case .settings:
                    SettingsDetailView()
                }
            }
        }
        .environment(coordinator)
    }

    private var categories: [String] {
        ["Electrónica", "Ropa", "Hogar", "Deportes", "Libros"]
    }

    private var sampleProducts: [Product] {
        [
            Product(