---
sidebar_position: 1
title: Uikit Basico
---

# UIKit Básico: La Base del Desarrollo iOS

## ¿Qué es UIKit?

UIKit es el **framework fundamental** que Apple proporciona para construir interfaces de usuario en aplicaciones iOS. Durante más de 15 años, ha sido la columna vertebral del desarrollo de apps para iPhone y iPad. Aunque SwiftUI ha ganado popularidad desde 2019, **la gran mayoría de aplicaciones en producción en Latinoamérica siguen utilizando UIKit**, y prácticamente todas las ofertas laborales en la región requieren conocimiento sólido de este framework.

UIKit te permite crear y gestionar:

- **Vistas y controles** (botones, etiquetas, campos de texto, tablas, etc.)
- **Navegación** entre pantallas
- **Gestión de eventos** táctiles y de usuario
- **Animaciones** e interacciones visuales
- **Auto Layout** para interfaces adaptables

## ¿Por qué es crucial para un desarrollador iOS en LATAM?

Si revisas portales de empleo como LinkedIn, Computrabajo, Get on Board o Torre.co en cualquier país de Latinoamérica, notarás un patrón claro:

1. **El 80-90% de las vacantes iOS piden UIKit** como requisito obligatorio.
2. **Los proyectos legacy dominan el mercado**: bancos, fintechs, apps de delivery y gobierno en México, Colombia, Argentina, Chile y Brasil mantienen bases de código en UIKit que necesitan mantenimiento y evolución constante.
3. **SwiftUI aún no reemplaza a UIKit**: muchas empresas necesitan soporte para versiones de iOS anteriores, y SwiftUI todavía no cubre todos los casos de uso que UIKit resuelve.
4. **Entender UIKit te hace mejor desarrollador SwiftUI**: los conceptos de ciclo de vida, responder chain, delegados y Auto Layout te dan una comprensión profunda de cómo funciona iOS por debajo.

> 💡 **Consejo profesional**: No caigas en la trampa de "solo aprender SwiftUI". En el mercado laboral latinoamericano, UIKit sigue siendo tu boleto de entrada más seguro.

## Arquitectura de UIKit: Los Componentes Clave

### El Ciclo de Vida de una Aplicación UIKit

Toda aplicación UIKit comienza con un `AppDelegate` y un `SceneDelegate` (desde iOS 13):

```swift
// AppDelegate.swift
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        // Configuración inicial de la app
        print("La aplicación se ha iniciado correctamente")
        return true
    }

    // MARK: - UISceneSession Lifecycle
    func application(
        _ application: UIApplication,
        configurationForConnecting connectingSceneSession: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        return UISceneConfiguration(
            name: "Default Configuration",
            sessionRole: connectingSceneSession.role
        )
    }
}
```

```swift
// SceneDelegate.swift
import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        // Crear la ventana principal programáticamente
        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = UINavigationController(
            rootViewController: HomeViewController()
        )
        window?.makeKeyAndVisible()
    }
}
```

### UIViewController: El Corazón de Cada Pantalla

Cada pantalla de tu app es un `UIViewController`. Este es el componente más importante que debes dominar:

```swift
import UIKit

class HomeViewController: UIViewController {

    // MARK: - UI Elements
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "Bienvenido a mi App"
        label.font = UIFont.systemFont(ofSize: 28, weight: .bold)
        label.textColor = .label
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let descriptionLabel: UILabel = {
        let label = UILabel()
        label.text = "Esta es una app construida con UIKit"
        label.font = UIFont.systemFont(ofSize: 16, weight: .regular)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let actionButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Comenzar", for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupActions()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Se llama cada vez que la vista está a punto de aparecer
        print("La vista va a aparecer")
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        // Se llama cuando la vista ya es visible
        print("La vista ya apareció")
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        // Se llama cuando la vista está a punto de desaparecer
        print("La vista va a desaparecer")
    }

    // MARK: - Setup
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Inicio"

        view.addSubview(titleLabel)
        view.addSubview(descriptionLabel)
        view.addSubview(actionButton)
    }

    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Title Label
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            titleLabel.centerYAnchor.constraint(
                equalTo: view.centerYAnchor,
                constant: -60
            ),
            titleLabel.leadingAnchor.constraint(
                equalTo: view.leadingAnchor,
                constant: 20
            ),
            titleLabel.trailingAnchor.constraint(
                equalTo: view.trailingAnchor,
                constant: -20
            ),

            // Description Label
            descriptionLabel.topAnchor.constraint(
                equalTo: titleLabel.bottomAnchor,
                constant: 12
            ),
            descriptionLabel.leadingAnchor.constraint(
                equalTo: view.leadingAnchor,
                constant: 40
            ),
            descriptionLabel.trailingAnchor.constraint(
                equalTo: view.trailingAnchor,
                constant: -40
            ),

            // Action Button
            actionButton.topAnchor.constraint(
                equalTo: descriptionLabel.bottomAnchor,
                constant: 32
            ),
            actionButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            actionButton.widthAnchor.constraint(equalToConstant: 200),
            actionButton.heightAnchor.constraint(equalToConstant: 50),
        ])
    }

    private func setupActions() {
        actionButton.addTarget(
            self,
            action: #selector(didTapActionButton),
            for: .touchUpInside
        )
    }

    // MARK: - Actions
    @objc private func didTapActionButton() {
        let detailVC = DetailViewController()
        navigationController?.pushViewController(detailVC, animated: true)
    }
}
```

