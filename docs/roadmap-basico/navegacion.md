---
sidebar_position: 1
title: Navegacion
---

# Navegación en iOS

## ¿Qué es la navegación en iOS?

La **navegación** es el sistema que permite a los usuarios moverse entre las diferentes pantallas (vistas) de tu aplicación. Es el esqueleto de la experiencia de usuario: sin una navegación clara y bien implementada, tu app se convierte en un laberinto frustrante.

Piensa en la navegación como el mapa de una ciudad. No importa qué tan bonitos sean los edificios (tus vistas) si las calles (la navegación) no tienen sentido. En iOS, Apple nos ofrece varios patrones y herramientas para construir estas "calles" de manera intuitiva.

## ¿Por qué es fundamental para un dev iOS en LATAM?

En el mercado latinoamericano, las apps más exitosas —desde apps de delivery como Rappi o PedidosYa, hasta fintech como Mercado Pago o Nu— comparten algo en común: **una navegación impecable**. Los usuarios en LATAM frecuentemente acceden desde dispositivos con pantallas variadas y conexiones inestables, lo que hace que una navegación rápida, predecible y clara sea aún más crítica.

Si buscas posicionarte como desarrollador iOS competitivo en la región, dominar la navegación no es opcional. Es lo primero que evalúan en entrevistas técnicas y lo primero que nota un usuario al abrir tu app.

## Patrones principales de navegación

### 1. Navegación jerárquica (NavigationStack)

Es el patrón más común. Funciona como una pila: empujas pantallas hacia adelante y retrocedes con el botón "Atrás".

**Ejemplo clásico:** La app de Configuración de tu iPhone.

### 2. Navegación plana (TabView)

Permite saltar entre secciones independientes al mismo nivel. Cada pestaña representa un flujo separado.

**Ejemplo clásico:** Instagram, WhatsApp, Mercado Libre.

### 3. Navegación modal

Presenta contenido de forma temporal que interrumpe el flujo principal. Ideal para formularios, alertas o tareas que requieren atención inmediata.

**Ejemplo clásico:** Componer un nuevo correo en Mail.

## Implementación práctica con SwiftUI

### NavigationStack (iOS 16+)

El `NavigationStack` es la forma moderna de manejar navegación jerárquica en SwiftUI. Reemplaza al antiguo `NavigationView`.

```swift
import SwiftUI

struct ProductListView: View {
    let products = ["iPhone 15", "MacBook Pro", "iPad Air", "AirPods Pro"]
    
    var body: some View {
        NavigationStack {
            List(products, id: \.self) { product in
                NavigationLink(value: product) {
                    HStack {
                        Image(systemName: "bag.fill")
                            .foregroundColor(.blue)
                        Text(product)
                            .font(.body)
                    }
                }
            }
            .navigationTitle("Productos")
            .navigationDestination(for: String.self) { product in
                ProductDetailView(productName: product)
            }
        }
    }
}

struct ProductDetailView: View {
    let productName: String
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "shippingbox.fill")
                .font(.system(size: 80))
                .foregroundColor(.orange)
            
            Text(productName)
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("Disponible para envío en toda Latinoamérica")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Button("Agregar al carrito") {
                // Acción de compra
            }
            .buttonStyle(.borderedProminent)
        }
        .navigationTitle(productName)
        .navigationBarTitleDisplayMode(.inline)
    }
}
```

### TabView: Navegación por pestañas

```swift
struct MainTabView: View {
    var body: some View {
        TabView {
            Tab("Inicio", systemImage: "house.fill") {
                NavigationStack {
                    HomeView()
                }
            }
            
            Tab("Buscar", systemImage: "magnifyingglass") {
                NavigationStack {
                    SearchView()
                }
            }
            
            Tab("Carrito", systemImage: "cart.fill") {
                NavigationStack {
                    CartView()
                }
            }
            
            Tab("Perfil", systemImage: "person.fill") {
                NavigationStack {
                    ProfileView()
                }
            }
        }
    }
}

struct HomeView: View {
    var body: some View {
        Text("Bienvenido a la tienda")
            .navigationTitle("Inicio")
    }
}

struct SearchView: View {
    var body: some View {
        Text("Busca productos")
            .navigationTitle("Buscar")
    }
}

struct CartView: View {
    var body: some View {
        Text("Tu carrito está vacío")
            .navigationTitle("Carrito")
    }
}

struct ProfileView: View {
    var body: some View {
        Text("Mi cuenta")
            .navigationTitle("Perfil")
    }
}
```

### Navegación modal con sheets

```swift
struct OrderListView: View {
    @State private var showingNewOrder = false
    @State private var showingConfirmation = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Tus pedidos aparecerán aquí")
                    .foregroundColor(.secondary)
                
                Button("Nuevo pedido") {
                    showingNewOrder = true
                }
                .buttonStyle(.borderedProminent)
            }
            .navigationTitle("Mis Pedidos")
            .sheet(isPresented: $showingNewOrder) {
                NewOrderView(showConfirmation: $showingConfirmation)
            }
            .alert("¡Pedido confirmado!", isPresented: $showingConfirmation) {
                Button("OK", role: .cancel) { }
            } message: {
                Text("Tu pedido ha sido registrado exitosamente.")
            }
        }
    }
}

struct NewOrderView: View {
    @Environment(\.dismiss) private var dismiss
    @Binding var showConfirmation: Bool
    
    @State private var productName = ""
    @State private var quantity = 1
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Datos del pedido") {
                    TextField("Nombre del producto", text: $productName)
                    Stepper("Cantidad: \(quantity)", value: $quantity, in: 1...99)
                }
                
                Section("Envío") {
                    Text("Envío estándar - 3 a 5 días hábiles")
                    Text("Cobertura: México, Colombia, Argentina, Chile")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Nuevo Pedido")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancelar") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Confirmar") {
                        dismiss()
                        showConfirmation = true
                    }
                    .disabled(productName.isEmpty)
                }
            }
        }
    }
}
```

### Navegación programática avanzada con NavigationPath

Para aplicaciones más complejas, necesitas controlar la pila de navegación de forma programática. Esto es esencial en apps del mundo real donde las notificaciones push o los deep links deben llevar al usuario a pantallas específicas.

```swift
// Definimos los destinos posibles de navegación
enum AppDestination: Hashable {
    case category(String)
    case product(Product)
    case checkout
}

struct Product: Hashable, Identifiable {
    let id = UUID()
    let name: String
    let price: Double
    let category: String
}

class NavigationRouter: ObservableObject {
    @Published var path = NavigationPath()
    
    func navigateToProduct(_ product: Product) {
        path.append(AppDestination.product(product))
    }
    
    func navigateToCheckout() {
        path.append(AppDestination.checkout)
    }
    
    func goToRoot() {
        path = NavigationPath()
    }
    
    func goBack() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }
    
    // Útil para deep links desde notificaciones push
    func handleDeepLink(to destination: AppDestination) {
        path = NavigationPath()
        path.append(destination)
    }
}

struct StoreView: View {
    @StateObject private var router = NavigationRouter()
    
    let categories = ["Electrónica", "Ropa", "Hogar", "Deportes"]
    
    var body: some View {
        NavigationStack(path: $router.path) {
            List(categories, id: \.self) { category in
                NavigationLink(value: AppDestination.category(category)) {
                    Label(category, systemImage: "folder.fill")
                }
            }
            .navigationTitle("Tienda")
            .navigationDestination(for: AppDestination.self) { destination in
                switch destination {
                case .category(let name):
                    CategoryView(categoryName: name, router: router)
                case .product(let product):
                    StoreProductDetailView(product: product, router: router)
                case .checkout:
                    CheckoutView(router: router)
                }
            }
        }
        .environmentObject(router)
    }
}

struct CategoryView: View {
    let categoryName: String
    let router: NavigationRouter
    
    var sampleProducts: [Product] {
        [
            Product(name: "Producto A", price: 299.99, category: categoryName),
            Product(name: "Producto B", price: 549.50, category: categoryName),
            Product(name: "Producto C", price: 1299.00, category: categoryName)
        ]
    }
    
    var body: some View {
        List(sampleProducts) { product in
            Button {
                router.navigateToProduct(product)
            } label: {
                HStack {
                    VStack(alignment: .leading) {
                        Text(product.name)
                            .font(.headline)
                        Text("$\(product.price, specifier: "%.2f") MXN")
                            .font(.subheadline)
                            .foregroundColor(.green)
                    }
                    Spacer()
                    Image(systemName: "chevron.right")
                        .foregroundColor(.secondary)
                }
            }
            .foregroundColor(.primary)
        }
        .navigationTitle(categoryName)
    }
}

struct StoreProductDetailView: View {
    let product: Product
    let router: NavigationRouter
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "shippingbox.fill")
                .font(.system(size: 100))
                .foregroundColor(.blue)
            
            Text(product.name)
                .font(.title)
                .fontWeight(.bold)
            
            Text("$\(product.price, specifier: "%.2f") MXN")
                .font(.title2)
                .foregroundColor(.green)
            
            Button("Comprar ahora") {
                router.navigateToCheckout()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .navigationTitle(product.name)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct CheckoutView: View {
    let router: NavigationRouter
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 80))
                .foregroundColor(.green)
            
            Text("Proceso de pago")
                .font(.title)
            
            Text("Aquí iría la integración con pasarelas de pago como Mercado Pago, Stripe, etc.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            Button("Volver al inicio") {
                router.goToRoot()
            }
            .buttonStyle(.bordered)
        }
        .navigationTitle("Checkout")
        .navigationBarTitleDisplayMode(.inline)
    }
}
```

## Navegación con UIKit (UINavigationController)

Aunque SwiftUI es el presente y futuro, **la realidad del mercado laboral en LATAM** es que muchas empresas mantienen bases de código en UIKit. Es indispensable conocer `UINavigationController`.

```swift
import UIKit

// MARK: - Lista de productos
class ProductsViewController: UITableViewController {
    
    let products = [
        ("iPhone 15", 22999.0),
        ("MacBook Air", 28999.0),
        ("iPad Pro", 19999.0)
    ]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Productos"
        navigationController?.navigationBar.prefersLargeTitles = true
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "ProductCell")
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        products.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ProductCell", for: indexPath)
        var config = cell.defaultContentConfiguration()
        let product = products[indexPath.row]
        config.text = product.0
        config.secondaryText = "$\(product.1) MXN"
        cell.contentConfiguration = config
        cell.accessoryType = .disclosureIndicator
        return cell
    }
    
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let product = products[indexPath.row]
        let detailVC = ProductDetailViewController(
            productName: product.0,
            price: product.1
        )
        // Push: navegación jerárquica
        navigationController?.pushViewController(detailVC, animated: true)
    }
}

// MARK: - Detalle del producto
class ProductDetailViewController: UIViewController {
    
    private let productName: String
    private let price: Double
    
    init(productName: String, price: Double) {
        self.productName = productName
        self.price = price
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        title = productName
        navigationItem.largeTitleDisplayMode = .never
        
        setupUI()
    }
    
    private func setupUI() {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.alignment = .center
        stackView.translatesAutoresizingMaskIntoConstraints = false
        
        let imageView = UIImageView(image: UIImage(systemName: "bag.fill"))
        imageView.tintColor = .systemBlue
        imageView.contentMode = .scaleAsp