### Ciclo de Vida del UIViewController — Diagrama

Comprender el orden de ejecución es **absolutamente crítico**:

```
viewDidLoad()          → Se llama UNA sola vez cuando se carga la vista
    ↓
viewWillAppear()       → Antes de que la vista sea visible
    ↓
viewDidAppear()        → La vista ya es visible en pantalla
    ↓
viewWillDisappear()    → Antes de que la vista deje de ser visible
    ↓
viewDidDisappear()     → La vista ya no es visible
```

## UITableView: El Componente Más Usado en iOS

Sin exagerar, `UITableView` es probablemente el componente que más usarás en tu carrera como desarrollador iOS. Listas de productos, feeds, configuraciones, menús... todo utiliza tablas.

```swift
import UIKit

class ProductListViewController: UIViewController {

    // MARK: - Data
    private var products: [String] = [
        "iPhone 15 Pro",
        "MacBook Air M2",
        "iPad Pro",
        "Apple Watch Ultra",
        "AirPods Pro"
    ]

    // MARK: - UI Elements
    private let tableView: UITableView = {
        let table = UITableView()
        table.register(
            UITableViewCell.self,
            forCellReuseIdentifier: "ProductCell"
        )
        table.translatesAutoresizingMaskIntoConstraints = false
        return table
    }()

    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }

    private func setupUI() {
        title = "Productos"
        view.backgroundColor = .systemBackground

        view.addSubview(tableView)
        tableView.delegate = self
        tableView.dataSource = self

        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.topAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
        ])
    }
}

// MARK: - UITableViewDataSource
extension ProductListViewController: UITableViewDataSource {

    func tableView(
        _ tableView: UITableView,
        numberOfRowsInSection section: Int
    ) -> Int {
        return products.count
    }

    func tableView(
        _ tableView: UITableView,
        cellForRowAt indexPath: IndexPath
    ) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(
            withIdentifier: "ProductCell",
            for: indexPath
        )

        var content = cell.defaultContentConfiguration()
        content.text = products[indexPath.row]
        content.image = UIImage(systemName: "bag.fill")
        cell.contentConfiguration = content
        cell.accessoryType = .disclosureIndicator

        return cell
    }
}

// MARK: - UITableViewDelegate
extension ProductListViewController: UITableViewDelegate {

    func tableView(
        _ tableView: UITableView,
        didSelectRowAt indexPath: IndexPath
    ) {
        tableView.deselectRow(at: indexPath, animated: true)
        let selectedProduct = products[indexPath.row]
        print("Seleccionaste: \(selectedProduct)")

        // Navegar a detalle
        let alert = UIAlertController(
            title: "Producto",
            message: "Seleccionaste \(selectedProduct)",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    func tableView(
        _ tableView: UITableView,
        heightForRowAt indexPath: IndexPath
    ) -> CGFloat {
        return 60
    }
}
```

## Patrones Fundamentales en UIKit

### 1. Delegation (Delegación)

Es el patrón más utilizado en UIKit. Lo viste con `UITableViewDelegate` y `UITableViewDataSource`. La idea es simple: **un objeto delega responsabilidades a otro**.

```swift
// Definir un protocolo (contrato)
protocol LoginViewControllerDelegate: AnyObject {
    func didLoginSuccessfully(username: String)
    func didFailLogin(error: String)
}

class LoginViewController: UIViewController {

    weak var delegate: LoginViewControllerDelegate?

    private func performLogin() {
        let username = "usuario_latam"
        let success = true

        if success {
            delegate?.didLoginSuccessfully(username: username)
        } else {
            delegate?.didFailLogin(error: "Credenciales inválidas")
        }
    }
}

// El que recibe la delegación
class MainCoordinator: LoginViewControllerDelegate {

    func didLoginSuccessfully(username: String) {
        print("Bienvenido \(username), redirigiendo al home...")
    }

    func didFailLogin(error: String) {
        print("Error: \(error)")
    }
}
```

### 2. Target-Action

Es el patrón que usas con botones y controles:

```swift
// Ya lo vimos antes con el botón
actionButton.addTarget(
    self,                          // target: quién responde
    action: #selector(didTapButton), // action: qué método ejecutar
    for: .touchUpInside            // evento: cuándo ejecutar
)

@objc func didTapButton() {
    print("¡Botón presionado!")
}
```

### 3. MVC (Model-View-Controller)

UIKit fue diseñado con el patrón **MVC** en mente:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Model     │◄────│   Controller     │────►│    View      │
│             │     │ (UIViewController)│     │  (UIView)   │
│ Datos y     │     │                  │     │             │
│ lógica de   │────►│ Coordina Model   │◄────│ Muestra     │
│ negocio     │     │ y View           │     │ información │
└─────────────┘     └──────────────────┘     └─────────────┘
```

```swift
// Model
struct Product {
    let id: Int
    let name: String
    let price: Double
    let currency: String

    var formattedPrice: String {
        return "\(currency) \(String(format: "%.2f", price))"
    }
}

// Controller usa el Model para alimentar la View
class ProductDetailViewController: UIViewController {

    // El modelo
    private let product: Product

    // Las vistas
    private let nameLabel = UILabel()
    private let priceLabel = UILabel()

    // Inyección de dependencias vía inicializador
    init(product: Product) {
        self.product = product
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        configureView()
    }

    private func configureView() {
        nameLabel.text = product.name
        priceLabel.text = product.formattedPrice
    }